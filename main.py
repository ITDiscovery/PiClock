import sys
import os # <-- NEW IMPORT
from PyQt5.QtWidgets import QApplication

from config_utils import load_config
from ui.WeatherWindow import WeatherWindow

from core.WeatherService import WeatherService
from core.NewsService import NewsService
from core.HardwareService import HardwareService
from core.TTSService import TTSService
from core.MapService import MapService

def main():
    print("Loading configuration...")
    config = load_config('config.json')

    app = QApplication(sys.argv)
    window = WeatherWindow(config)
    
    print("Initializing services...")
    weather_service = WeatherService(config)
    news_service = NewsService(config)
    hardware_service = HardwareService(config)
    tts_service = TTSService(config)
    
    # --- UPDATED: Use absolute paths ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    radar_file_path = os.path.join(BASE_DIR, "_radar.gif")
    map_file_path = os.path.join(BASE_DIR, "_map.gif")
    
    radar_service = MapService(config['radar_frame'], radar_file_path)
    map_service = MapService(config['map_frame'], map_file_path)

    # ... (Rest of the file is unchanged) ...
    print("Connecting services to UI...")
    
    weather_service.weather_data_ready.connect(window.on_weather_ready)
    weather_service.weather_error.connect(window.on_weather_error)
    
    radar_service.map_file_ready.connect(window.on_radar_ready)
    radar_service.map_error.connect(window.on_radar_error)
    
    news_service.news_ticker_updated.connect(window.on_news_updated)
    hardware_service.bme_data_ready.connect(window.on_bme_data)
    
    map_service.map_file_ready.connect(window.on_map_ready)
    map_service.map_error.connect(window.on_map_error)
    
    hardware_service.button_pressed.connect(window.on_button_pressed)
    hardware_service.button_pressed.connect(
        lambda action: tts_service.speak(
            window.current_spoken_forecast
        ) if action == "play_audio" else None
    )
    hardware_service.button_pressed.connect(
        lambda action: os.system("reboot") if action == "reboot" else None
    )
    hardware_service.hardware_error.connect(window.on_weather_error)

    print("Connecting cleanup tasks...")
    app.aboutToQuit.connect(hardware_service.cleanup)
    app.aboutToQuit.connect(tts_service.cleanup)

    print("Starting services...")
    weather_service.start()
    radar_service.start()
    news_service.start()
    hardware_service.start()
    map_service.start()   
    
    print("--- Application Started ---")
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()