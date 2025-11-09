import requests
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

class WeatherService(QObject):
    """
    Handles all weather data fetching from OpenWeatherMap using
    the free-tier /weather and /forecast APIs.
    """
    
    weather_data_ready = pyqtSignal(dict)
    weather_error = pyqtSignal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self.update_weather)
        
        self.api_key = self.config['api_keys']['openweathermap']
        self.lat = self.config['location']['latitude']
        self.lon = self.config['location']['longitude']
        self.units = self.config['display']['units']
        
        # 900000 milliseconds = 15 minutes
        self.update_interval = self.config['display'].get('weather_refresh_ms', 900000)

    def start(self):
        """Starts the weather service timer."""
        print("WeatherService started. Fetching initial data...")
        self.update_weather() # Fetch immediately on start
        self.weather_timer.start(self.update_interval)

    def update_weather(self):
        """
        Fetches the current weather and forecast from OpenWeatherMap
        using two separate, free API calls.
        """
        try:
            # --- Call 1: Get CURRENT weather ---
            current_url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?lat={self.lat}&lon={self.lon}"
                f"&units={self.units}&appid={self.api_key}"
            )
            
            print(f"WeatherService: Fetching current weather from: {current_url}")
            current_response = requests.get(current_url, timeout=10)
            current_response.raise_for_status() # Check for errors
            current_data = current_response.json()
            
            # --- Call 2: Get 5-DAY / 3-HOUR forecast ---
            forecast_url = (
                f"https://api.openweathermap.org/data/2.5/forecast"
                f"?lat={self.lat}&lon={self.lon}"
                f"&units={self.units}&appid={self.api_key}"
            )
            
            print(f"WeatherService: Fetching forecast from: {forecast_url}")
            forecast_response = requests.get(forecast_url, timeout=10)
            forecast_response.raise_for_status() # Check for errors
            forecast_data = forecast_response.json()

            # --- 1. Get data for the UI labels (from Call 1) ---
            temp = current_data['main']['temp']
            desc = current_data['weather'][0]['description'].title()
            
            # --- 2. Build the "Spoken Forecast" string (from Call 2) ---
            spoken_forecast = ""
            
            # Get today's forecast (first item in the 'list')
            # This API gives a 3-hour forecast. We'll find the max/min
            # for the next 24 hours (8 entries).
            today_high = -200
            today_low = 200
            forecast_desc = set() # Use a set to avoid duplicate descriptions

            for i in range(min(8, len(forecast_data['list']))): # Next 24 hours
                entry = forecast_data['list'][i]
                if entry['main']['temp_max'] > today_high:
                    today_high = entry['main']['temp_max']
                if entry['main']['temp_min'] < today_low:
                    today_low = entry['main']['temp_min']
                forecast_desc.add(entry['weather'][0]['description'])
            
            # Create a simple description
            if not forecast_desc:
                today_desc_str = desc # Fallback to current
            else:
                today_desc_str = ", ".join(list(forecast_desc))

            spoken_forecast = (
                f"Today's forecast includes {today_desc_str}, "
                f"with a high of {today_high:.0f} "
                f"and a low of {today_low:.0f}. "
                f"It is currently {temp:.0f} degrees and {desc}."
            )

            # --- 3. Prepare Data Packet ---
            weather_packet = {
                'temperature': temp,
                'description': desc,
                'spoken_forecast': spoken_forecast # The new data!
            }
            
            # --- 4. Emit Signal ---
            self.weather_data_ready.emit(weather_packet)
            print("WeatherService: Data fetch successful.")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching/parsing weather: {e}")
            self.weather_error.emit(f"Weather API Error: {e}")
        except KeyError as e:
            print(f"Error parsing weather data: Missing key {e}")
            self.weather_error.emit(f"Weather Data Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred in WeatherService: {e}")
            self.weather_error.emit(f"Unknown Error: {e}")