import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/foundation.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:crypto/crypto.dart';
import 'package:sqflite/sqflite.dart';
import 'package:background_fetch/background_fetch.dart';

/// Comprehensive offline-first service for global accessibility
class OfflineFirstService {
  static const String _syncQueueBox = 'sync_queue';
  static const String _contentCacheBox = 'content_cache';
  static const String _userDataBox = 'user_data';
  static const String _coursesBox = 'courses';
  static const String _lessonsBox = 'lessons';
  static const String _progressBox = 'progress';
  static const String _settingsBox = 'settings';

  late Box _syncQueue;
  late Box _contentCache;
  late Box _userData;
  late Box _courses;
  late Box _lessons;
  late Box _progress;
  late Box _settings;

  late Database _database;
  late Dio _dio;

  final StreamController<List<ConnectivityResult>> _connectivityController =
      StreamController<List<ConnectivityResult>>.broadcast();
  final StreamController<SyncStatus> _syncStatusController =
      StreamController<SyncStatus>.broadcast();

  List<ConnectivityResult> _currentConnectivity = [ConnectivityResult.none];
  bool _isSyncing = false;
  Timer? _syncTimer;

  // Singleton pattern
  static final OfflineFirstService _instance = OfflineFirstService._internal();
  factory OfflineFirstService() => _instance;
  OfflineFirstService._internal();

  /// Initialize the offline-first service
  Future<void> initialize() async {
    try {
      await _initializeHive();
      await _initializeDatabase();
      await _initializeNetworking();
      await _initializeConnectivityMonitoring();
      await _initializeBackgroundSync();

      // Start periodic sync
      _startPeriodicSync();

      debugPrint('OfflineFirstService initialized successfully');
    } catch (e) {
      debugPrint('Failed to initialize OfflineFirstService: $e');
      rethrow;
    }
  }

  /// Initialize Hive boxes for local storage
  Future<void> _initializeHive() async {
    await Hive.initFlutter();

    // Register adapters for custom objects
    if (!Hive.isAdapterRegistered(0)) {
      Hive.registerAdapter(SyncItemAdapter());
    }
    if (!Hive.isAdapterRegistered(1)) {
      Hive.registerAdapter(CourseDataAdapter());
    }
    if (!Hive.isAdapterRegistered(2)) {
      Hive.registerAdapter(LessonDataAdapter());
    }
    if (!Hive.isAdapterRegistered(3)) {
      Hive.registerAdapter(ProgressDataAdapter());
    }

    // Open boxes
    _syncQueue = await Hive.openBox(_syncQueueBox);
    _contentCache = await Hive.openBox(_contentCacheBox);
    _userData = await Hive.openBox(_userDataBox);
    _courses = await Hive.openBox(_coursesBox);
    _lessons = await Hive.openBox(_lessonsBox);
    _progress = await Hive.openBox(_progressBox);
    _settings = await Hive.openBox(_settingsBox);
  }

  /// Initialize SQLite database for complex queries
  Future<void> _initializeDatabase() async {
    final documentsDirectory = await getApplicationDocumentsDirectory();
    final path = '${documentsDirectory.path}/eduverse_offline.db';

    _database = await openDatabase(
      path,
      version: 1,
      onCreate: _createDatabase,
      onUpgrade: _upgradeDatabase,
    );
  }

  /// Create database tables
  Future<void> _createDatabase(Database db, int version) async {
    // Content table for full-text search
    await db.execute('''
      CREATE TABLE content (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        content TEXT,
        metadata TEXT,
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL,
        sync_status TEXT DEFAULT 'synced'
      )
    ''');

    // Full-text search index
    await db.execute('''
      CREATE VIRTUAL TABLE content_fts USING fts5(
        title, description, content, content=content, content_rowid=rowid
      )
    ''');

    // Sync queue table
    await db.execute('''
      CREATE TABLE sync_queue (
        id TEXT PRIMARY KEY,
        operation TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        data TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        retry_count INTEGER DEFAULT 0,
        last_error TEXT
      )
    ''');

    // Analytics table for offline tracking
    await db.execute('''
      CREATE TABLE analytics (
        id TEXT PRIMARY KEY,
        event_type TEXT NOT NULL,
        event_data TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        synced INTEGER DEFAULT 0
      )
    ''');

    // Create indexes
    await db.execute('CREATE INDEX idx_content_type ON content(type)');
    await db.execute('CREATE INDEX idx_content_updated ON content(updated_at)');
    await db.execute(
        'CREATE INDEX idx_sync_queue_created ON sync_queue(created_at)');
    await db.execute('CREATE INDEX idx_analytics_synced ON analytics(synced)');
  }

  /// Upgrade database schema
  Future<void> _upgradeDatabase(
      Database db, int oldVersion, int newVersion) async {
    // Handle database migrations
    if (oldVersion < 2) {
      // Add new columns or tables for version 2
    }
  }

  /// Initialize networking with offline-first configuration
  Future<void> _initializeNetworking() async {
    _dio = Dio(BaseOptions(
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      sendTimeout: const Duration(seconds: 30),
    ));

    // Add interceptors
    _dio.interceptors.add(OfflineInterceptor(this));
    _dio.interceptors.add(CacheInterceptor(this));
    _dio.interceptors.add(RetryInterceptor());
  }

  /// Initialize connectivity monitoring
  Future<void> _initializeConnectivityMonitoring() async {
    final connectivity = Connectivity();

    // Get initial connectivity status
    _currentConnectivity = await connectivity.checkConnectivity();
    _connectivityController.add(_currentConnectivity);

    // Listen for connectivity changes
    connectivity.onConnectivityChanged
        .listen((List<ConnectivityResult> result) {
      _currentConnectivity = result;
      _connectivityController.add(result);

      // Trigger sync when connectivity is restored
      if (!result.contains(ConnectivityResult.none)) {
        _triggerSync();
      }
    });
  }

  /// Initialize background sync
  Future<void> _initializeBackgroundSync() async {
    await BackgroundFetch.configure(
      BackgroundFetchConfig(
        minimumFetchInterval: 15, // 15 minutes
        stopOnTerminate: false,
        enableHeadless: true,
        startOnBoot: true,
      ),
      _onBackgroundFetch,
      _onBackgroundFetchTimeout,
    );
  }

  /// Background fetch handler
  void _onBackgroundFetch(String taskId) async {
    debugPrint('Background fetch started: $taskId');

    try {
      await _performBackgroundSync();
      BackgroundFetch.finish(taskId);
    } catch (e) {
      debugPrint('Background fetch failed: $e');
      BackgroundFetch.finish(taskId);
    }
  }

  /// Background fetch timeout handler
  void _onBackgroundFetchTimeout(String taskId) {
    debugPrint('Background fetch timeout: $taskId');
    BackgroundFetch.finish(taskId);
  }

  /// Store data locally with automatic sync queuing
  Future<void> storeData(
    String key,
    dynamic data, {
    String? boxName,
    bool queueForSync = true,
  }) async {
    try {
      final box = _getBox(boxName);
      await box.put(key, data);

      // Queue for sync if online sync is needed
      if (queueForSync) {
        await _queueForSync('create', boxName ?? 'default', key, data);
      }

      // Update database for searchable content
      if (data is Map<String, dynamic> && data.containsKey('title')) {
        await _updateSearchableContent(key, data);
      }
    } catch (e) {
      debugPrint('Failed to store data: $e');
      rethrow;
    }
  }

  /// Retrieve data from local storage
  Future<T?> getData<T>(String key, {String? boxName}) async {
    try {
      final box = _getBox(boxName);
      return box.get(key) as T?;
    } catch (e) {
      debugPrint('Failed to get data: $e');
      return null;
    }
  }

  /// Search content offline using FTS
  Future<List<Map<String, dynamic>>> searchContent(
    String query, {
    String? contentType,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      String sql = '''
        SELECT c.* FROM content c
        JOIN content_fts fts ON c.rowid = fts.rowid
        WHERE content_fts MATCH ?
      ''';

      List<dynamic> args = [query];

      if (contentType != null) {
        sql += ' AND c.type = ?';
        args.add(contentType);
      }

      sql += ' ORDER BY rank LIMIT ? OFFSET ?';
      args.addAll([limit, offset]);

      final results = await _database.rawQuery(sql, args);

      return results
          .map((row) => {
                ...row,
                'metadata': row['metadata'] != null
                    ? jsonDecode(row['metadata'] as String)
                    : null,
              })
          .toList();
    } catch (e) {
      debugPrint('Failed to search content: $e');
      return [];
    }
  }

  /// Download content for offline access
  Future<void> downloadForOffline(
    String contentId,
    String url, {
    Map<String, dynamic>? metadata,
    Function(double)? onProgress,
  }) async {
    try {
      final response = await _dio.get(
        url,
        options: Options(responseType: ResponseType.bytes),
        onReceiveProgress: (received, total) {
          if (total != -1 && onProgress != null) {
            onProgress(received / total);
          }
        },
      );

      // Store content locally
      final contentHash = _generateContentHash(response.data);
      await _storeOfflineContent(
          contentId, response.data, contentHash, metadata);

      // Update content registry
      await storeData(
        'offline_content_$contentId',
        {
          'id': contentId,
          'url': url,
          'hash': contentHash,
          'size': response.data.length,
          'downloaded_at': DateTime.now().millisecondsSinceEpoch,
          'metadata': metadata,
        },
        boxName: _contentCacheBox,
        queueForSync: false,
      );
    } catch (e) {
      debugPrint('Failed to download content: $e');
      rethrow;
    }
  }

  /// Get offline content
  Future<Uint8List?> getOfflineContent(String contentId) async {
    try {
      final contentInfo = await getData<Map<String, dynamic>>(
        'offline_content_$contentId',
        boxName: _contentCacheBox,
      );

      if (contentInfo == null) return null;

      final documentsDirectory = await getApplicationDocumentsDirectory();
      final contentPath =
          '${documentsDirectory.path}/offline_content/${contentInfo['hash']}';
      final contentFile = File(contentPath);

      if (await contentFile.exists()) {
        return await contentFile.readAsBytes();
      }

      return null;
    } catch (e) {
      debugPrint('Failed to get offline content: $e');
      return null;
    }
  }

  /// Sync data with server
  Future<void> sync({bool force = false}) async {
    if (_isSyncing && !force) return;

    _isSyncing = true;
    _syncStatusController.add(SyncStatus.syncing);

    try {
      // Check connectivity
      if (_currentConnectivity.contains(ConnectivityResult.none)) {
        _syncStatusController.add(SyncStatus.offline);
        return;
      }

      // Process sync queue
      await _processSyncQueue();

      // Sync user data
      await _syncUserData();

      // Sync course progress
      await _syncProgress();

      // Sync analytics
      await _syncAnalytics();

      _syncStatusController.add(SyncStatus.synced);
    } catch (e) {
      debugPrint('Sync failed: $e');
      _syncStatusController.add(SyncStatus.error);
    } finally {
      _isSyncing = false;
    }
  }

  /// Queue operation for sync
  Future<void> _queueForSync(
    String operation,
    String entityType,
    String entityId,
    dynamic data,
  ) async {
    final syncItem = SyncItem(
      id: _generateId(),
      operation: operation,
      entityType: entityType,
      entityId: entityId,
      data: data,
      createdAt: DateTime.now(),
      retryCount: 0,
    );

    await _syncQueue.put(syncItem.id, syncItem);

    // Also store in database for persistence
    await _database.insert('sync_queue', {
      'id': syncItem.id,
      'operation': operation,
      'entity_type': entityType,
      'entity_id': entityId,
      'data': jsonEncode(data),
      'created_at': syncItem.createdAt.millisecondsSinceEpoch,
      'retry_count': 0,
    });
  }

  /// Process sync queue
  Future<void> _processSyncQueue() async {
    final queueItems = _syncQueue.values.cast<SyncItem>().toList();

    for (final item in queueItems) {
      try {
        await _processSyncItem(item);
        await _syncQueue.delete(item.id);

        // Remove from database
        await _database.delete(
          'sync_queue',
          where: 'id = ?',
          whereArgs: [item.id],
        );
      } catch (e) {
        debugPrint('Failed to sync item ${item.id}: $e');

        // Update retry count
        item.retryCount++;
        item.lastError = e.toString();

        if (item.retryCount < 3) {
          await _syncQueue.put(item.id, item);
        } else {
          // Remove failed item after 3 retries
          await _syncQueue.delete(item.id);
          await _database.delete(
            'sync_queue',
            where: 'id = ?',
            whereArgs: [item.id],
          );
        }
      }
    }
  }

  /// Process individual sync item
  Future<void> _processSyncItem(SyncItem item) async {
    switch (item.operation) {
      case 'create':
        await _syncCreate(item);
        break;
      case 'update':
        await _syncUpdate(item);
        break;
      case 'delete':
        await _syncDelete(item);
        break;
    }
  }

  /// Sync create operation
  Future<void> _syncCreate(SyncItem item) async {
    final response = await _dio.post(
      '/api/v1/${item.entityType}',
      data: item.data,
    );

    if (response.statusCode == 201) {
      // Update local data with server response
      final box = _getBox(item.entityType);
      await box.put(item.entityId, response.data);
    }
  }

  /// Sync update operation
  Future<void> _syncUpdate(SyncItem item) async {
    final response = await _dio.put(
      '/api/v1/${item.entityType}/${item.entityId}',
      data: item.data,
    );

    if (response.statusCode == 200) {
      // Update local data with server response
      final box = _getBox(item.entityType);
      await box.put(item.entityId, response.data);
    }
  }

  /// Sync delete operation
  Future<void> _syncDelete(SyncItem item) async {
    final response = await _dio.delete(
      '/api/v1/${item.entityType}/${item.entityId}',
    );

    if (response.statusCode == 200) {
      // Remove from local storage
      final box = _getBox(item.entityType);
      await box.delete(item.entityId);
    }
  }

  /// Get appropriate Hive box
  Box _getBox(String? boxName) {
    switch (boxName) {
      case _coursesBox:
        return _courses;
      case _lessonsBox:
        return _lessons;
      case _progressBox:
        return _progress;
      case _userDataBox:
        return _userData;
      case _contentCacheBox:
        return _contentCache;
      case _settingsBox:
        return _settings;
      default:
        return _userData;
    }
  }

  /// Store offline content
  Future<void> _storeOfflineContent(
    String contentId,
    Uint8List data,
    String hash,
    Map<String, dynamic>? metadata,
  ) async {
    final documentsDirectory = await getApplicationDocumentsDirectory();
    final offlineDir = Directory('${documentsDirectory.path}/offline_content');

    if (!await offlineDir.exists()) {
      await offlineDir.create(recursive: true);
    }

    final contentFile = File('${offlineDir.path}/$hash');
    await contentFile.writeAsBytes(data);
  }

  /// Generate content hash
  String _generateContentHash(Uint8List data) {
    final digest = sha256.convert(data);
    return digest.toString();
  }

  /// Update searchable content in database
  Future<void> _updateSearchableContent(
      String id, Map<String, dynamic> data) async {
    await _database.insert(
      'content',
      {
        'id': id,
        'type': data['type'] ?? 'unknown',
        'title': data['title'] ?? '',
        'description': data['description'] ?? '',
        'content': data['content'] ?? '',
        'metadata': jsonEncode(data),
        'created_at': DateTime.now().millisecondsSinceEpoch,
        'updated_at': DateTime.now().millisecondsSinceEpoch,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );

    // Update FTS index
    await _database.insert(
      'content_fts',
      {
        'rowid': await _database.rawQuery('SELECT last_insert_rowid()').then(
              (result) => result.first['last_insert_rowid()'],
            ),
        'title': data['title'] ?? '',
        'description': data['description'] ?? '',
        'content': data['content'] ?? '',
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  /// Start periodic sync
  void _startPeriodicSync() {
    _syncTimer = Timer.periodic(const Duration(minutes: 5), (timer) {
      if (!_currentConnectivity.contains(ConnectivityResult.none)) {
        sync();
      }
    });
  }

  /// Trigger immediate sync
  void _triggerSync() {
    if (_currentConnectivity != ConnectivityResult.none) {
      Future.delayed(const Duration(seconds: 2), () => sync());
    }
  }

  /// Perform background sync
  Future<void> _performBackgroundSync() async {
    if (_currentConnectivity.contains(ConnectivityResult.none)) return;

    // Sync critical data only in background
    await _syncProgress();
    await _syncAnalytics();
  }

  /// Sync user data
  Future<void> _syncUserData() async {
    // Implementation for syncing user data
  }

  /// Sync progress data
  Future<void> _syncProgress() async {
    // Implementation for syncing progress data
  }

  /// Sync analytics data
  Future<void> _syncAnalytics() async {
    final unsynced = await _database.query(
      'analytics',
      where: 'synced = ?',
      whereArgs: [0],
    );

    for (final record in unsynced) {
      try {
        await _dio.post('/api/v1/analytics', data: {
          'event_type': record['event_type'],
          'event_data': jsonDecode(record['event_data'] as String),
          'timestamp': record['timestamp'],
        });

        // Mark as synced
        await _database.update(
          'analytics',
          {'synced': 1},
          where: 'id = ?',
          whereArgs: [record['id']],
        );
      } catch (e) {
        debugPrint('Failed to sync analytics record: $e');
      }
    }
  }

  /// Generate unique ID
  String _generateId() {
    return DateTime.now().millisecondsSinceEpoch.toString() +
        (1000 + (DateTime.now().microsecond % 9000)).toString();
  }

  /// Get connectivity stream
  Stream<List<ConnectivityResult>> get connectivityStream =>
      _connectivityController.stream;

  /// Get sync status stream
  Stream<SyncStatus> get syncStatusStream => _syncStatusController.stream;

  /// Check if currently online
  bool get isOnline => !_currentConnectivity.contains(ConnectivityResult.none);

  /// Check if currently syncing
  bool get isSyncing => _isSyncing;

  /// Dispose resources
  Future<void> dispose() async {
    _syncTimer?.cancel();
    await _connectivityController.close();
    await _syncStatusController.close();
    await _database.close();
    await Hive.close();
  }
}

/// Sync status enumeration
enum SyncStatus {
  synced,
  syncing,
  offline,
  error,
}

/// Sync item model
@HiveType(typeId: 0)
class SyncItem extends HiveObject {
  @HiveField(0)
  String id;

  @HiveField(1)
  String operation;

  @HiveField(2)
  String entityType;

  @HiveField(3)
  String entityId;

  @HiveField(4)
  dynamic data;

  @HiveField(5)
  DateTime createdAt;

  @HiveField(6)
  int retryCount;

  @HiveField(7)
  String? lastError;

  SyncItem({
    required this.id,
    required this.operation,
    required this.entityType,
    required this.entityId,
    required this.data,
    required this.createdAt,
    this.retryCount = 0,
    this.lastError,
  });
}

/// Course data model
@HiveType(typeId: 1)
class CourseData extends HiveObject {
  @HiveField(0)
  String id;

  @HiveField(1)
  String title;

  @HiveField(2)
  String description;

  @HiveField(3)
  String instructor;

  @HiveField(4)
  List<String> modules;

  @HiveField(5)
  Map<String, dynamic> metadata;

  CourseData({
    required this.id,
    required this.title,
    required this.description,
    required this.instructor,
    required this.modules,
    required this.metadata,
  });
}

/// Lesson data model
@HiveType(typeId: 2)
class LessonData extends HiveObject {
  @HiveField(0)
  String id;

  @HiveField(1)
  String courseId;

  @HiveField(2)
  String title;

  @HiveField(3)
  String content;

  @HiveField(4)
  int duration;

  @HiveField(5)
  Map<String, dynamic> metadata;

  LessonData({
    required this.id,
    required this.courseId,
    required this.title,
    required this.content,
    required this.duration,
    required this.metadata,
  });
}

/// Progress data model
@HiveType(typeId: 3)
class ProgressData extends HiveObject {
  @HiveField(0)
  String userId;

  @HiveField(1)
  String courseId;

  @HiveField(2)
  String lessonId;

  @HiveField(3)
  double progress;

  @HiveField(4)
  DateTime lastAccessed;

  @HiveField(5)
  Map<String, dynamic> metadata;

  ProgressData({
    required this.userId,
    required this.courseId,
    required this.lessonId,
    required this.progress,
    required this.lastAccessed,
    required this.metadata,
  });
}

/// Offline interceptor for Dio
class OfflineInterceptor extends Interceptor {
  final OfflineFirstService offlineService;

  OfflineInterceptor(this.offlineService);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // Add offline headers
    options.headers['X-Offline-Capable'] = 'true';
    options.headers['X-Client-Version'] = '1.0.0';

    super.onRequest(options, handler);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Handle offline errors
    if (err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.receiveTimeout ||
        err.type == DioExceptionType.connectionError) {
      // Try to serve from cache
      // Implementation for serving cached responses
    }

    super.onError(err, handler);
  }
}

/// Cache interceptor for Dio
class CacheInterceptor extends Interceptor {
  final OfflineFirstService offlineService;

  CacheInterceptor(this.offlineService);

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    // Cache successful responses
    if (response.statusCode == 200) {
      // Implementation for caching responses
    }

    super.onResponse(response, handler);
  }
}

/// Retry interceptor for Dio
class RetryInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Implement retry logic for failed requests
    super.onError(err, handler);
  }
}

/// Hive adapters
class SyncItemAdapter extends TypeAdapter<SyncItem> {
  @override
  final int typeId = 0;

  @override
  SyncItem read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return SyncItem(
      id: fields[0] as String,
      operation: fields[1] as String,
      entityType: fields[2] as String,
      entityId: fields[3] as String,
      data: fields[4] as dynamic,
      createdAt: fields[5] as DateTime,
      retryCount: fields[6] as int,
      lastError: fields[7] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, SyncItem obj) {
    writer
      ..writeByte(8)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.operation)
      ..writeByte(2)
      ..write(obj.entityType)
      ..writeByte(3)
      ..write(obj.entityId)
      ..writeByte(4)
      ..write(obj.data)
      ..writeByte(5)
      ..write(obj.createdAt)
      ..writeByte(6)
      ..write(obj.retryCount)
      ..writeByte(7)
      ..write(obj.lastError);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SyncItemAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class CourseDataAdapter extends TypeAdapter<CourseData> {
  @override
  final int typeId = 1;

  @override
  CourseData read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return CourseData(
      id: fields[0] as String,
      title: fields[1] as String,
      description: fields[2] as String,
      instructor: fields[3] as String,
      modules: (fields[4] as List).cast<String>(),
      metadata: (fields[5] as Map).cast<String, dynamic>(),
    );
  }

  @override
  void write(BinaryWriter writer, CourseData obj) {
    writer
      ..writeByte(6)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.title)
      ..writeByte(2)
      ..write(obj.description)
      ..writeByte(3)
      ..write(obj.instructor)
      ..writeByte(4)
      ..write(obj.modules)
      ..writeByte(5)
      ..write(obj.metadata);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CourseDataAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class LessonDataAdapter extends TypeAdapter<LessonData> {
  @override
  final int typeId = 2;

  @override
  LessonData read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return LessonData(
      id: fields[0] as String,
      courseId: fields[1] as String,
      title: fields[2] as String,
      content: fields[3] as String,
      duration: fields[4] as int,
      metadata: (fields[5] as Map).cast<String, dynamic>(),
    );
  }

  @override
  void write(BinaryWriter writer, LessonData obj) {
    writer
      ..writeByte(6)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.courseId)
      ..writeByte(2)
      ..write(obj.title)
      ..writeByte(3)
      ..write(obj.content)
      ..writeByte(4)
      ..write(obj.duration)
      ..writeByte(5)
      ..write(obj.metadata);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is LessonDataAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class ProgressDataAdapter extends TypeAdapter<ProgressData> {
  @override
  final int typeId = 3;

  @override
  ProgressData read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return ProgressData(
      userId: fields[0] as String,
      courseId: fields[1] as String,
      lessonId: fields[2] as String,
      progress: fields[3] as double,
      lastAccessed: fields[4] as DateTime,
      metadata: (fields[5] as Map).cast<String, dynamic>(),
    );
  }

  @override
  void write(BinaryWriter writer, ProgressData obj) {
    writer
      ..writeByte(6)
      ..writeByte(0)
      ..write(obj.userId)
      ..writeByte(1)
      ..write(obj.courseId)
      ..writeByte(2)
      ..write(obj.lessonId)
      ..writeByte(3)
      ..write(obj.progress)
      ..writeByte(4)
      ..write(obj.lastAccessed)
      ..writeByte(5)
      ..write(obj.metadata);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ProgressDataAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
