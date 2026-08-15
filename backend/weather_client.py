import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherClient:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    async def get_current_weather(self, lat: float, lng: float) -> dict:
        """
        Fetches current wind speed (mph), wind direction (degrees), humidity (%),
        and temperature (F) from the Open-Meteo weather API asynchronously.
        """
        params = {
            "latitude": lat,
            "longitude": lng,
            "current": "wind_speed_10m,wind_direction_10m,relative_humidity_2m,temperature_2m",
            "wind_speed_unit": "mph",
            "temperature_unit": "fahrenheit",
            "timezone": "auto"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                return {
                    "success": True,
                    "wind_speed": current.get("wind_speed_10m", 0.0),
                    "wind_direction": current.get("wind_direction_10m", 0),
                    "humidity": current.get("relative_humidity_2m", 50.0),
                    "temperature": current.get("temperature_2m", 70.0),
                    "timestamp": current.get("time"),
                    "source": "Open-Meteo"
                }
            else:
                logger.error(f"Weather API error {response.status_code}: {response.text}")
                return {
                    "success": False,
                    "message": f"API error {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Failed to fetch weather: {e}")
            return {
                "success": False,
                "message": str(e)
            }
