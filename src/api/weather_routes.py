from fastapi import APIRouter, HTTPException, Query, Path, status
from typing import Optional, List
from datetime import datetime

from src.services import WeatherService
from src.models import WeatherResponse, ForecastResponse, ForecastItem
from src.utils import (
    WeatherAPIException,
    NetworkException,
    TimeoutException,
    InvalidResponseException,
    APIKeyException,
    CityNotFoundException,
)


router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current/{city}", response_model=WeatherResponse, summary="Get current weather for a city")
async def get_current_weather(
    city: str = Path(..., description="City name (e.g., 'London', 'New York')", min_length=1)
):
    """
    Get current weather data for a specified city.
    
    **Endpoint**: Uses OpenWeather's `/weather` endpoint
    
    **Parameters**:
    - **city**: City name (required)
    
    **Returns**:
    - Current weather data including temperature, humidity, wind, etc.
    - Indicates if data was retrieved from cache
    
    **Example**: `/weather/current/London`
    """
    try:
        service = WeatherService()
        return await service.get_current_weather(city)
    except CityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except APIKeyException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except TimeoutException as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(e))
    except NetworkException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except InvalidResponseException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except WeatherAPIException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/current/id/{city_id}", response_model=WeatherResponse, summary="Get current weather by city ID")
async def get_current_weather_by_id(
    city_id: int = Path(..., description="OpenWeather city ID", gt=0)
):
    """
    Get current weather data by OpenWeather city ID.
    
    **Endpoint**: Uses OpenWeather's `/weather` endpoint
    
    **Parameters**:
    - **city_id**: OpenWeather city ID (required)
    
    **Returns**:
    - Current weather data for the specified city ID
    
    **Example**: `/weather/current/id/2643743` (London's ID)
    """
    try:
        service = WeatherService()
        return await service.get_weather_by_id(city_id)
    except CityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except APIKeyException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except TimeoutException as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(e))
    except NetworkException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except InvalidResponseException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except WeatherAPIException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/forecast/{city}", response_model=ForecastResponse, summary="Get 5-day forecast for a city")
async def get_forecast(
    city: str = Path(..., description="City name", min_length=1),
    cnt: int = Query(40, description="Number of forecast items (max 40 = 5 days)", ge=1, le=40)
):
    """
    Get 5-day weather forecast for a specified city.
    
    **Endpoint**: Uses OpenWeather's `/forecast` endpoint
    
    **Parameters**:
    - **city**: City name (required)
    - **cnt**: Number of forecast items (optional, default: 40, max: 40)
      - Each item represents 3-hour interval
      - 40 items = 5 days
    
    **Returns**:
    - List of forecast items with weather predictions
    - City information
    - Indicates if data was retrieved from cache
    
    **Example**: `/weather/forecast/London?cnt=16` (2 days of forecast)
    """
    try:
        service = WeatherService()
        return await service.get_forecast(city, cnt)
    except CityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except APIKeyException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except TimeoutException as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(e))
    except NetworkException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except InvalidResponseException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except WeatherAPIException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/forecast/id/{city_id}", response_model=ForecastResponse, summary="Get forecast by city ID")
async def get_forecast_by_id(
    city_id: int = Path(..., description="OpenWeather city ID", gt=0),
    cnt: int = Query(40, description="Number of forecast items (max 40)", ge=1, le=40)
):
    """
    Get 5-day weather forecast by OpenWeather city ID.
    
    **Endpoint**: Uses OpenWeather's `/forecast` endpoint
    
    **Parameters**:
    - **city_id**: OpenWeather city ID (required)
    - **cnt**: Number of forecast items (optional, default: 40)
    
    **Returns**:
    - Forecast data for the specified city ID
    
    **Example**: `/weather/forecast/id/2643743?cnt=24` (3 days for London)
    """
    try:
        service = WeatherService()
        return await service.get_forecast_by_id(city_id, cnt)
    except CityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except APIKeyException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except TimeoutException as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(e))
    except NetworkException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except InvalidResponseException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except WeatherAPIException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/forecast/{city}/filter",
    response_model=List[ForecastItem],
    summary="Get filtered forecast data"
)
async def get_filtered_forecast(
    city: str = Path(..., description="City name", min_length=1),
    weather_condition: Optional[str] = Query(None, description="Filter by weather condition (e.g., 'Rain', 'Clear', 'Clouds')"),
    min_temp: Optional[float] = Query(None, description="Minimum temperature in Celsius"),
    max_temp: Optional[float] = Query(None, description="Maximum temperature in Celsius"),
    min_humidity: Optional[int] = Query(None, description="Minimum humidity percentage", ge=0, le=100),
    max_humidity: Optional[int] = Query(None, description="Maximum humidity percentage", ge=0, le=100),
    cnt: int = Query(40, description="Number of forecast items to fetch", ge=1, le=40)
):
    """
    Get filtered 5-day weather forecast for a city.
    
    **Endpoint**: Uses OpenWeather's `/forecast` endpoint with client-side filtering
    
    **Filters Available**:
    - **weather_condition**: Filter by weather type (Rain, Clear, Clouds, Snow, etc.)
    - **min_temp**: Minimum temperature in Celsius
    - **max_temp**: Maximum temperature in Celsius
    - **min_humidity**: Minimum humidity percentage
    - **max_humidity**: Maximum humidity percentage
    
    **Returns**:
    - Filtered list of forecast items matching all specified criteria
    
    **Examples**:
    - `/weather/forecast/London/filter?weather_condition=Rain`
    - `/weather/forecast/Paris/filter?min_temp=15&max_temp=25`
    - `/weather/forecast/Tokyo/filter?min_humidity=60&weather_condition=Clear`
    """
    try:
        service = WeatherService()
        forecast = await service.get_forecast(city, cnt)
        
        # Apply filters
        filtered_items = forecast.list
        
        if weather_condition:
            filtered_items = [
                item for item in filtered_items
                if item.weather_main.lower() == weather_condition.lower()
            ]
        
        if min_temp is not None:
            filtered_items = [
                item for item in filtered_items
                if item.main.temp >= min_temp
            ]
        
        if max_temp is not None:
            filtered_items = [
                item for item in filtered_items
                if item.main.temp <= max_temp
            ]
        
        if min_humidity is not None:
            filtered_items = [
                item for item in filtered_items
                if item.main.humidity >= min_humidity
            ]
        
        if max_humidity is not None:
            filtered_items = [
                item for item in filtered_items
                if item.main.humidity <= max_humidity
            ]
        
        return filtered_items
    
    except CityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except APIKeyException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except TimeoutException as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(e))
    except NetworkException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except InvalidResponseException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except WeatherAPIException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/cache/clear", summary="Clear all cached data")
async def clear_cache():
    """
    Clear all cached weather data.
    
    **Returns**:
    - Number of cache files deleted
    
    **Example**: `DELETE /weather/cache/clear`
    """
    try:
        service = WeatherService()
        count = service.clear_cache()
        return {"message": f"Successfully cleared {count} cache files", "count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.delete("/cache/clear-expired", summary="Clear expired cache entries")
async def clear_expired_cache():
    """
    Clear only expired cache entries.
    
    **Returns**:
    - Number of expired cache files deleted
    
    **Example**: `DELETE /weather/cache/clear-expired`
    """
    try:
        service = WeatherService()
        count = service.clear_expired_cache()
        return {"message": f"Successfully cleared {count} expired cache files", "count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear expired cache: {str(e)}"
        )
