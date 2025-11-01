# 📡 ETLab Python API - Complete Reference

## Base URL
```
Production: https://your-app.onrender.com
Local: http://localhost:3000
```

---

## 🔐 Authentication Endpoints

### 1. Login
Authenticate user and get session token.

**Endpoint:** `POST /api/login`

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Login successful",
    "token": "SESSION_COOKIE_TOKEN_HERE"
  }
}
```

**Error Response (401):**
```json
{
  "success": false,
  "error": {
    "message": "Invalid username or password",
    "code": "LOGIN_FAILED"
  }
}
```

---

### 2. Logout
End user session.

**Endpoint:** `POST /api/logout`

**Headers:**
```
Authorization: Bearer YOUR_TOKEN_HERE
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  }
}
```

---

## 👤 Profile Endpoint

### Get User Profile
Retrieve student profile information.

**Endpoint:** `GET /api/profile`

**Headers:**
```
Authorization: Bearer YOUR_TOKEN_HERE
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "name": "John Doe",
    "admission_number": "KTU12345",
    "branch": "Computer Science",
    "semester": "S6",
    "email": "john@example.com",
    "phone": "1234567890"
  }
}
```

**Error Response (401):**
```json
{
  "success": false,
  "error": {
    "message": "Authorization token is required",
    "code": "UNAUTHORIZED"
  }
}
```

---

## 📊 Attendance Endpoints

### 1. Subject-wise Attendance
Get attendance percentage for each subject.

**Endpoint:** `GET /api/attendance`

**Headers:**
```
Authorization: Bearer YOUR_TOKEN_HERE
```

**Query Parameters:**
- `semester` (optional): Semester number (default: 3)

**Example Request:**
```
GET /api/attendance?semester=6
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "semester": "6",
    "subjects": [
      {
        "code": "CS301",
        "name": "Data Structures",
        "total_classes": 45,
        "attended": 40,
        "percentage": 88.89,
        "status": "satisfactory"
      },
      {
        "code": "CS302",
        "name": "Algorithm Design",
        "total_classes": 50,
        "attended": 48,
        "percentage": 96.0,
        "status": "excellent"
      }
    ],
    "overall_percentage": 92.44
  }
}
```

---

### 2. Day-by-Day Attendance Table
Get detailed attendance with period-wise breakdown.

**Endpoint:** `GET /api/attendance-table`

**Headers:**
```
Authorization: Bearer YOUR_TOKEN_HERE
```

**Query Parameters:**
- `semester` (optional): Semester number (default: 3)
- `month` (optional): Month name or number (default: current month)
  - Examples: "Oct", "October", "10"
- `year` (optional): Year (default: current year)

**Example Request:**
```
GET /api/attendance-table?semester=6&month=Oct&year=2025
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "semester": "6",
    "month": "10",
    "month_requested": "Oct",
    "year": "2025",
    "dates": [
      {
        "date": "1st Oct",
        "periods": [
          {
            "period": 1,
            "status": "present",
            "subject": "CS301"
          },
          {
            "period": 2,
            "status": "absent",
            "subject": "CS302"
          },
          {
            "period": 3,
            "status": "no_class",
            "subject": ""
          }
        ]
      }
    ],
    "summary": {
      "total_periods": 150,
      "present": 135,
      "absent": 10,
      "no_class": 5,
      "percentage": 93.1
    }
  }
}
```

**Period Status Values:**
- `"present"` - Student was present
- `"absent"` - Student was absent
- `"no_class"` - No class scheduled

---

## 📅 Timetable Endpoint

### Get Class Timetable
Retrieve weekly class schedule.

**Endpoint:** `GET /api/timetable`

**Headers:**
```
Authorization: Bearer YOUR_TOKEN_HERE
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Timetable retrieved successfully",
    "schedule": {
      "Monday": [
        {
          "time": "9:00 AM - 10:00 AM",
          "subject_code": "CS301",
          "subject_name": "Data Structures",
          "teacher": "Dr. Smith",
          "room": "Lab 101"
        }
      ],
      "Tuesday": [],
      "Wednesday": [],
      "Thursday": [],
      "Friday": [],
      "Saturday": []
    },
    "total_periods": 30,
    "total_days": 6
  }
}
```

---

## 📝 Results Endpoints

### 1. Semester Results
Get exam results for a semester.

**Endpoint:** `GET /api/results`

**Headers:**
```
Authorization: Bearer YOUR_TOKEN_HERE
```

**Query Parameters:**
- `semester` (optional): Semester number

**Example Request:**
```
GET /api/results?semester=5
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "semester": "5",
    "results": [
      {
        "subject_code": "CS301",
        "subject_name": "Data Structures",
        "internal_marks": 18,
        "external_marks": 75,
        "total": 93,
        "grade": "A+",
        "credits": 4,
        "status": "PASS"
      }
    ],
    "sgpa": 9.2,
    "cgpa": 8.8
  }
}
```

---

### 2. End Semester Results
Get end semester examination results.

**Endpoint:** `GET /api/end-semester-results`

**Headers:**
```
Authorization: Bearer YOUR_TOKEN_HERE
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "exam_name": "End Semester Examination - Nov 2025",
    "semester": "6",
    "results": [
      {
        "subject_code": "CS301",
        "subject_name": "Data Structures",
        "grade": "A+",
        "credits": 4
      }
    ],
    "sgpa": 9.2,
    "result": "PASS"
  }
}
```

---

## 📋 Status Endpoint

### Get Student Status
Check current academic status.

**Endpoint:** `GET /api/status`

**Headers:**
```
Authorization: Bearer YOUR_TOKEN_HERE
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "status": "Active",
    "semester": "6",
    "academic_year": "2024-2025",
    "attendance_percentage": 92.5,
    "cgpa": 8.8,
    "backlogs": 0
  }
}
```

---

## ❤️ Health Check

### System Health
Check if API is running.

**Endpoint:** `GET /health`

**No Authentication Required**

**Success Response (200):**
```json
{
  "status": "healthy",
  "message": "ETLabsHR Python API is running"
}
```

---

## 🏠 Root Endpoint

### API Information
Get API metadata and available endpoints.

**Endpoint:** `GET /`

**No Authentication Required**

**Success Response (200):**
```json
{
  "name": "ETLabsHR Python API",
  "version": "2.0.0",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "login": "/api/login",
    "profile": "/api/profile",
    "attendance": "/api/attendance",
    "attendance_table": "/api/attendance-table",
    "timetable": "/api/timetable",
    "results": "/api/results",
    "status": "/api/status",
    "logout": "/api/logout"
  }
}
```

---

## 🔒 Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer YOUR_TOKEN_HERE
```

**How to get a token:**
1. Call `POST /api/login` with username and password
2. Extract the `token` from the response
3. Use this token in the `Authorization` header for subsequent requests

**Token expiration:**
- Tokens expire after the session ends on the ETLab server
- If you receive a 401 error, login again to get a fresh token

---

## ❌ Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": {
    "message": "Description of the error",
    "code": "ERROR_CODE"
  }
}
```

**Common Error Codes:**
- `UNAUTHORIZED` - Missing or invalid authentication token
- `INVALID_CREDENTIALS` - Wrong username/password
- `LOGIN_FAILED` - Login unsuccessful
- `TOKEN_EXPIRED` - Session expired, login again
- `SERVER_ERROR` - Internal server error
- `VALIDATION_ERROR` - Invalid request data

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

---

## 📦 Response Structure

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE"
  }
}
```

---

## 🧪 Testing

**Example cURL request:**
```bash
# Login
curl -X POST https://your-app.onrender.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'

# Get Profile (with token)
curl https://your-app.onrender.com/api/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Example JavaScript fetch:**
```javascript
// Login
const response = await fetch('https://your-app.onrender.com/api/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'user', password: 'pass' })
});
const data = await response.json();
const token = data.data.token;

// Get Profile
const profile = await fetch('https://your-app.onrender.com/api/profile', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const profileData = await profile.json();
```

---

## 🌐 CORS

The API supports Cross-Origin Resource Sharing (CORS). Configure allowed origins in environment variables:

```
CORS_ALLOWED_ORIGINS=*
CORS_ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_CREDENTIALS=true
```

---

## 📞 Support

For issues or questions, check:
- `/health` endpoint for API status
- `/` endpoint for available endpoints
- Server logs for detailed error messages

---

**Last Updated:** November 2025  
**API Version:** 2.0.0
