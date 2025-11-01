# ETLab Python API# ETLab Python API



Flask REST API for Sahrdaya's ETLab academic portal with Cloudflare bypass support.Flask REST API for Sahrdaya's ETLab academic portal with Cloudflare bypass support.



## 🚀 Quick Start## 🚀 Quick Start



### Local Development### Local Development

```bash```bash

pip install -r requirements.txtpip install -r requirements.txt

python app.pypython app.py

``````

Server runs on `http://localhost:3000`

Server runs on `http://localhost:3000`

### Production (Docker)

```bash### Production (Docker)

docker build -t etlab-api .```bash

docker run -p 3000:10000 etlab-apidocker build -t etlab-api .

```docker run -p 3000:10000 etlab-api

```

## 📡 API Documentation

## 📡 API Documentation

**Complete API documentation with all endpoints, request/response examples, and authentication details:**

**Complete API documentation with all endpoints, request/response examples, and authentication details:**

👉 **[View API_INFO.md](./API_INFO.md)** 👈

👉 **[View API_INFO.md](./API_INFO.md)** 👈

### Quick Reference

### Quick Reference

**Available Endpoints:**

- `POST /api/login` - User authentication**Available Endpoints:**

- `GET /api/profile` - User profile- `POST /api/login` - User authentication

- `GET /api/attendance` - Subject-wise attendance- `GET /api/profile` - User profile

- `GET /api/attendance-table` - Day-by-day attendance with periods- `GET /api/attendance` - Subject-wise attendance

- `GET /api/timetable` - Class timetable- `GET /api/attendance-table` - Day-by-day attendance with periods

- `GET /api/results` - Semester results- `GET /api/timetable` - Class timetable

- `GET /api/end-semester-results` - End semester results- `GET /api/results` - Semester results

- `GET /api/status` - Student status- `GET /api/end-semester-results` - End semester results

- `POST /api/logout` - Logout- `GET /api/status` - Student status

- `GET /health` - Health check- `POST /api/logout` - Logout

- `GET /` - API information- `GET /health` - Health check

- `GET /` - API information

## 🔐 Authentication

## 🔐 Authentication

1. Login with credentials:

```bash1. Login with credentials:

curl -X POST http://localhost:3000/api/login \```bash

  -H "Content-Type: application/json" \curl -X POST http://localhost:3000/api/login \

  -d '{"username":"your_username","password":"your_password"}'  -H "Content-Type: application/json" \

```  -d '{"username":"your_username","password":"your_password"}'

```

2. Use the returned token in subsequent requests:

```bash2. Use the returned token in subsequent requests:

curl http://localhost:3000/api/profile \```bash

  -H "Authorization: Bearer YOUR_TOKEN_HERE"curl http://localhost:3000/api/profile \

```  -H "Authorization: Bearer YOUR_TOKEN_HERE"

```

## 📦 Project Structure  "summary": {"total_periods": 100, "present": 85, "absent": 15, "percentage": 85.0}

}

``````

app/

├── config/          # Configuration files### 4. Timetable

├── controllers/     # API route handlers`GET /api/timetable`

├── models/          # Data models & DTOs

├── services/        # Business logicHeaders: `Authorization: Bearer {token}`

├── parsers/         # HTML/CSV parsing```json

└── utils/           # Helper utilitiesResponse: {

```  "schedule": {

    "Monday": [

## 🔧 Environment Variables      {

        "period": 1,

```env        "subject": "CST302 - Compiler Design [T] VINU V",

BASE_URL=https://etlab.kem.edu.in/ktuacademics        "code": "CST302",

PORT=3000        "name": "Compiler Design",

FLASK_ENV=production        "type": "T",

CORS_ALLOWED_ORIGINS=*        "teacher": "VINU V"

```      }

    ]

## 🐳 Docker Deployment  },

  "total_periods": 35

### Build}

```bash```

docker build -t etlab-api .

```### 5. Profile

`GET /api/profile`

### Run

```bashHeaders: `Authorization: Bearer {token}`

docker run -p 3000:10000 \```json

  -e BASE_URL=https://etlab.kem.edu.in/ktuacademics \Response: {

  -e PORT=10000 \  "success": true,

  etlab-api  "profile": {"name": "Student Name", "roll_number": "TVE20CS001"}

```}

```

## ☁️ Deploy to Render

### 6. Internal Results

1. Push code to GitHub`GET /api/results?semester=5`

2. Create new Web Service on Render

3. Select **Docker** environmentHeaders: `Authorization: Bearer {token}`

4. Set environment variables:```json

   - `PORT=10000`Response: {

   - `FLASK_ENV=production`  "results": [

5. Deploy!    {"subject": "Computer Networks", "type": "Series Test 1", "max_marks": 50, "marks": 45}

  ],

## 🛠️ Tech Stack  "semester": "5"

}

- **Flask 3.0** - Web framework```

- **Gunicorn** - WSGI server (production)

- **CloudScraper** - Cloudflare bypass### 7. End Semester Results

- **BeautifulSoup4** - HTML parsing`GET /api/end-semester-results`

- **HTTPX** - HTTP/2 support

Headers: `Authorization: Bearer {token}`

## 📝 Logging```json

Response: {

The API uses minimal logging:  "exams": [

- ✅ Shows successful logins: `User: username logged in`    {

- ❌ Shows only critical errors: `ERROR: Cloudflare bypass failed`      "exam_name": "Fifth Semester B.Tech Degree Examination December 2024",

- 🔇 Suppresses all INFO/DEBUG logs      "degree": "BTech KTU",

      "semester": "Fifth Semester",

## ✨ Features      "month": "December",

      "year": "2024",

- ✅ **Cloudflare Bypass** - Automatic handling of Cloudflare protection      "subjects": [

- ✅ **Session Management** - Token-based authentication        {"code": "CST301", "name": "Theory of Computation", "grade": "A+", "credit": 3}

- ✅ **CORS Support** - Cross-origin requests enabled      ],

- ✅ **Error Handling** - Comprehensive error responses      "sgpa": 9.53,

- ✅ **Production Ready** - Optimized for deployment      "cgpa": 7.36,

- ✅ **Docker Support** - Containerized deployment      "earned_credit": 22

- ✅ **Health Checks** - Monitoring endpoints    }

  ]

## 📄 License}

```

MIT License

### 8. Status

## 🤝 Contributing`GET /api/status`

```json

Contributions welcome! Please open an issue or submit a pull request.Response: {"status": "running", "version": "1.0.0"}

```

---

### 9. Logout

**For complete API documentation with request/response examples, see [API_INFO.md](./API_INFO.md)**`GET /api/logout`

```json
Response: {"message": "Logout successful"}
```

## Environment Variables

Create `.env` file (optional):
```env
BASE_URL=https://sahrdaya.etlab.in
COOKIE_KEY=_identity
CLOUDFLARE_BYPASS_ENABLED=true
```

## Tech Stack

- Flask 2.3.x
- BeautifulSoup4 (HTML parsing)
- cloudscraper (Cloudflare bypass)
- requests

## Docker

```bash
docker-compose up
```

## Notes

- Only ERROR level logs shown for production
- Cloudflare bypass uses multiple strategies (cloudscraper, httpx, selenium)
- Session tokens expire - handle 401 responses
- Educational use only
