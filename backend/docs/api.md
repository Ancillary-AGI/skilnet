# EduVerse API Documentation

## Overview

EduVerse is a comprehensive social e-learning platform with VR/AR capabilities and AI-powered personalization. This API provides access to all platform features including authentication, course management, real-time collaboration, analytics, and more.

## Base URL

```
http://localhost:8000/api/v1
```

## WebSocket URL

```
ws://localhost:8000/ws/{user_id}
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Social Authentication

The platform supports multiple authentication methods:

- **Email/Password**: Traditional authentication
- **Google OAuth**: Social login via Google
- **Apple Sign In**: Social login via Apple
- **Facebook Login**: Social login via Facebook
- **Biometric**: Fingerprint/Face authentication

## API Endpoints

### Authentication Endpoints

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

#### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

#### Social Login
```http
POST /auth/firebase/verify
Content-Type: application/json

{
  "id_token": "firebase_id_token",
  "firebase_uid": "firebase_user_id"
}
```

### Course Management

#### Get All Courses
```http
GET /courses
Authorization: Bearer <token>
```

#### Get Course Details
```http
GET /courses/{course_id}
Authorization: Bearer <token>
```

#### Enroll in Course
```http
POST /courses/{course_id}/enroll
Authorization: Bearer <token>
```

### Real-Time Collaboration

#### Join Collaboration Room
```http
POST /collaboration/rooms/{room_id}/join
Authorization: Bearer <token>
```

#### Send Message
```http
POST /collaboration/rooms/{room_id}/messages
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Hello everyone!",
  "message_type": "text"
}
```

### Analytics & Progress

#### Get User Analytics
```http
GET /analytics/dashboard
Authorization: Bearer <token>
```

#### Get Learning Insights
```http
GET /analytics/insights
Authorization: Bearer <token>
```

### Subscription Management

#### Get Subscription Status
```http
GET /subscription
Authorization: Bearer <token>
```

#### Upgrade Subscription
```http
POST /subscription/upgrade
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan_id": "premium_monthly"
}
```

## Response Formats

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Free tier**: 100 requests per hour
- **Premium tier**: 1000 requests per hour
- **Enterprise tier**: Unlimited

## WebSocket Events

### Event Types

#### User Events
- `user_joined`: User joined a room
- `user_left`: User left a room
- `presence_update`: User presence status changed

#### Message Events
- `new_message`: New message in room
- `message_edited`: Message was edited
- `message_deleted`: Message was deleted

#### Course Events
- `course_updated`: Course content was updated
- `lesson_completed`: User completed a lesson
- `quiz_submitted`: User submitted a quiz

#### System Events
- `achievement_unlocked`: User earned an achievement
- `live_class_started`: Live class is starting
- `system_announcement`: System-wide announcement

### Example WebSocket Message
```json
{
  "type": "new_message",
  "data": {
    "message_id": "msg_123",
    "room_id": "room_456",
    "user_id": "user_789",
    "content": "Hello everyone!",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server issue |

## SDKs and Libraries

### Python SDK
```python
from eduverse_sdk import EduVerseClient

client = EduVerseClient(api_key="your_api_key")

# Get courses
courses = client.get_courses()

# Enroll in course
client.enroll_in_course("course_id")

# Join collaboration room
client.join_room("room_id")
```

### JavaScript SDK
```javascript
import { EduVerseClient } from 'eduverse-sdk';

const client = new EduVerseClient({
  apiKey: 'your_api_key'
});

// Get courses
const courses = await client.getCourses();

// Enroll in course
await client.enrollInCourse('course_id');
```

## Testing

### Postman Collection

Import the complete Postman collection for testing all endpoints:

```bash
# Download collection
curl -o eduverse-api-collection.json https://api.eduverse.com/postman-collection

# Import in Postman and use environment variables
```

### Environment Variables for Postman

```json
{
  "base_url": "http://localhost:8000/api/v1",
  "ws_url": "ws://localhost:8000/ws",
  "access_token": "{{your_jwt_token}}"
}
```

## Support

For API support and questions:

- **Documentation**: https://docs.eduverse.com
- **Support Email**: api-support@eduverse.com
- **Community Forum**: https://community.eduverse.com
- **Status Page**: https://status.eduverse.com

## Changelog

### v2.0.0 (Latest)
- Added WebSocket real-time communication
- Enhanced authentication with social login
- Added subscription management
- Improved analytics and insights
- Added VR/AR content support

### v1.5.0
- Added AI-powered recommendations
- Enhanced mobile responsiveness
- Added offline caching
- Improved performance

## License

This API is provided under the EduVerse Platform License. See LICENSE file for details.
