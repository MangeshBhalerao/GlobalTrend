from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CoordinateData(BaseModel):
    """Geographic coordinates."""
    lon: float = Field(..., description="Longitude")
    lat: float = Field(..., description="Latitude")


class WeatherDescription(BaseModel):
    """Weather condition description."""
    id: int = Field(..., description="Weather condition id")
    main: str = Field(..., description="Group of weather parameters (Rain, Snow, Extreme etc.)")
    description: str = Field(..., description="Weather condition within the group")
    icon: str = Field(..., description="Weather icon id")


class MainData(BaseModel):
    """Main weather parameters."""
    temp: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Feels like temperature in Celsius")
    temp_min: float = Field(..., description="Minimum temperature")
    temp_max: float = Field(..., description="Maximum temperature")
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    humidity: int = Field(..., description="Humidity in %")
    sea_level: Optional[int] = Field(None, description="Atmospheric pressure on sea level")
    grnd_level: Optional[int] = Field(None, description="Atmospheric pressure on ground level")


class WindData(BaseModel):
    """Wind information."""
    speed: float = Field(..., description="Wind speed in meter/sec")
    deg: int = Field(..., description="Wind direction in degrees")
    gust: Optional[float] = Field(None, description="Wind gust in meter/sec")


class CloudsData(BaseModel):
    """Cloudiness information."""
    all: int = Field(..., description="Cloudiness in %")


class WeatherItem(BaseModel):
    """Complete weather data for a single location."""
    coord: CoordinateData
    weather: List[WeatherDescription]
    base: str = Field(..., description="Internal parameter")
    main: MainData
    visibility: int = Field(..., description="Visibility in meters")
    wind: WindData
    clouds: CloudsData
    dt: int = Field(..., description="Time of data calculation, unix, UTC")
    timezone: int = Field(..., description="Shift in seconds from UTC")
    id: int = Field(..., description="City ID")
    name: str = Field(..., description="City name")
    cod: int = Field(..., description="Internal parameter")
    
    @property
    def datetime(self) -> datetime:
        """Convert unix timestamp to datetime."""
        return datetime.fromtimestamp(self.dt)
    
    @property
    def temp_celsius(self) -> float:
        """Temperature in Celsius (already in Celsius from API when units=metric)."""
        return self.main.temp
    
    @property
    def weather_main(self) -> str:
        """Primary weather condition."""
        return self.weather[0].main if self.weather else "Unknown"


class ForecastItem(BaseModel):
    """Single forecast entry."""
    dt: int = Field(..., description="Time of forecasted data, unix, UTC")
    main: MainData
    weather: List[WeatherDescription]
    clouds: CloudsData
    wind: WindData
    visibility: int = Field(..., description="Visibility in meters")
    pop: float = Field(..., description="Probability of precipitation")
    dt_txt: str = Field(..., description="Time of data forecasted, ISO format")
    
    @property
    def datetime(self) -> datetime:
        """Convert unix timestamp to datetime."""
        return datetime.fromtimestamp(self.dt)
    
    @property
    def weather_main(self) -> str:
        """Primary weather condition."""
        return self.weather[0].main if self.weather else "Unknown"


class CityData(BaseModel):
    """City information in forecast response."""
    id: int = Field(..., description="City ID")
    name: str = Field(..., description="City name")
    coord: CoordinateData
    country: str = Field(..., description="Country code")
    population: int = Field(0, description="City population")
    timezone: int = Field(..., description="Shift in seconds from UTC")
    sunrise: int = Field(..., description="Sunrise time, unix, UTC")
    sunset: int = Field(..., description="Sunset time, unix, UTC")


class WeatherResponse(BaseModel):
    """Response model for current weather data."""
    data: WeatherItem
    cached: bool = Field(False, description="Whether data was retrieved from cache")
    cached_at: Optional[datetime] = Field(None, description="When the data was cached")


class ForecastResponse(BaseModel):
    """Response model for forecast data."""
    cod: str = Field(..., description="Internal parameter")
    message: int = Field(..., description="Internal parameter")
    cnt: int = Field(..., description="Number of forecast items")
    list: List[ForecastItem] = Field(..., description="List of forecast items")
    city: CityData
    cached: bool = Field(False, description="Whether data was retrieved from cache")
    cached_at: Optional[datetime] = Field(None, description="When the data was cached")
