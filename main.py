import sys
import os
from PyQt5.QtWidgets import QApplication

# --- 1. Import all our modules ---
from config_utils import load_config
from ui.WeatherWindow import WeatherWindow

# --- Import Core Services ---
from core.WeatherService import WeatherService
from core.NewsService import NewsService
from core.HardwareService import HardwareService
from core.TTSService import TTSService
from core.MapService import MapService # We will use this for both!

def main():
    # --- 1. Load Config ---
    print("Loading configuration...")
    config = load_config('config.json')

    # --- 2. Create the Application and Main Window ---
    app = QApplication(sys.argv)
    window = WeatherWindow(config)
    
    # --- 3. Initialize All Services ---
    print("Initializing services...")
    weather_service = WeatherService(config)
    news_service = NewsService(config)
    hardware_service = HardwareService(config)
    tts_service = TTSService(config)
    
    # --- Create two instances of MapService ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    radar_file_path = os.path.join(BASE_DIR, "_radar.gif")
    map_file_path = os.path.join(BASE_DIR, "_map.gif")
    
    radar_service = MapService(config['radar_frame'], radar_file_path)
    map_service = MapService(config['map_frame'], map_file_path)

    # --- 4. Connect Services to UI Slots ---
    print("Connecting services to UI...")
    
    # Weather
    weather_service.weather_data_ready.connect(window.on_weather_ready)
    weather_service.weather_error.connect(window.on_weather_error)
    
    # --- Connect the 'radar_service' instance ---
    # This connects our first MapService to the radar slots
    radar_service.map_file_ready.connect(window.on_radar_ready)
    radar_service.map_error.connect(window.on_radar_error)
    
    # News
    news_service.news_ticker_updated.connect(window.on_news_updated)
    
    # BME280 Sensor
    hardware_service.bme_data_ready.connect(window.on_bme_data)
    
    # --- Connect the 'map_service' instance ---
    # This connects our second MapService to the map slots
    map_service.map_file_ready.connect(window.on_map_ready)
    map_service.map_error.connect(window.on_map_error)
    
    # --- Connect the audio state signal ---
    tts_service.audio_state_changed.connect(window.on_audio_state_changed)
    
    # --- 5. Connect Hardware to UI and other Services ---
    
    # Button presses go to the UI (for "next_frame")
    hardware_service.button_pressed.connect(window.on_button_pressed)
    
    # Connect "play_audio" button to the TTSService
    hardware_service.button_pressed.connect(
        lambda action: tts_service.speak(
            window.current_spoken_forecast
        ) if action == "play_audio" else None
    )

    # Connect "reboot" button
    hardware_service.button_pressed.connect(
        lambda action: os.system("reboot") if action == "reboot" else None
    )
    
    # Hardware errors
    hardware_service.hardware_error.connect(window.on_weather_error)

    # --- 6. Setup Application Cleanup ---
    print("Connecting cleanup tasks...")
    app.aboutToQuit.connect(hardware_service.cleanup)
    app.aboutToQuit.connect(tts_service.cleanup)

    # --- 7. Start All Services ---
    print("Starting services...")
    weather_service.start()
    radar_service.start() # <-- This is our first MapService
    news_service.start()
    hardware_service.start()
    map_service.start()   # <-- This is our second MapService
    
    print("--- Application Started ---")

    # --- 8. Run the Application ---
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()