import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:hive/hive.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';

import '../app_config.dart';

enum SyncStatus {
  idle,
  syncing,
  completed,
  failed,
  paused,
}

enum ContentPriority {
  low,
  medium,
  high,
  critical,
}

class OfflineContent {
  final String id;
  final String type;
  final String title;
  final Map<String, dynamic> data;
  final List<String> downloadUrls;
  final int sizeBytes;
  final ContentPriority priority;
  final DateTime createdAt;
  final DateTime? expiresAt;
  final bool isDownloaded;
  final double downloadProgress;

  OfflineContent({
    required this.id,
    required this.type,
    required this.title,
    required this.data,
    required this.downloadUrls,
    required this.sizeBytes,
    this.priority = ContentPriority.medium,
    required this.createdAt,
    this.expiresAt,
    this.isDownloaded = false,
    this.downloadProgress = 0.0,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type,
    'title': title,
    'data': data,
    'downloadUrls': downloadUrls,
    'sizeBytes': sizeBytes,
    'priority': priority.index,
    'createdAt': createdAt.toIso8601String(),
    'expiresAt': expiresAt?.toIso8601String(),
    'isDownloaded': isDownloaded,
    'downloadProgress': downloadProgress,
  };

  factory OfflineContent.fromJson(Map<String, dynamic> json) => OfflineContent(
    id: json['id'],
    type: json['type'],
    title: json['title'],
    data: json['data'],
    downloadUrls: List<String>.from(json['downloadUrls']),
    sizeBytes: json['sizeBytes'],
    priority: ContentPriority.values[json['priority']],
    createdAt: DateTime.parse(json['createdAt']),
    expiresAt: json['expiresAt'] != null ? DateTime.parse(json['expiresAt']) : null,
    isDownloaded: json['isDownloaded'],
    downloadProgress: json['downloadProgress'],
  );
}

class SyncOperation {
  final String id;
  final String type;
  final String method;
  final String endpoint;
  final Map<String, dynamic> data;
  final DateTime createdAt;
  final int retryCount;
  final ContentPriority priority;

  SyncOperation({
    required this.id,
    required this.type,
    required this.method,
    required this.endpoint,
    required this.data,
    required this.createdAt,
    this.retryCount = 0,
    this.priority = ContentPriority.medium,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type,
    'method': method,
    'endpoint': endpoint,
    'data': data,
    'createdAt': createdAt.toIso8601String(),
    'retryCount': retryCount,
    'priority': priority.index,
  };

  factory SyncOperation.fromJson(Map<String, dynamic> json) => SyncOperation(
    id: json['id'],
    type: json['type'],
    method: json['method'],
    endpoint: json['endpoint'],
    data: json['data'],
    createdAt: DateTime.parse(json['createdAt']),
    retryCount: json['retryCount'],
    priority: ContentPriority.values[json['priority']],
  );
}

class OfflineSyncService {
  static final OfflineSyncService _instance = OfflineSyncService._internal();
  factory OfflineSyncService() => _instance;
  OfflineSyncService._internal();

  late Box<String> _offlineContentBox;
  late Box<String> _syncOperationsBox;
  late Box<String> _userDataBox;
  late Dio _dio;
  
  final StreamController<SyncStatus> _syncStatusController = StreamController<SyncStatus>.broadcast();
  final StreamController<double> _syncProgressController = StreamController<double>.broadcast();
  final StreamController<String> _syncMessageController = StreamController<String>.broadcast();
  
  SyncStatus _currentStatus = SyncStatus.idle;
  Timer? _syncTimer;
  Timer? _cleanupTimer;
  
  // Connectivity monitoring
  late StreamSubscription<ConnectivityResult> _connectivitySubscription;
  bool _isOnline = false;
  
  // Download management
  final Map<String, CancelToken> _activeDownloads = {};
  final Map<String, double> _downloadProgress = {};
  
  // Bandwidth monitoring
  int _currentBandwidth = 0;
  bool _isLowBandwidth = false;
  
  Stream<SyncStatus> get syncStatus => _syncStatusController.stream;
  Stream<double> get syncProgress => _syncProgressController.stream;
  Stream<String> get syncMessage => _syncMessageController.stream;
  
  bool get isOnline => _isOnline;
  bool get isLowBandwidth => _isLowBandwidth;
  SyncStatus get currentStatus => _currentStatus;

  Future<void> initialize() async {
    try {
      // Initialize Hive boxes
      _offlineContentBox = await Hive.openBox<String>('offline_content');
      _syncOperationsBox = await Hive.openBox<String>('sync_operations');
      _userDataBox = await Hive.openBox<String>('user_data');
      
      // Initialize Dio with offline-friendly configuration
      _dio = Dio(BaseOptions(
        baseUrl: AppConfig.apiBaseUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 60),
        sendTimeout: const Duration(seconds: 60),
      ));
      
      // Add interceptors for offline handling
      _dio.interceptors.add(_OfflineInterceptor(this));
      _dio.interceptors.add(_BandwidthMonitorInterceptor(this));
      
      // Monitor connectivity
      await _initializeConnectivityMonitoring();
      
      // Start periodic sync
      _startPeriodicSync();
      
      // Start cleanup timer
      _startCleanupTimer();
      
      // Perform initial sync if online
      if (_isOnline) {
        unawaited(_performSync());
      }
      
      debugPrint('OfflineSyncService initialized successfully');
    } catch (e) {
      debugPrint('Failed to initialize OfflineSyncService: $e');
    }
  }

  Future<void> _initializeConnectivityMonitoring() async {
    // Check initial connectivity
    final connectivityResult = await Connectivity().checkConnectivity();
    _isOnline = connectivityResult != ConnectivityResult.none;
    
    // Monitor connectivity changes
    _connectivitySubscription = Connectivity().onConnectivityChanged.listen(
      (ConnectivityResult result) async {
        final wasOnline = _isOnline;
        _isOnline = result != ConnectivityResult.none;
        
        if (!wasOnline && _isOnline) {
          // Just came online - start sync
          debugPrint('Device came online - starting sync');
          await _performSync();
        } else if (wasOnline && !_isOnline) {
          // Just went offline
          debugPrint('Device went offline');
          _updateSyncStatus(SyncStatus.paused);
        }
        
        // Update bandwidth estimation
        await _updateBandwidthEstimation(result);
      },
    );
  }

  Future<void> _updateBandwidthEstimation(ConnectivityResult result) async {
    // Estimate bandwidth based on connection type
    switch (result) {
      case ConnectivityResult.wifi:
        _currentBandwidth = 10000; // 10 Mbps
        _isLowBandwidth = false;
        break;
      case ConnectivityResult.mobile:
        _currentBandwidth = 2000; // 2 Mbps
        _isLowBandwidth = true;
        break;
      case ConnectivityResult.ethernet:
        _currentBandwidth = 50000; // 50 Mbps
        _isLowBandwidth = false;
        break;
      default:
        _currentBandwidth = 0;
        _isLowBandwidth = true;
    }
    
    // Perform actual bandwidth test periodically
    if (_isOnline) {
      unawaited(_performBandwidthTest());
    }
  }

  Future<void> _performBandwidthTest() async {
    try {
      final stopwatch = Stopwatch()..start();
      
      // Download a small test file to measure bandwidth
      final response = await _dio.get(
        '/api/v1/system/bandwidth-test',
        options: Options(
          responseType: ResponseType.bytes,
        ),
      );
      
      stopwatch.stop();
      
      if (response.statusCode == 200) {
        final bytes = response.data.length;
        final seconds = stopwatch.elapsedMilliseconds / 1000.0;
        final bitsPerSecond = (bytes * 8) / seconds;
        final kbps = bitsPerSecond / 1000;
        
        _currentBandwidth = kbps.round();
        _isLowBandwidth = _currentBandwidth < AppConfig.liteModeThrsholdKbps;
        
        debugPrint('Bandwidth test: ${_currentBandwidth} kbps');
      }
    } catch (e) {
      debugPrint('Bandwidth test failed: $e');
    }
  }

  void _startPeriodicSync() {
    _syncTimer = Timer.periodic(
      Duration(seconds: AppConfig.backgroundSyncInterval),
      (_) async {
        if (_isOnline && _currentStatus == SyncStatus.idle) {
          await _performSync();
        }
      },
    );
  }

  void _startCleanupTimer() {
    _cleanupTimer = Timer.periodic(
      const Duration(hours: 1),
      (_) async {
        await _cleanupExpiredContent();
      },
    );
  }

  Future<void> _performSync() async {
    if (_currentStatus == SyncStatus.syncing) return;
    
    _updateSyncStatus(SyncStatus.syncing);
    _updateSyncMessage('Starting sync...');
    
    try {
      // Sync pending operations first
      await _syncPendingOperations();
      
      // Download queued content
      await _downloadQueuedContent();
      
      // Sync user data
      await _syncUserData();
      
      _updateSyncStatus(SyncStatus.completed);
      _updateSyncMessage('Sync completed successfully');
      
    } catch (e) {
      debugPrint('Sync failed: $e');
      _updateSyncStatus(SyncStatus.failed);
      _updateSyncMessage('Sync failed: ${e.toString()}');
    }
  }

  Future<void> _syncPendingOperations() async {
    final operations = await _getPendingOperations();
    
    if (operations.isEmpty) return;
    
    _updateSyncMessage('Syncing ${operations.length} pending operations...');
    
    // Sort by priority and creation time
    operations.sort((a, b) {
      final priorityComparison = b.priority.index.compareTo(a.priority.index);
      if (priorityComparison != 0) return priorityComparison;
      return a.createdAt.compareTo(b.createdAt);
    });
    
    for (int i = 0; i < operations.length; i++) {
      final operation = operations[i];
      
      try {
        await _executeSyncOperation(operation);
        await _removeSyncOperation(operation.id);
        
        _updateSyncProgress((i + 1) / operations.length);
        
      } catch (e) {
        debugPrint('Failed to sync operation ${operation.id}: $e');
        
        // Increment retry count
        final updatedOperation = SyncOperation(
          id: operation.id,
          type: operation.type,
          method: operation.method,
          endpoint: operation.endpoint,
          data: operation.data,
          createdAt: operation.createdAt,
          retryCount: operation.retryCount + 1,
          priority: operation.priority,
        );
        
        // Remove if max retries reached
        if (updatedOperation.retryCount >= 3) {
          await _removeSyncOperation(operation.id);
        } else {
          await _updateSyncOperation(updatedOperation);
        }
      }
    }
  }

  Future<void> _downloadQueuedContent() async {
    final queuedContent = await _getQueuedContent();
    
    if (queuedContent.isEmpty) return;
    
    _updateSyncMessage('Downloading ${queuedContent.length} items...');
    
    // Filter based on bandwidth and user preferences
    final filteredContent = _filterContentForBandwidth(queuedContent);
    
    for (int i = 0; i < filteredContent.length; i++) {
      final content = filteredContent[i];
      
      try {
        await _downloadContent(content);
        _updateSyncProgress((i + 1) / filteredContent.length);
        
      } catch (e) {
        debugPrint('Failed to download content ${content.id}: $e');
      }
    }
  }

  List<OfflineContent> _filterContentForBandwidth(List<OfflineContent> content) {
    if (!_isLowBandwidth) return content;
    
    // On low bandwidth, prioritize smaller, high-priority content
    return content.where((item) {
      // Skip large files on low bandwidth
      if (item.sizeBytes > 50 * 1024 * 1024) return false; // 50MB limit
      
      // Prioritize high-priority content
      return item.priority == ContentPriority.high || 
             item.priority == ContentPriority.critical;
    }).toList();
  }

  Future<void> _downloadContent(OfflineContent content) async {
    final cancelToken = CancelToken();
    _activeDownloads[content.id] = cancelToken;
    
    try {
      final directory = await getApplicationDocumentsDirectory();
      final contentDir = Directory('${directory.path}/offline_content/${content.type}');
      await contentDir.create(recursive: true);
      
      for (final url in content.downloadUrls) {
        final fileName = url.split('/').last;
        final filePath = '${contentDir.path}/$fileName';
        
        await _dio.download(
          url,
          filePath,
          cancelToken: cancelToken,
          onReceiveProgress: (received, total) {
            if (total != -1) {
              final progress = received / total;
              _downloadProgress[content.id] = progress;
              
              // Update content progress
              final updatedContent = OfflineContent(
                id: content.id,
                type: content.type,
                title: content.title,
                data: content.data,
                downloadUrls: content.downloadUrls,
                sizeBytes: content.sizeBytes,
                priority: content.priority,
                createdAt: content.createdAt,
                expiresAt: content.expiresAt,
                isDownloaded: progress >= 1.0,
                downloadProgress: progress,
              );
              
              unawaited(_updateOfflineContent(updatedContent));
            }
          },
        );
      }
      
      // Mark as downloaded
      final downloadedContent = OfflineContent(
        id: content.id,
        type: content.type,
        title: content.title,
        data: content.data,
        downloadUrls: content.downloadUrls,
        sizeBytes: content.sizeBytes,
        priority: content.priority,
        createdAt: content.createdAt,
        expiresAt: content.expiresAt,
        isDownloaded: true,
        downloadProgress: 1.0,
      );
      
      await _updateOfflineContent(downloadedContent);
      
    } finally {
      _activeDownloads.remove(content.id);
      _downloadProgress.remove(content.id);
    }
  }

  Future<void> _syncUserData() async {
    try {
      // Get local user data changes
      final localChanges = await _getLocalUserDataChanges();
      
      if (localChanges.isNotEmpty) {
        _updateSyncMessage('Syncing user data...');
        
        // Upload local changes
        for (final change in localChanges) {
          await _uploadUserDataChange(change);
        }
      }
      
      // Download remote user data updates
      final lastSyncTime = await _getLastUserDataSyncTime();
      final remoteUpdates = await _fetchRemoteUserDataUpdates(lastSyncTime);
      
      if (remoteUpdates.isNotEmpty) {
        await _applyRemoteUserDataUpdates(remoteUpdates);
      }
      
      // Update last sync time
      await _updateLastUserDataSyncTime(DateTime.now());
      
    } catch (e) {
      debugPrint('User data sync failed: $e');
      rethrow;
    }
  }

  // Public API methods
  Future<void> queueContentForDownload(OfflineContent content) async {
    await _saveOfflineContent(content);
    
    // Start download immediately if online and not low bandwidth
    if (_isOnline && !_isLowBandwidth) {
      unawaited(_downloadContent(content));
    }
  }

  Future<void> queueSyncOperation(SyncOperation operation) async {
    await _saveSyncOperation(operation);
    
    // Execute immediately if online
    if (_isOnline) {
      try {
        await _executeSyncOperation(operation);
        await _removeSyncOperation(operation.id);
      } catch (e) {
        debugPrint('Immediate sync operation failed: $e');
        // Will be retried in next sync cycle
      }
    }
  }

  Future<OfflineContent?> getOfflineContent(String contentId) async {
    final contentJson = _offlineContentBox.get(contentId);
    if (contentJson == null) return null;
    
    final contentData = jsonDecode(contentJson);
    return OfflineContent.fromJson(contentData);
  }

  Future<List<OfflineContent>> getAllOfflineContent() async {
    final contentList = <OfflineContent>[];
    
    for (final key in _offlineContentBox.keys) {
      final contentJson = _offlineContentBox.get(key);
      if (contentJson != null) {
        final contentData = jsonDecode(contentJson);
        contentList.add(OfflineContent.fromJson(contentData));
      }
    }
    
    return contentList;
  }

  Future<void> removeOfflineContent(String contentId) async {
    // Remove from storage
    await _offlineContentBox.delete(contentId);
    
    // Delete downloaded files
    try {
      final directory = await getApplicationDocumentsDirectory();
      final contentDir = Directory('${directory.path}/offline_content');
      
      if (await contentDir.exists()) {
        await for (final entity in contentDir.list(recursive: true)) {
          if (entity.path.contains(contentId)) {
            await entity.delete();
          }
        }
      }
    } catch (e) {
      debugPrint('Failed to delete offline content files: $e');
    }
  }

  Future<void> pauseSync() async {
    _updateSyncStatus(SyncStatus.paused);
    
    // Cancel active downloads
    for (final cancelToken in _activeDownloads.values) {
      cancelToken.cancel('Sync paused by user');
    }
    _activeDownloads.clear();
  }

  Future<void> resumeSync() async {
    if (_isOnline) {
      await _performSync();
    } else {
      _updateSyncStatus(SyncStatus.idle);
    }
  }

  Future<void> forcSync() async {
    if (!_isOnline) {
      throw Exception('Cannot force sync while offline');
    }
    
    await _performSync();
  }

  Future<Map<String, dynamic>> getSyncStatistics() async {
    final offlineContent = await getAllOfflineContent();
    final pendingOperations = await _getPendingOperations();
    
    final downloadedContent = offlineContent.where((c) => c.isDownloaded).length;
    final totalSize = offlineContent.fold<int>(0, (sum, c) => sum + c.sizeBytes);
    final downloadedSize = offlineContent
        .where((c) => c.isDownloaded)
        .fold<int>(0, (sum, c) => sum + c.sizeBytes);
    
    return {
      'total_content': offlineContent.length,
      'downloaded_content': downloadedContent,
      'pending_operations': pendingOperations.length,
      'total_size_mb': (totalSize / (1024 * 1024)).round(),
      'downloaded_size_mb': (downloadedSize / (1024 * 1024)).round(),
      'is_online': _isOnline,
      'bandwidth_kbps': _currentBandwidth,
      'is_low_bandwidth': _isLowBandwidth,
      'sync_status': _currentStatus.toString(),
    };
  }

  // Private helper methods
  Future<void> _saveOfflineContent(OfflineContent content) async {
    final contentJson = jsonEncode(content.toJson());
    await _offlineContentBox.put(content.id, contentJson);
  }

  Future<void> _updateOfflineContent(OfflineContent content) async {
    await _saveOfflineContent(content);
  }

  Future<void> _saveSyncOperation(SyncOperation operation) async {
    final operationJson = jsonEncode(operation.toJson());
    await _syncOperationsBox.put(operation.id, operationJson);
  }

  Future<void> _updateSyncOperation(SyncOperation operation) async {
    await _saveSyncOperation(operation);
  }

  Future<void> _removeSyncOperation(String operationId) async {
    await _syncOperationsBox.delete(operationId);
  }

  Future<List<SyncOperation>> _getPendingOperations() async {
    final operations = <SyncOperation>[];
    
    for (final key in _syncOperationsBox.keys) {
      final operationJson = _syncOperationsBox.get(key);
      if (operationJson != null) {
        final operationData = jsonDecode(operationJson);
        operations.add(SyncOperation.fromJson(operationData));
      }
    }
    
    return operations;
  }

  Future<List<OfflineContent>> _getQueuedContent() async {
    final allContent = await getAllOfflineContent();
    return allContent.where((content) => !content.isDownloaded).toList();
  }

  Future<void> _executeSyncOperation(SyncOperation operation) async {
    final options = Options(method: operation.method);
    
    Response response;
    
    switch (operation.method.toUpperCase()) {
      case 'GET':
        response = await _dio.get(operation.endpoint, options: options);
        break;
      case 'POST':
        response = await _dio.post(
          operation.endpoint,
          data: operation.data,
          options: options,
        );
        break;
      case 'PUT':
        response = await _dio.put(
          operation.endpoint,
          data: operation.data,
          options: options,
        );
        break;
      case 'DELETE':
        response = await _dio.delete(operation.endpoint, options: options);
        break;
      default:
        throw Exception('Unsupported HTTP method: ${operation.method}');
    }
    
    if (response.statusCode! < 200 || response.statusCode! >= 300) {
      throw Exception('HTTP ${response.statusCode}: ${response.statusMessage}');
    }
  }

  Future<void> _cleanupExpiredContent() async {
    final allContent = await getAllOfflineContent();
    final now = DateTime.now();
    
    for (final content in allContent) {
      if (content.expiresAt != null && content.expiresAt!.isBefore(now)) {
        await removeOfflineContent(content.id);
        debugPrint('Removed expired content: ${content.id}');
      }
    }
  }

  Future<List<Map<String, dynamic>>> _getLocalUserDataChanges() async {
    // Implementation for getting local user data changes
    return [];
  }

  Future<void> _uploadUserDataChange(Map<String, dynamic> change) async {
    // Implementation for uploading user data changes
  }

  Future<DateTime?> _getLastUserDataSyncTime() async {
    final timeString = _userDataBox.get('last_sync_time');
    return timeString != null ? DateTime.parse(timeString) : null;
  }

  Future<List<Map<String, dynamic>>> _fetchRemoteUserDataUpdates(DateTime? since) async {
    // Implementation for fetching remote user data updates
    return [];
  }

  Future<void> _applyRemoteUserDataUpdates(List<Map<String, dynamic>> updates) async {
    // Implementation for applying remote user data updates
  }

  Future<void> _updateLastUserDataSyncTime(DateTime time) async {
    await _userDataBox.put('last_sync_time', time.toIso8601String());
  }

  void _updateSyncStatus(SyncStatus status) {
    _currentStatus = status;
    _syncStatusController.add(status);
  }

  void _updateSyncProgress(double progress) {
    _syncProgressController.add(progress);
  }

  void _updateSyncMessage(String message) {
    _syncMessageController.add(message);
  }

  void dispose() {
    _syncTimer?.cancel();
    _cleanupTimer?.cancel();
    _connectivitySubscription.cancel();
    _syncStatusController.close();
    _syncProgressController.close();
    _syncMessageController.close();
    
    // Cancel active downloads
    for (final cancelToken in _activeDownloads.values) {
      cancelToken.cancel('Service disposed');
    }
    _activeDownloads.clear();
  }
}

class _OfflineInterceptor extends Interceptor {
  final OfflineSyncService syncService;

  _OfflineInterceptor(this.syncService);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // Add offline headers
    options.headers['X-Offline-Capable'] = 'true';
    options.headers['X-Bandwidth'] = syncService._currentBandwidth.toString();
    
    if (syncService._isLowBandwidth) {
      options.headers['X-Low-Bandwidth'] = 'true';
    }
    
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Handle offline errors
    if (err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.receiveTimeout ||
        err.type == DioExceptionType.connectionError) {
      
      // Queue operation for later sync if it's a write operation
      if (err.requestOptions.method != 'GET') {
        final operation = SyncOperation(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          type: 'api_call',
          method: err.requestOptions.method,
          endpoint: err.requestOptions.path,
          data: err.requestOptions.data ?? {},
          createdAt: DateTime.now(),
        );
        
        syncService.queueSyncOperation(operation);
      }
    }
    
    handler.next(err);
  }
}

class _BandwidthMonitorInterceptor extends Interceptor {
  final OfflineSyncService syncService;

  _BandwidthMonitorInterceptor(this.syncService);

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    // Monitor response times to estimate bandwidth
    final requestTime = response.requestOptions.extra['start_time'] as DateTime?;
    if (requestTime != null) {
      final duration = DateTime.now().difference(requestTime);
      final bytes = response.data?.toString().length ?? 0;
      
      if (duration.inMilliseconds > 0 && bytes > 0) {
        final kbps = (bytes * 8) / (duration.inMilliseconds / 1000.0) / 1000.0;
        
        // Update bandwidth estimation (simple moving average)
        syncService._currentBandwidth = 
            ((syncService._currentBandwidth * 0.8) + (kbps * 0.2)).round();
        
        syncService._isLowBandwidth = 
            syncService._currentBandwidth < AppConfig.liteModeThrsholdKbps;
      }
    }
    
    handler.next(response);
  }

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    options.extra['start_time'] = DateTime.now();
    handler.next(options);
  }
}

// Extension for unawaited futures
extension Unawaited on Future {
  void get unawaited => null;
}