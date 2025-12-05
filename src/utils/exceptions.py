class WeatherAPIException(Exception):
    """Base exception for weather API errors."""
    pass


class NetworkException(WeatherAPIException):
    """Raised when network connection fails."""
    pass


class TimeoutException(WeatherAPIException):
    """Raised when API request times out."""
    pass


class InvalidResponseException(WeatherAPIException):
    """Raised when API response is invalid or malformed."""
    pass


class APIKeyException(WeatherAPIException):
    """Raised when API key is missing or invalid."""
    pass


class CityNotFoundException(WeatherAPIException):
    """Raised when city is not found."""
    pass
