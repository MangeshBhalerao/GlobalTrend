"""
CLI interface for GlobalTrend Weather API
Run this to interact with the weather API from command line.
"""

import asyncio
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from src.services import WeatherService
from src.utils import WeatherAPIException

console = Console()


async def show_current_weather(city: str):
    """Display current weather for a city."""
    try:
        service = WeatherService()
        weather = await service.get_current_weather(city)
        
        # Create a nice table
        table = Table(title=f"Current Weather - {weather.data.name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Temperature", f"{weather.data.main.temp}°C")
        table.add_row("Feels Like", f"{weather.data.main.feels_like}°C")
        table.add_row("Condition", weather.data.weather_main)
        table.add_row("Description", weather.data.weather[0].description)
        table.add_row("Humidity", f"{weather.data.main.humidity}%")
        table.add_row("Pressure", f"{weather.data.main.pressure} hPa")
        table.add_row("Wind Speed", f"{weather.data.wind.speed} m/s")
        table.add_row("Visibility", f"{weather.data.visibility} m")
        
        if weather.cached:
            table.add_row("📦 Cached", f"Yes (at {weather.cached_at})")
        else:
            table.add_row("📦 Cached", "No (Fresh data)")
        
        console.print(table)
        
    except WeatherAPIException as e:
        console.print(f"[red]Error: {e}[/red]")


async def show_forecast(city: str, days: int = 3):
    """Display forecast for a city."""
    try:
        service = WeatherService()
        cnt = days * 8  # 8 items per day (3-hour intervals)
        forecast = await service.get_forecast(city, cnt)
        
        table = Table(title=f"{days}-Day Forecast - {forecast.city.name}")
        table.add_column("Date/Time", style="cyan")
        table.add_column("Temp (°C)", style="yellow")
        table.add_column("Condition", style="green")
        table.add_column("Humidity", style="blue")
        table.add_column("Rain %", style="magenta")
        
        for item in forecast.list[:cnt]:
            table.add_row(
                item.dt_txt,
                f"{item.main.temp}°C",
                item.weather_main,
                f"{item.main.humidity}%",
                f"{int(item.pop * 100)}%"
            )
        
        console.print(table)
        
    except WeatherAPIException as e:
        console.print(f"[red]Error: {e}[/red]")


async def main():
    """Main CLI interface."""
    console.print(Panel.fit(
        "[bold cyan]🌤️  GlobalTrend Weather CLI[/bold cyan]\n"
        "Powered by OpenWeather API",
        border_style="blue"
    ))
    
    if len(sys.argv) < 2:
        console.print("\n[yellow]Usage:[/yellow]")
        console.print("  python cli.py current <city>")
        console.print("  python cli.py forecast <city> [days]")
        console.print("\n[yellow]Examples:[/yellow]")
        console.print("  python cli.py current London")
        console.print("  python cli.py forecast Paris 5")
        return
    
    command = sys.argv[1].lower()
    
    if command == "current":
        if len(sys.argv) < 3:
            console.print("[red]Error: Please specify a city name[/red]")
            return
        city = " ".join(sys.argv[2:])
        await show_current_weather(city)
    
    elif command == "forecast":
        if len(sys.argv) < 3:
            console.print("[red]Error: Please specify a city name[/red]")
            return
        
        city = sys.argv[2]
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        
        if days > 5:
            console.print("[yellow]Note: Maximum 5 days available, showing 5 days[/yellow]")
            days = 5
        
        await show_forecast(city, days)
    
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print("[yellow]Available commands: current, forecast[/yellow]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
