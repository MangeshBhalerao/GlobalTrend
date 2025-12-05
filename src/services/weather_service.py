import httpx
from typing import Optional, Dict, Any
from datetime import datetime

from src.config import settings
from src.models import WeatherResponse, ForecastResponse, WeatherItem
from src.utils import (
    CacheManager,
    NetworkException,
    TimeoutException,
    InvalidResponseException,
    APIKeyException,
    CityNotFoundException,
)


class WeatherService:
    """Service for fetching weather data from OpenWeather API."""
    
    def __init__(self):
        """Initialize weather service."""
        self.base_url = settings.openweather_base_url
        self.api_key = settings.openweather_api_key
        self.timeout = settings.api_timeout
        self.cache = CacheManager()
        
        if not self.api_key:
            raise APIKeyException(
                "OpenWeather API key is not configured. "
                "Please set OPENWEATHER_API_KEY in .env file"
            )
    
    def _build_url(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Build API URL with parameters."""
        params['appid'] = self.api_key
        params['units'] = 'metric'  # Use metric units for temperature in Celsius
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}/{endpoint}?{query_string}"
    
    async def _fetch_data(self, endpoint: str, params: Dict[str, Any], cache_key: str) -> Dict[str, Any]:
        """
        Fetch data from API with caching and error handling.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            cache_key: Key for caching
            
        Returns:
            API response data
            
        Raises:
            NetworkException: On network failures
            TimeoutException: On request timeout
            InvalidResponseException: On invalid response
            CityNotFoundException: On 404 city not found
        """
        # Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # Build URL
        url = self._build_url(endpoint, params)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=self.timeout)
                
                # Handle different HTTP status codes
                if response.status_code == 404:
                    raise CityNotFoundException(f"City not found: {params.get('q', params.get('id', 'unknown'))}")
                elif response.status_code == 401:
                    raise APIKeyException("Invalid API key")
                elif response.status_code != 200:
                    raise InvalidResponseException(
                        f"API returned status code {response.status_code}: {response.text}"
                    )
                
                # Parse JSON response
                try:
                    data = response.json()
                except Exception as e:
                    raise InvalidResponseException(f"Failed to parse JSON response: {e}")
                
                # Cache the successful response
                self.cache.set(cache_key, data)
                
                return {
                    'data': data,
                    'cached': False,
                    'cached_at': None
                }
        
        except httpx.TimeoutException as e:
            raise TimeoutException(f"Request timeout after {self.timeout} seconds: {e}")
        except httpx.NetworkError as e:
            raise NetworkException(f"Network error occurred: {e}")
        except httpx.HTTPError as e:
            raise NetworkException(f"HTTP error occurred: {e}")
    
    async def get_current_weather(self, city: str) -> WeatherResponse:
        """
        Get current weather for a city.
        
        Args:
            city: City name (e.g., "London", "New York")
            
        Returns:
            WeatherResponse with current weather data
        """
        cache_key = f"weather_{city}"
        params = {'q': city}
        
        result = await self._fetch_data('weather', params, cache_key)
        
        return WeatherResponse(
            data=WeatherItem(**result['data']),
            cached=result['cached'],
            cached_at=result['cached_at']
        )
    
    async def get_weather_by_id(self, city_id: int) -> WeatherResponse:
        """
        Get current weather by city ID.
        
        Args:
            city_id: OpenWeather city ID
            
        Returns:
            WeatherResponse with current weather data
        """
        cache_key = f"weather_id_{city_id}"
        params = {'id': city_id}
        
        result = await self._fetch_data('weather', params, cache_key)
        
        return WeatherResponse(
            data=WeatherItem(**result['data']),
            cached=result['cached'],
            cached_at=result['cached_at']
        )
    
    async def get_forecast(self, city: str, cnt: int = 40) -> ForecastResponse:
        """
        Get 5-day weather forecast for a city.
        
        Args:
            city: City name
            cnt: Number of forecast items (max 40, default 40 = 5 days)
            
        Returns:
            ForecastResponse with forecast data
        """
        cache_key = f"forecast_{city}_{cnt}"
        params = {'q': city, 'cnt': cnt}
        
        result = await self._fetch_data('forecast', params, cache_key)
        
        # Add cached metadata to the response
        forecast_data = result['data']
        forecast_data['cached'] = result['cached']
        forecast_data['cached_at'] = result['cached_at']
        
        return ForecastResponse(**forecast_data)
    
    async def get_forecast_by_id(self, city_id: int, cnt: int = 40) -> ForecastResponse:
        """
        Get 5-day weather forecast by city ID.
        
        Args:
            city_id: OpenWeather city ID
            cnt: Number of forecast items (max 40)
            
        Returns:
            ForecastResponse with forecast data
        """
        cache_key = f"forecast_id_{city_id}_{cnt}"
        params = {'id': city_id, 'cnt': cnt}
        
        result = await self._fetch_data('forecast', params, cache_key)
        
        # Add cached metadata to the response
        forecast_data = result['data']
        forecast_data['cached'] = result['cached']
        forecast_data['cached_at'] = result['cached_at']
        
        return ForecastResponse(**forecast_data)
    
    def clear_cache(self) -> int:
        """Clear all cached data."""
        return self.cache.clear()
    
    def clear_expired_cache(self) -> int:
        """Clear expired cache entries."""
        return self.cache.clear_expired()
