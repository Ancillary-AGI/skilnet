/**
 * K6 Load Testing Script for EduVerse Platform
 * Tests various endpoints under different load conditions
 */

import http from 'k6/http';
import ws from 'k6/ws';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');
const wsConnections = new Counter('websocket_connections');
const vrSessions = new Counter('vr_sessions');
const aiInteractions = new Counter('ai_interactions');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.1'],    // Error rate under 10%
    error_rate: ['rate<0.05'],        // Custom error rate under 5%
    websocket_connections: ['count>100'], // At least 100 WS connections
  },
};

// Base URL
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const WS_URL = __ENV.WS_URL || 'ws://localhost:8000';

// Test data
const testUsers = [
  { email: 'student1@example.com', password: 'password123' },
  { email: 'student2@example.com', password: 'password123' },
  { email: 'instructor1@example.com', password: 'password123' },
];

const courseIds = ['course-1', 'course-2', 'course-3'];
const lessonIds = ['lesson-1', 'lesson-2', 'lesson-3'];

export function setup() {
  // Setup test data
  console.log('Setting up load test...');
  
  // Create test users and courses
  const setupData = {
    users: testUsers,
    courses: courseIds,
    lessons: lessonIds,
  };
  
  return setupData;
}

export default function(data) {
  const user = data.users[Math.floor(Math.random() * data.users.length)];
  
  group('Authentication Flow', () => {
    // Login
    const loginResponse = http.post(`${BASE_URL}/api/v1/auth/login`, {
      username: user.email,
      password: user.password,
    });
    
    check(loginResponse, {
      'login successful': (r) => r.status === 200,
      'login response time OK': (r) => r.timings.duration < 1000,
    });
    
    errorRate.add(loginResponse.status !== 200);
    responseTime.add(loginResponse.timings.duration);
    
    if (loginResponse.status !== 200) {
      return; // Skip rest of test if login fails
    }
    
    const authToken = loginResponse.json('access_token');
    const headers = { Authorization: `Bearer ${authToken}` };
    
    // Get user profile
    const profileResponse = http.get(`${BASE_URL}/api/v1/auth/me`, { headers });
    check(profileResponse, {
      'profile fetch successful': (r) => r.status === 200,
    });
  });
  
  group('Course Browsing', () => {
    // Browse courses
    const coursesResponse = http.get(`${BASE_URL}/api/v1/courses/`);
    check(coursesResponse, {
      'courses loaded': (r) => r.status === 200,
      'courses response time OK': (r) => r.timings.duration < 2000,
    });
    
    // Search courses
    const searchResponse = http.get(`${BASE_URL}/api/v1/courses/?search=machine learning`);
    check(searchResponse, {
      'search successful': (r) => r.status === 200,
    });
    
    // Get course details
    const courseId = data.courses[Math.floor(Math.random() * data.courses.length)];
    const courseDetailResponse = http.get(`${BASE_URL}/api/v1/courses/${courseId}`);
    check(courseDetailResponse, {
      'course details loaded': (r) => r.status === 200,
    });
  });
  
  group('Learning Activities', () => {
    const authToken = 'mock-token'; // In real test, get from login
    const headers = { Authorization: `Bearer ${authToken}` };
    
    // Enroll in course
    const courseId = data.courses[0];
    const enrollResponse = http.post(
      `${BASE_URL}/api/v1/courses/${courseId}/enroll`,
      {},
      { headers }
    );
    
    // Update lesson progress
    const lessonId = data.lessons[0];
    const progressData = {
      completion_percentage: 75.0,
      time_spent_minutes: 15,
      quiz_score: 85.0,
      vr_interactions_count: 5,
    };
    
    const progressResponse = http.post(
      `${BASE_URL}/api/v1/courses/${courseId}/modules/module-1/lessons/${lessonId}/progress`,
      JSON.stringify(progressData),
      { headers: { ...headers, 'Content-Type': 'application/json' } }
    );
    
    check(progressResponse, {
      'progress update successful': (r) => r.status === 200,
    });
  });
  
  group('AI Interactions', () => {
    const authToken = 'mock-token';
    const headers = { Authorization: `Bearer ${authToken}` };
    
    // AI tutor chat
    const chatData = {
      message: 'Explain quantum computing',
      context: { course: 'physics-101', lesson: 'quantum-basics' },
    };
    
    const chatResponse = http.post(
      `${BASE_URL}/api/v1/ai/chat`,
      JSON.stringify(chatData),
      { headers: { ...headers, 'Content-Type': 'application/json' } }
    );
    
    check(chatResponse, {
      'AI chat successful': (r) => r.status === 200,
      'AI response time acceptable': (r) => r.timings.duration < 3000,
    });
    
    aiInteractions.add(1);
    
    // AI content generation
    const contentRequest = {
      type: 'video',
      topic: 'Introduction to AI',
      duration: 300,
    };
    
    const contentResponse = http.post(
      `${BASE_URL}/api/v1/courses/course-1/generate-ai-content`,
      JSON.stringify(contentRequest),
      { headers: { ...headers, 'Content-Type': 'application/json' } }
    );
    
    check(contentResponse, {
      'AI content generation started': (r) => r.status === 200,
    });
  });
  
  group('VR Classroom', () => {
    // Test VR session creation
    const authToken = 'mock-token';
    const headers = { Authorization: `Bearer ${authToken}` };
    
    const vrSessionData = {
      room_name: 'Load Test VR Room',
      max_participants: 30,
      environment: 'modern_classroom',
    };
    
    const vrResponse = http.post(
      `${BASE_URL}/api/v1/vr/sessions`,
      JSON.stringify(vrSessionData),
      { headers: { ...headers, 'Content-Type': 'application/json' } }
    );
    
    check(vrResponse, {
      'VR session created': (r) => r.status === 200,
    });
    
    vrSessions.add(1);
    
    // Test spatial updates
    const spatialData = {
      position: [Math.random() * 10, 0, Math.random() * 10],
      rotation: [0, Math.random() * 360, 0, 1],
      head_position: [Math.random() * 10, 1.7, Math.random() * 10],
    };
    
    const spatialResponse = http.post(
      `${BASE_URL}/api/v1/vr/sessions/test-room/spatial-update`,
      JSON.stringify(spatialData),
      { headers: { ...headers, 'Content-Type': 'application/json' } }
    );
    
    check(spatialResponse, {
      'spatial update successful': (r) => r.status === 200,
    });
  });
  
  group('WebSocket Connections', () => {
    // Test WebSocket classroom connection
    const wsUrl = `${WS_URL}/ws/classroom/load-test-room`;
    
    const wsResponse = ws.connect(wsUrl, {}, function (socket) {
      socket.on('open', () => {
        wsConnections.add(1);
        console.log('WebSocket connected');
      });
      
      socket.on('message', (data) => {
        const message = JSON.parse(data);
        check(message, {
          'valid WebSocket message': (msg) => msg.type !== undefined,
        });
      });
      
      socket.on('close', () => {
        console.log('WebSocket disconnected');
      });
      
      // Send test messages
      for (let i = 0; i < 5; i++) {
        socket.send(JSON.stringify({
          type: 'chat_message',
          content: `Load test message ${i}`,
          timestamp: new Date().toISOString(),
        }));
        sleep(1);
      }
      
      sleep(10); // Keep connection open for 10 seconds
    });
  });
  
  // Random sleep between 1-3 seconds
  sleep(Math.random() * 2 + 1);
}

export function teardown(data) {
  console.log('Load test completed');
  console.log(`Total VR sessions: ${vrSessions.count}`);
  console.log(`Total AI interactions: ${aiInteractions.count}`);
  console.log(`Total WebSocket connections: ${wsConnections.count}`);
}

// Stress test scenario
export function stressTest() {
  group('Stress Test - High Load', () => {
    // Simulate extreme load conditions
    const requests = [];
    
    // Create 100 concurrent requests
    for (let i = 0; i < 100; i++) {
      requests.push(http.get(`${BASE_URL}/api/v1/courses/`));
    }
    
    // Check that system handles stress
    const responses = http.batch(requests);
    
    let successCount = 0;
    responses.forEach((response) => {
      if (response.status === 200) {
        successCount++;
      }
    });
    
    check(successCount, {
      'stress test success rate > 90%': (count) => count / responses.length > 0.9,
    });
  });
}

// Spike test scenario
export function spikeTest() {
  group('Spike Test - Sudden Load', () => {
    // Simulate sudden traffic spike
    const spikeRequests = [];
    
    for (let i = 0; i < 500; i++) {
      spikeRequests.push(http.get(`${BASE_URL}/api/v1/courses/featured`));
    }
    
    const startTime = Date.now();
    const responses = http.batch(spikeRequests);
    const endTime = Date.now();
    
    const totalTime = endTime - startTime;
    
    check(totalTime, {
      'spike handled within 10 seconds': (time) => time < 10000,
    });
    
    const errorCount = responses.filter(r => r.status !== 200).length;
    check(errorCount, {
      'spike error rate < 20%': (errors) => errors / responses.length < 0.2,
    });
  });
}

// Volume test scenario
export function volumeTest() {
  group('Volume Test - Large Data', () => {
    // Test with large payloads
    const largeContent = 'x'.repeat(1024 * 1024); // 1MB content
    
    const uploadResponse = http.post(
      `${BASE_URL}/api/v1/courses/upload-content`,
      {
        file: http.file(largeContent, 'large-file.txt', 'text/plain'),
        course_id: 'test-course',
        content_type: 'text',
      },
      {
        headers: { Authorization: 'Bearer mock-token' },
      }
    );
    
    check(uploadResponse, {
      'large file upload successful': (r) => r.status === 200,
      'large file upload time acceptable': (r) => r.timings.duration < 30000,
    });
  });
}

// Endurance test scenario
export function enduranceTest() {
  group('Endurance Test - Long Running', () => {
    // Simulate long-running user session
    const sessionDuration = 30 * 60; // 30 minutes
    const startTime = Date.now();
    
    while ((Date.now() - startTime) < sessionDuration * 1000) {
      // Simulate user activities
      http.get(`${BASE_URL}/api/v1/courses/`);
      sleep(5);
      
      http.get(`${BASE_URL}/api/v1/auth/me`, {
        headers: { Authorization: 'Bearer mock-token' },
      });
      sleep(10);
      
      // Simulate VR interaction
      http.post(
        `${BASE_URL}/api/v1/vr/sessions/endurance-room/spatial-update`,
        JSON.stringify({
          position: [Math.random() * 10, 0, Math.random() * 10],
          rotation: [0, Math.random() * 360, 0, 1],
        }),
        {
          headers: {
            Authorization: 'Bearer mock-token',
            'Content-Type': 'application/json',
          },
        }
      );
      sleep(2);
      
      // Check memory usage doesn't grow unbounded
      const memoryResponse = http.get(`${BASE_URL}/api/v1/system/memory`);
      if (memoryResponse.status === 200) {
        const memoryUsage = memoryResponse.json('memory_usage_mb');
        check(memoryUsage, {
          'memory usage stable': (usage) => usage < 2048, // Less than 2GB
        });
      }
      
      sleep(30);
    }
  });
}

// Security test scenario
export function securityTest() {
  group('Security Test - Attack Simulation', () => {
    // Test SQL injection protection
    const sqlInjectionPayloads = [
      "'; DROP TABLE users; --",
      "' OR '1'='1",
      "'; UPDATE users SET is_superuser=true; --",
    ];
    
    sqlInjectionPayloads.forEach((payload) => {
      const response = http.post(`${BASE_URL}/api/v1/auth/login`, {
        username: payload,
        password: 'password',
      });
      
      check(response, {
        'SQL injection blocked': (r) => r.status !== 200 || !r.body.includes('admin'),
      });
    });
    
    // Test XSS protection
    const xssPayloads = [
      "<script>alert('xss')</script>",
      "javascript:alert('xss')",
      "<img src=x onerror=alert('xss')>",
    ];
    
    xssPayloads.forEach((payload) => {
      const response = http.put(
        `${BASE_URL}/api/v1/users/profile`,
        JSON.stringify({ bio: payload }),
        {
          headers: {
            Authorization: 'Bearer mock-token',
            'Content-Type': 'application/json',
          },
        }
      );
      
      check(response, {
        'XSS payload sanitized': (r) => !r.body.includes('<script>'),
      });
    });
    
    // Test rate limiting
    const rateLimitRequests = [];
    for (let i = 0; i < 100; i++) {
      rateLimitRequests.push(http.post(`${BASE_URL}/api/v1/auth/login`, {
        username: 'test@example.com',
        password: 'wrongpassword',
      }));
    }
    
    const rateLimitResponses = http.batch(rateLimitRequests);
    const rateLimitedCount = rateLimitResponses.filter(r => r.status === 429).length;
    
    check(rateLimitedCount, {
      'rate limiting active': (count) => count > 0,
    });
  });
}

// WebSocket stress test
export function websocketStressTest() {
  group('WebSocket Stress Test', () => {
    const wsUrl = `${WS_URL}/ws/classroom/stress-test-room`;
    
    ws.connect(wsUrl, {}, function (socket) {
      socket.on('open', () => {
        wsConnections.add(1);
        
        // Send rapid messages
        for (let i = 0; i < 100; i++) {
          socket.send(JSON.stringify({
            type: 'stress_test_message',
            content: `Message ${i}`,
            timestamp: new Date().toISOString(),
          }));
          
          if (i % 10 === 0) {
            sleep(0.1); // Brief pause every 10 messages
          }
        }
      });
      
      socket.on('message', (data) => {
        const message = JSON.parse(data);
        check(message, {
          'WebSocket message valid': (msg) => msg.type !== undefined,
        });
      });
      
      socket.setTimeout(() => {
        socket.close();
      }, 30000); // Close after 30 seconds
    });
  });
}

// AI model performance test
export function aiPerformanceTest() {
  group('AI Performance Test', () => {
    const authToken = 'mock-token';
    const headers = {
      Authorization: `Bearer ${authToken}`,
      'Content-Type': 'application/json',
    };
    
    // Test AI chat response time
    const chatStartTime = Date.now();
    const chatResponse = http.post(
      `${BASE_URL}/api/v1/ai/chat`,
      JSON.stringify({
        message: 'Explain machine learning algorithms',
        context: { course: 'ml-101', difficulty: 'beginner' },
      }),
      { headers }
    );
    const chatEndTime = Date.now();
    
    check(chatResponse, {
      'AI chat response received': (r) => r.status === 200,
      'AI chat response time acceptable': (r) => (chatEndTime - chatStartTime) < 5000,
    });
    
    // Test AI video generation
    const videoGenStartTime = Date.now();
    const videoResponse = http.post(
      `${BASE_URL}/api/v1/courses/test-course/generate-ai-content`,
      JSON.stringify({
        type: 'video',
        topic: 'Neural Networks',
        duration: 60,
        style: 'educational',
      }),
      { headers }
    );
    const videoGenEndTime = Date.now();
    
    check(videoResponse, {
      'AI video generation started': (r) => r.status === 200,
      'AI video generation response time OK': (r) => (videoGenEndTime - videoGenStartTime) < 2000,
    });
    
    aiInteractions.add(2);
  });
}

// Database performance test
export function databasePerformanceTest() {
  group('Database Performance Test', () => {
    // Test complex queries
    const complexQueryResponse = http.get(
      `${BASE_URL}/api/v1/analytics/course-performance?include_detailed_stats=true`
    );
    
    check(complexQueryResponse, {
      'complex query successful': (r) => r.status === 200,
      'complex query time acceptable': (r) => r.timings.duration < 5000,
    });
    
    // Test concurrent database operations
    const concurrentRequests = [];
    for (let i = 0; i < 50; i++) {
      concurrentRequests.push(
        http.get(`${BASE_URL}/api/v1/courses/?skip=${i * 20}&limit=20`)
      );
    }
    
    const concurrentResponses = http.batch(concurrentRequests);
    const successfulResponses = concurrentResponses.filter(r => r.status === 200);
    
    check(successfulResponses.length, {
      'concurrent DB operations successful': (count) => count / concurrentRequests.length > 0.95,
    });
  });
}

// Memory leak test
export function memoryLeakTest() {
  group('Memory Leak Test', () => {
    // Perform memory-intensive operations repeatedly
    for (let iteration = 0; iteration < 100; iteration++) {
      // Large data processing
      const largeDataResponse = http.get(`${BASE_URL}/api/v1/courses/?limit=1000`);
      
      // AI processing
      http.post(
        `${BASE_URL}/api/v1/ai/chat`,
        JSON.stringify({
          message: 'Generate a long explanation about quantum physics',
          context: { detailed: true, include_examples: true },
        }),
        {
          headers: {
            Authorization: 'Bearer mock-token',
            'Content-Type': 'application/json',
          },
        }
      );
      
      // Check memory usage periodically
      if (iteration % 10 === 0) {
        const memoryResponse = http.get(`${BASE_URL}/api/v1/system/memory`);
        if (memoryResponse.status === 200) {
          const memoryData = memoryResponse.json();
          console.log(`Memory usage at iteration ${iteration}: ${memoryData.memory_usage_mb}MB`);
        }
      }
      
      sleep(0.1);
    }
  });
}