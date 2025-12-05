
## 📋 Requirements
- Python 3.8+
- OpenWeather API Key (free tier available at [openweathermap.org](https://openweathermap.org/api))

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd GlobalTrend
```

### 2. Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenWeather API key:

```env
OPENWEATHER_API_KEY=your_actual_api_key_here
OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5
CACHE_DIR=cache
CACHE_EXPIRY_SECONDS=300
API_TIMEOUT=10
```

**Get your free API key**: Sign up at [OpenWeather](https://home.openweathermap.org/users/sign_up)

### 5. Run the Application

```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📚 API Endpoints

### OpenWeather Endpoints Used

This application uses **two OpenWeather API endpoints**:

1. **Current Weather** (`/weather`): Real-time weather data
2. **5-Day Forecast** (`/forecast`): Weather predictions in 3-hour intervals

### Available API Routes

#### 1. Get Current Weather by City Name
```
GET /weather/current/{city}
```

**Example:**
```bash
curl http://localhost:8000/weather/current/London
```

**Response:**
```json
{
  "data": {
    "coord": {"lon": -0.1257, "lat": 51.5085},
    "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
    "main": {
      "temp": 15.5,
      "feels_like": 14.8,
      "temp_min": 13.2,
      "temp_max": 17.1,
      "pressure": 1013,
      "humidity": 72
    },
    "wind": {"speed": 3.5, "deg": 210},
    "name": "London"
  },
  "cached": false,
  "cached_at": null
}
```

#### 2. Get Current Weather by City ID
```
GET /weather/current/id/{city_id}
```

**Example:**
```bash
curl http://localhost:8000/weather/current/id/2643743
```

#### 3. Get 5-Day Forecast
```
GET /weather/forecast/{city}?cnt=40
```

**Parameters:**
- `cnt`: Number of forecast items (1-40, default: 40)
  - Each item = 3-hour interval
  - 40 items = 5 days

**Example:**
```bash
curl "http://localhost:8000/weather/forecast/Paris?cnt=16"
```

#### 4. Get Forecast by City ID
```
GET /weather/forecast/id/{city_id}?cnt=40
```

**Example:**
```bash
curl "http://localhost:8000/weather/forecast/id/2988507?cnt=24"
```

#### 5. Get Filtered Forecast (Advanced)
```
GET /weather/forecast/{city}/filter
```

**Filter Parameters:**
- `weather_condition`: Filter by weather type (Rain, Clear, Clouds, Snow, etc.)
- `min_temp`: Minimum temperature in Celsius
- `max_temp`: Maximum temperature in Celsius
- `min_humidity`: Minimum humidity (0-100)
- `max_humidity`: Maximum humidity (0-100)
- `cnt`: Number of items to fetch before filtering

**Examples:**
```bash
# Get only rainy forecasts
curl "http://localhost:8000/weather/forecast/London/filter?weather_condition=Rain"

# Get forecasts with temperature between 15-25°C
curl "http://localhost:8000/weather/forecast/Tokyo/filter?min_temp=15&max_temp=25"

# Get clear weather with low humidity
curl "http://localhost:8000/weather/forecast/Dubai/filter?weather_condition=Clear&max_humidity=60"
```

#### 6. Clear All Cache
```
DELETE /weather/cache/clear
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/weather/cache/clear
```

#### 7. Clear Expired Cache
```
DELETE /weather/cache/clear-expired
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/weather/cache/clear-expired
```

#### 8. Health Check
```
GET /health
```

## 🗂️ Project Structure

```
GlobalTrend/
├── src/
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   └── weather_routes.py  # Weather endpoints
│   ├── config/                 # Configuration
│   │   ├── __init__.py
│   │   └── settings.py        # Settings with Pydantic
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   └── weather_models.py  # Pydantic models
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   └── weather_service.py # OpenWeather API client
│   ├── utils/                  # Utilities
│   │   ├── __init__.py
│   │   ├── cache_manager.py   # Caching system
│   │   └── exceptions.py      # Custom exceptions
│   └── __init__.py
├── cache/                      # Cache storage (auto-created)
├── venv/                       # Virtual environment
├── .env                        # Environment variables (create this)
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🎯 Filters Implementation

The application provides powerful filtering capabilities on forecast data:

### Temperature Filters
- **min_temp**: Only show forecasts with temperature >= specified value
- **max_temp**: Only show forecasts with temperature <= specified value

### Humidity Filters
- **min_humidity**: Only show forecasts with humidity >= specified value
- **max_humidity**: Only show forecasts with humidity <= specified value

### Weather Condition Filter
- **weather_condition**: Only show forecasts matching specific weather (e.g., "Rain", "Clear", "Clouds")

**All filters can be combined** for precise results.

## 🔧 Error Handling

The application handles various error scenarios:

### Network Errors
- **NetworkException**: Connection failures
- **TimeoutException**: Request timeouts (configurable in `.env`)

### API Errors
- **APIKeyException**: Missing or invalid API key
- **CityNotFoundException**: City not found (404)
- **InvalidResponseException**: Malformed API responses

### Response Codes
- `200`: Success
- `401`: Invalid API key
- `404`: City not found
- `502`: Invalid API response
- `503`: Service unavailable (network error)
- `504`: Gateway timeout

## 💾 Caching System

### How It Works
- API responses are cached as JSON files in `cache/` directory
- Cache keys are based on request parameters
- Default expiry: 300 seconds (5 minutes)

### Configuration
Edit `.env` to customize:
```env
CACHE_DIR=cache
CACHE_EXPIRY_SECONDS=300
```

### Cache Management
- **Automatic**: Expired cache is ignored on read
- **Manual**: Use DELETE endpoints to clear cache
- **Storage**: JSON files for easy inspection

## 🧪 Testing the API

### Using Interactive Docs
Visit http://localhost:8000/docs for a web interface to test all endpoints.

### Using CLI (Bonus Feature!)

The project includes a beautiful CLI interface:

```bash
# Get current weather
python cli.py current London

# Get 3-day forecast
python cli.py forecast Paris

# Get 5-day forecast
python cli.py forecast Tokyo 5
```

### Using cURL

```bash
# Current weather
curl http://localhost:8000/weather/current/London

# Forecast with filtering
curl "http://localhost:8000/weather/forecast/Paris/filter?min_temp=10&max_temp=20"

# Clear cache
curl -X DELETE http://localhost:8000/weather/cache/clear
```

### Using Python

```python
import requests

# Get current weather
response = requests.get("http://localhost:8000/weather/current/London")
print(response.json())

# Get filtered forecast
response = requests.get(
    "http://localhost:8000/weather/forecast/Tokyo/filter",
    params={"weather_condition": "Clear", "min_temp": 15}
)
print(response.json())
```

## 📝 Assumptions & Notes

### API Key
- You need a valid OpenWeather API key
- Free tier includes 1,000 calls/day

### Cache Behavior
- Cache is stored locally in JSON files
- Cached responses include `cached: true` and `cached_at` timestamp
- Cache survives application restarts
- Cache directory is created automatically

### City Identification
- Cities can be identified by name or OpenWeather city ID
- City names are case-insensitive
- For better accuracy, use city IDs from [OpenWeather city list](https://bulk.openweathermap.org/sample/)


## 📦 Dependencies

- **FastAPI**: Modern, fast web framework
- **Uvicorn**: ASGI server for production
- **Pydantic**: Data validation using Python type hints
- **HTTPx**: Async HTTP client for API calls
- **Python-dotenv**: Environment variable management

