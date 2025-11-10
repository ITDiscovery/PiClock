import requests
import re
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

class WeatherService(QObject):
    """
    Handles all weather data fetching.
    - OpenWeatherMap: for visual display (temp, description)
    - NWS ZFP: for the detailed spoken forecast text
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
        self.nws_office = self.config['location'].get('nws_office', None)
        
        # --- NEW: Read NWS Zone ID ---
        self.nws_zone_id = self.config['location'].get('nws_zone_id', None)
        
        audio_config = self.config.get('audio', {})
        self.spoken_forecast_periods = audio_config.get('spoken_forecast_periods', 2)
        
        self.update_interval = self.config['display'].get('weather_refresh_ms', 900000)

    def start(self):
        """Starts the weather service timer."""
        print("WeatherService started. Fetching initial data...")
        self.update_weather()
        self.weather_timer.start(self.update_interval)

    # --- UPDATED: More robust parser ---
    def _clean_zfp_text(self, text, zone_id, num_periods):
        """
        Cleans the raw ZFP text for a *specific zone* to make it speakable.
        """
        if not text or not zone_id:
            return None

        # 1. Create a regex to find our specific zone block.
        zone_regex = re.compile(r'^' + re.escape(zone_id) + r'.*?\n(.*?)(?=^\w{2}Z\d{3}.*|^\$\$)', re.MULTILINE | re.DOTALL)
        zone_match = zone_regex.search(text)

        if not zone_match:
            print(f"WeatherService: Could not find zone '{zone_id}' in ZFP.")
            return None
        
        zone_text = zone_match.group(1)

        # 2. Split this block into periods.
        all_periods = re.split(r'\n(?=\.|\.\.\.)', zone_text)
        
        first_period_index = -1
        for i, period in enumerate(all_periods):
            if period.strip().startswith('.') or period.strip().startswith('...'):
                first_period_index = i
                break
        
        if first_period_index == -1:
             print(f"WeatherService: Found zone '{zone_id}', but no forecast periods (like .TONIGHT...)")
             return None
            
        # Get all valid forecast periods
        all_valid_periods = all_periods[first_period_index:]
        
        # --- NEW LOGIC ---
        # If user wants 0 or less, send all. Otherwise, send the requested number.
        if num_periods <= 0:
            our_periods = all_valid_periods
            print(f"WeatherService: Reading all {len(our_periods)} forecast periods.")
        else:
            our_periods = all_valid_periods[:num_periods]
            print(f"WeatherService: Reading {len(our_periods)} of {num_periods} requested periods.")
        
        # 3. Clean and join
        full_forecast = " ".join(our_periods)
        full_forecast = re.sub(r'\n', ' ', full_forecast)
        full_forecast = re.sub(r'\s+', ' ', full_forecast)
        full_forecast = re.sub(r'\.\.\.', '... ', full_forecast)
        
        return full_forecast.strip()

    def _get_nws_forecast_text(self):
        """
        Fetches the detailed Zone Forecast Product (ZFP) text from the NWS.
        """
        if not self.nws_office or not self.nws_zone_id:
            print("WeatherService: No 'nws_office' or 'nws_zone_id' in config. Skipping ZFP fetch.")
            return None
            
        try:
            list_url = f"https://api.weather.gov/products/types/ZFP/locations/{self.nws_office}"
            headers = {'User-Agent': 'PiWeatherClock (my-email@example.com)'}
            
            list_resp = requests.get(list_url, headers=headers, timeout=10)
            list_resp.raise_for_status()
            
            latest_product_url = list_resp.json()['@graph'][0]['@id']
            
            product_resp = requests.get(latest_product_url, headers=headers, timeout=10)
            product_resp.raise_for_status()
            
            raw_text = product_resp.json().get('productText', None)
            
            # --- UPDATED: Pass num_periods and zone_id to the cleaner ---
            return self._clean_zfp_text(raw_text, self.nws_zone_id, self.spoken_forecast_periods)
            
        except requests.exceptions.RequestException as e:
            print(f"WeatherService: NWS API error: {e}")
            return None
        except (KeyError, IndexError) as e:
            print(f"WeatherService: Error parsing NWS product list: {e}")
            return None

    def update_weather(self):
        """
        Fetches current weather from OWM and forecast text from NWS.
        """
        try:
            # --- Call 1: Get CURRENT weather (for visual display) ---
            current_url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?lat={self.lat}&lon={self.lon}"
                f"&units={self.units}&appid={self.api_key}"
            )
            print(f"WeatherService: Fetching current weather from: {current_url}")
            current_response = requests.get(current_url, timeout=10)
            current_response.raise_for_status()
            current_data = current_response.json()
            
            temp = current_data['main']['temp']
            desc = current_data['weather'][0]['description'].title()
            
            # --- Call 2: Get NWS Zone Forecast Product (for audio) ---
            spoken_forecast = self._get_nws_forecast_text()
            
            # --- FALLBACK: If NWS fails, build our own forecast ---
            if not spoken_forecast:
                print("WeatherService: NWS fetch failed, falling back to OWM forecast.")
                
                forecast_url = (
                    f"https://api.openweathermap.org/data/2.5/forecast"
                    f"?lat={self.lat}&lon={self.lon}"
                    f"&units={self.units}&appid={self.api_key}"
                )
                print(f"WeatherService: Fetching OWM forecast from: {forecast_url}")
                forecast_response = requests.get(forecast_url, timeout=10)
                forecast_response.raise_for_status()
                forecast_data = forecast_response.json()

                today_high = -200
                today_low = 200
                forecast_desc = set()
                for i in range(min(8, len(forecast_data['list']))):
                    entry = forecast_data['list'][i]
                    if entry['main']['temp_max'] > today_high: today_high = entry['main']['temp_max']
                    if entry['main']['temp_min'] < today_low: today_low = entry['main']['temp_min']
                    forecast_desc.add(entry['weather'][0]['description'])
                
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
                'spoken_forecast': spoken_forecast
            }
            
            # --- 4. Emit Signal ---
            self.weather_data_ready.emit(weather_packet)
            print("WeatherService: Data fetch successful.")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching/parsing OWM weather: {e}")
            self.weather_error.emit(f"Weather API Error: {e}")
        except KeyError as e:
            print(f"Error parsing OWM weather data: {e}")
            self.weather_error.emit(f"Weather Data Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred in WeatherService: {e}")
            self.weather_error.emit(f"Unknown Error: {e}")