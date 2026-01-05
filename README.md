# Travel Recommender API

A Django REST API that helps users find the best districts in Bangladesh for travel based on temperature and air quality data. The application fetches real-time weather forecasts and air quality metrics from Open-Meteo API to provide intelligent travel recommendations.

## 🌟 Features

- **Best Districts Ranking**: Find the top 10 coolest and cleanest districts in Bangladesh
- **Travel Recommendations**: Get personalized travel advice based on current location vs. destination
- **Real-time Weather Data**: Fetches 7-day forecasts from Open-Meteo API
- **Air Quality Monitoring**: Tracks PM2.5 levels for health-conscious travel decisions
- **High Performance**: Response times under 500ms with Redis caching
- **Background Tasks**: Automated weather data updates using Celery
- **Comprehensive Testing**: Full test coverage with unit tests
- **CI/CD Pipeline**: GitHub Actions workflow for automated testing and deployment

## 📋 Prerequisites

- Python 3.11+
- Redis 7.0+
- Docker & Docker Compose (optional, for containerized deployment)
- Git

## 🚀 Quick Start

### Option 1: Local Development (Without Docker)

#### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd strativ-assessment
```

#### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables

Create a `.env` file in the project root (use `sample.env` as reference):

```bash
cp sample.env .env
```

Edit `.env` with your configuration:

```env
SECRET_KEY='your-secret-key-here'
DEBUG=True
ALLOWED_HOSTS=*

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/0

# Cache Settings
CACHE_TTL_IN_SECONDS=3600
DISTRICTS_CACHE_TTL_IN_SECONDS=86400
WEATHER_CACHE_TTL_IN_SECONDS=3600

# API URLs
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1
OPEN_METEO_AIR_QUALITY_BASE_URL=https://air-quality-api.open-meteo.com/v1/
DISTRICTS_JSON_URL=https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json

# Other Settings
REQUEST_TIMEOUT_IN_SECONDS=10
PAGINATION_PAGE_SIZE=10
LOG_LEVEL=INFO
```

#### 5. Start Redis Server

```bash
# macOS (using Homebrew)
brew services start redis

# Linux
sudo systemctl start redis

# Or using Docker
docker run -d -p 6379:6379 redis:7-alpine
```

#### 6. Run Migrations

```bash
python manage.py migrate
```

#### 7. Start Development Server

```bash
python manage.py runserver
```

#### 8. (Optional) Start Celery Workers

In separate terminal windows:

```bash
# Terminal 1: Celery Worker
celery -A travel_recommender worker --loglevel=info

# Terminal 2: Celery Beat (for scheduled tasks)
celery -A travel_recommender beat --loglevel=info
```

### Option 2: Docker Deployment

#### 1. Clone and Configure

```bash
git clone <your-repository-url>
cd strativ-assessment
cp sample.env .env
# Edit .env as needed
```

#### 2. Build and Start Services

```bash
docker-compose up --build
```

This will start:
- Django web application (port 8000)
- Redis cache server (port 6379)
- Celery worker
- Celery beat scheduler

#### 3. Access the Application

```bash
# Health check
curl http://localhost:8000/health/

# API endpoints
curl http://localhost:8000/api/best-districts/
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Endpoints

#### 1. Get Best Districts

Returns the top districts ranked by coolest temperature and best air quality.

**Endpoint:** `GET /api/best-districts/`

**Query Parameters:**
- `limit` (optional): Number of districts to return (1-64, default: 10)

**Example Request:**
```bash
curl "http://localhost:8000/api/best-districts/?limit=5"
```

**Example Response:**
```json
{
  "count": 5,
  "results": [
    {
      "district": "Sylhet",
      "avg_temp": 20.5,
      "avg_pm25": 28.3
    },
    {
      "district": "Rangamati",
      "avg_temp": 21.2,
      "avg_pm25": 30.1
    }
  ]
}
```

#### 2. Get Travel Recommendation

Compare current location with destination to get travel advice.

**Endpoint:** `GET /api/recommend/`

**Query Parameters:**
- `current_lat` (required): Current latitude (-90 to 90)
- `current_lon` (required): Current longitude (-180 to 180)
- `destination_name` (required): Destination district name
- `travel_date` (required): Travel date (YYYY-MM-DD, within next 7 days)

**Example Request:**
```bash
curl "http://localhost:8000/api/recommend/?current_lat=23.8103&current_lon=90.4125&destination_name=Sylhet&travel_date=2026-01-10"
```

**Example Response:**
```json
{
  "recommendation": "Recommended",
  "reason": "Your destination is 3.5°C cooler and has significantly better air quality (PM2.5: 28.3 vs 120.5). Enjoy your trip!",
  "travel_date": "2026-01-10",
  "current_location": {
    "temperature": 28.0,
    "pm25": 120.5
  },
  "destination": {
    "name": "Sylhet",
    "temperature": 24.5,
    "pm25": 28.3
  }
}
```

## 🧪 Running Tests

### Run All Tests

```bash
python manage.py test
```

### Run Specific Test Modules

```bash
# Test services
python manage.py test travel.tests.test_services

# Test views
python manage.py test travel.tests.test_views

# Test serializers
python manage.py test travel.tests.test_serializers
```

### Run Tests with Coverage

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report in htmlcov/
```

## 🏗️ Project Structure

```
strativ-assessment/
├── travel/                          # Main application
│   ├── services/                    # Business logic
│   │   ├── best_districts_service.py
│   │   ├── district_service.py
│   │   ├── recommend_service.py
│   │   └── weather_service.py
│   ├── views/                       # API views
│   ├── serializers/                 # Request/response serializers
│   ├── tasks/                       # Celery tasks
│   └── tests/                       # Test modules
├── travel_recommender/              # Project configuration
│   ├── settings.py
│   ├── celery.py
│   ├── middleware/                  # Custom middleware
│   └── services/                    # Shared services
├── docker-compose.yml               # Docker orchestration
├── Dockerfile                       # Docker image definition
├── requirements.txt                 # Python dependencies
├── .github/workflows/ci-cd.yml      # CI/CD pipeline
└── manage.py                        # Django management script
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | False |
| `ALLOWED_HOSTS` | Allowed hosts | localhost,127.0.0.1 |
| `REDIS_HOST` | Redis server host | localhost |
| `REDIS_PORT` | Redis server port | 6379 |
| `CACHE_TTL_IN_SECONDS` | General cache TTL | 3600 |
| `DISTRICTS_CACHE_TTL_IN_SECONDS` | Districts cache TTL | 86400 |
| `WEATHER_CACHE_TTL_IN_SECONDS` | Weather cache TTL | 3600 |
| `OPEN_METEO_BASE_URL` | Weather API base URL | https://api.open-meteo.com/v1 |
| `REQUEST_TIMEOUT_IN_SECONDS` | API request timeout | 10 |

### Celery Tasks

The application includes automated background tasks:

1. **Update Districts**: Refreshes district data daily
   - Task: `travel.tasks.update_districts_task`
   - Schedule: Every 24 hours

2. **Update Weather**: Refreshes weather data periodically
   - Task: `travel.tasks.update_weather_task`
   - Schedule: Every 1 hour

## 🚢 Deployment

### Production Checklist

1. **Set Production Environment Variables**
   ```bash
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com
   SECRET_KEY=<generate-strong-secret-key>
   ```

2. **Configure HTTPS**
   - Use a reverse proxy (nginx/Apache)
   - Enable SSL certificates

3. **Database Migration**
   ```bash
   python manage.py migrate --no-input
   ```

4. **Collect Static Files**
   ```bash
   python manage.py collectstatic --no-input
   ```

5. **Start Services**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 📊 Performance Optimization

- **Redis Caching**: Reduces API calls and improves response times
- **Concurrent Requests**: Thread pool for batch weather fetching
- **Database Indexing**: Optimized queries for district lookups
- **Response Time**: < 500ms for all API endpoints

## 🛠️ Development Tools

### Code Formatting

```bash
pip install black
black .
```

### Linting

```bash
pip install flake8
flake8 . --max-line-length=127
```

### Type Checking

```bash
pip install mypy
mypy travel/
```

## 📝 API Rate Limits

The Open-Meteo API has the following limits:
- 10,000 API calls per day
- No authentication required
- Free for non-commercial use

Our caching strategy minimizes API calls:
- District data: cached for 24 hours
- Weather data: cached for 1 hour
- Concurrent batch requests for better performance

## 🐛 Troubleshooting

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Check Redis logs
docker logs travel_redis
```

### Celery Not Processing Tasks

```bash
# Check Celery worker status
celery -A travel_recommender inspect active

# Restart Celery worker
docker-compose restart celery_worker
```

### API Timeout Errors

- Increase `REQUEST_TIMEOUT_IN_SECONDS` in `.env`
- Check internet connectivity
- Verify Open-Meteo API status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is created as part of a technical assessment for Strativ.

## 👤 Author

[Your Name]
- GitHub: [@your-username]
- Email: your.email@example.com

## 🙏 Acknowledgments

- [Open-Meteo](https://open-meteo.com/) for weather and air quality data
- [Strativ](https://strativ.se/) for the assignment
- Bangladesh district data from Strativ's GitHub repository

---

**Note**: This application is designed for educational and assessment purposes. For production use, implement proper authentication, rate limiting, and monitoring solutions.