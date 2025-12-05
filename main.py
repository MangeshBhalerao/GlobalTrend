from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import weather_router
from src.config import settings

# Create FastAPI app
app = FastAPI(
    title="GlobalTrend Weather API",
    description="A professional weather API using OpenWeather with caching and filtering capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(weather_router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "message": "Welcome to GlobalTrend Weather API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "current_weather": "/weather/current/{city}",
            "current_weather_by_id": "/weather/current/id/{city_id}",
            "forecast": "/weather/forecast/{city}",
            "forecast_by_id": "/weather/forecast/id/{city_id}",
            "filtered_forecast": "/weather/forecast/{city}/filter"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "api_configured": bool(settings.openweather_api_key),
        "cache_enabled": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
