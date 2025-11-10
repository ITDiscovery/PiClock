# PyQtPiClock

A modern, full-screen weather, news, and time display clock for the Raspberry Pi, rebuilt in Python 3 and PyQt5.

This project is a complete rebuild of the original PiClock, which was based on Qt4 and Python 2. This version modernizes the codebase for current hardware and software standards.

## Project History

This clock was originally based on the work from **`https://github.com/n0bel/PiClock`**, which was last updated around 2016. An initial update was made in 2019, and this repository represents a fresh rebuild to ensure long-term stability and compatibility.

### Rebuild To-Do List

* [ ] **Foundation:** Create the basic application window with Python 3 and PyQt5.
* [ ] **Configuration:** Implement a `config.json` file for all settings and API keys.
* [ ] **Clock:** Add the core digital clock and date display.
* [ ] **Weather:** Fetch and display current weather conditions.
* [ ] **Radar:** Integrate an animated weather radar map.
* [ ] **News Ticker:** Add a scrolling news headline ticker.
* [ ] **GPIO Control:** Implement logic for three external pushbuttons to change modes.
* [ ] **Error Handling:** Add robust error handling for network issues and API failures.
* [ ] **Weewx Integration:** If available, add data gathering from WeeWx weather station.


## Features (Use Cases)

This project turns a Raspberry Pi with a connected screen into a beautiful and informative smart display.

* **Digital Clock:** A large, clean, and easily readable display for the current time and date.
* **Current Weather:** Fetches and displays real-time weather conditions for a configurable location, including temperature, a weather description (e.g., "Clear Sky," "Light Rain"), and a weather icon.
* **Weather Radar:** Displays an animated, looping weather radar map for the local area to show precipitation.
* **News Ticker:** A smooth, scrolling ticker at the bottom of the screen that displays the latest headlines from a news source of your choice.
* **GPIO Pushbutton Control:** Supports three external pushbuttons connected via GPIO pins to change display modes or trigger actions.
* **Highly Configurable:** All API keys, location data, colors, and other settings are managed in a simple `config.json` file, requiring no changes to the core Python code.
* **Kiosk Mode:** Designed to run full-screen without any window borders for a clean, dedicated look.

***
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### 1. Hardware Setup

Before installing software, connect all your hardware:

* **Display:** Connect your display (e.g., 1024x600) via HDMI.
* **BME280 Sensor:** Connect the sensor to the Pi's I2C pins:
    * `VIN` -> 3.3V (Pin 1)
    * `GND` -> GND (Pin 9)
    * `SDA` -> BCM 2 (Pin 3)
    * `SCL` -> BCM 3 (Pin 5)
* **GPIO Buttons:** Connect your three buttons. This setup uses the Pi's internal pull-up resistors, so you only need to connect each button to a GPIO pin and a Ground pin.
    * **"Next Frame" Button:** BCM 5 (Pin 29) & GND
    * **"Play Audio" Button:** BCM 6 (Pin 31) & GND
    * **"Reboot" Button:** BCM 26 (Pin 37) & GND

### 2. System Configuration & Dependencies

This is the most critical part of the setup.

#### Step 2a: Grant GPIO & Audio Permissions

The app must be run by the standard `pi` user for audio to work correctly. We need to grant this user permissions to access the GPIO hardware.

1.  Add the `pi` user to the `gpio` group:
    ```bash
    sudo usermod -a -G gpio pi
    ```
2.  **You must reboot** for this change to take effect:
    ```bash
    sudo reboot
    ```

#### Step 2b: Install System Packages (apt)

Once rebooted, log in and install all the system-level libraries for audio, sensors, and image formats.

```bash
sudo apt update
sudo apt install espeak-ng alsa-utils libqt5gui5 qt5-image-formats-plugins python3-smbus2 python3-rpi.bme280
```

* **espeak-ng: The text-to-speech engine.
* **alsa-utils: Provides the aplay command for audio.
* **qt5-image-formats-plugins: CRITICAL. This adds GIF support to Qt5.
* **python3-smbus2 & python3-rpi.bme280: Drivers for your BME280 sensor.

#### Step 2c: (Optional) Install High-Quality Voice

1. Download the **mbrola engine and the us1 voice (these are not in the default **bookworm repository):
```bash
wget [http://ftp.debian.org/debian/pool/non-free/m/mbrola/mbrola_3.01+repack2-5_all.deb](http://ftp.debian.org/debian/pool/non-free/m/mbrola/mbrola_3.01+repack2-5_all.deb)
wget [http://ftp.debian.org/debian/pool/non-free/m/mbrola-us1/mbrola-us1_0.3+repack2-5_all.deb](http://ftp.debian.org/debian/pool/non-free/m/mbrola-us1/mbrola-us1_0.3+repack2-5_all.deb)
```

2. Install the packages using `dpkg`:
```bash
sudo dpkg -i mbrola_3.01+repack2-5_all.deb mbrola-us1_0.3+repack2-5_all.deb
```

3. Register the voice with `espeak-ng` by creating a config file:
```bash
sudo nano /usr/share/espeak-ng-data/mbrola_voices
```

4. Paste this single line into the file, then save and exit:
```bash
mb-us1 m en /usr/share/mbrola/us1/us1
```

### 3. Application Setup

#### Step 3a: Get the Code

Clone the project repository from GitHub (replace with your URL):
```bash
git clone [https://github.com/your-username/PiClock.git](https://github.com/your-username/PiClock.git)
cd PiClock
```

#### Step 3b: Install Python Libraries (pip)
Create a `requirements.txt` file for the Python dependencies.

1. Create the file
```bash3
nano requirements.txt
```
2. Paste these two lines into the file:
```bash
PyQt5
requests
```
3. Install the libraries
```bash
pip install -r requirements.txt
```

#### Step 3c: Create Configuration File
Create your `config.json file`. You can copy the template below.

```bash
nano config.json
```

Paste this text and fill in your personal API keys and location details:
```json
{
  "api_keys": {
    "openweathermap": "YOUR_OPENWEATHERMAP_API_KEY",
    "newsapi": "YOUR_NEWSAPI_API_KEY"
  },
  "debug": true,
  "location": {
    "latitude": 42.9881,
    "longitude": -85.0689,
    "nws_office": "GRR",
    "nws_zone_id": "MIZ058"
  },
  "display": {
    "background_color": "black",
    "font_color": "white",
    "units": "imperial",
    "news_country": "us",
    "screen": {
      "width": 1024,
      "height": 600,
      "start_x": 0,
      "start_y": 0
    }
  },
  "hardware": {
    "enable": true,
    "bme280_i2c_address": "0x76",
    "poll_interval_ms": 2000,
    "buttons": {
      "next_frame": 5,
      "play_audio": 6,
      "reboot": 26
    }
  },
  "audio": {
    "aplay_device": "default",
    "audio_volume_percent": 90,
    "espeak_voice": "mb-us1",
    "spoken_forecast_periods": 8
  },
  "radar_frame": {
    "url": "[https://radar.weather.gov/ridge/standard/KGRR_loop.gif](https://radar.weather.gov/ridge/standard/KGRR_loop.gif)",
    "refresh_ms": 600000
  },
  "map_frame": {
    "url": "[https://radar.weather.gov/ridge/standard/CONUS_loop.gif](https://radar.weather.gov/ridge/standard/CONUS_loop.gif)",
    "refresh_ms": 300000
  }
}
```
Note: If you skipped the MBROLA install, change espeak_voice to "en-us".

### 4. Run the Application

You can now run the clock! **Do not use `sudo`.**
```bash
python3 main.py
```
### 5. (Optional) Run on Boot

To make the clock start automatically when the Pi boots up:

1.  Create a launcher script:
    ```bash
    nano start_clock.sh
    ```
2.  Paste in the following. This waits 10 seconds for the network to connect before launching.
    ```bash
    #!/bin/bash
    sleep 10
    cd "$(dirname "$0")"
    python3 main.py
    ```
3.  Save, exit, and make it executable:
    ```bash
    chmod +x start_clock.sh
    ```
4.  Create the autostart "shortcut" file:
    ```bash
    mkdir -p ~/.config/autostart
    nano ~/.config/autostart/piclock.desktop
    ```
5.  Paste in the following (confirm the `Exec=` path is correct for your system):
    ```ini
    [Desktop Entry]
    Name=PiClock
    Comment=Raspberry Pi Weather Clock
    Exec=/home/pi/PiClock/start_clock.sh
    Type=Application
    Terminal=false
    ```
6.  Save and exit.

Now, reboot your Pi (`sudo reboot`), and the clock should launch automatically.

## Application Architecture

This project uses a modular, service-oriented architecture based on PyQt5's **signals and slots** mechanism. The core principle is a complete **Separation of Concerns**, which makes the application stable, easy to debug, and simple to extend.

The application is broken into three main parts:

1.  **The UI (`ui/WeatherWindow.py`)**
    This is the "dumb" front-end. It is responsible *only* for displaying data. It creates all the labels, image containers, and multiple screens (using a `QStackedWidget`). It has no knowledge of *how* to get data. It only has public "slots" (like `on_weather_ready`) that wait to be told what to display.

2.  **The Services (`core/`)**
    These are the background workers. Each service is a `QObject` that runs on its own timers. It handles one job (e.g., fetching weather, polling hardware) and has no knowledge of the UI. When it has new data, it emits a "signal" (e.g., `weather_data_ready`).

3.  **The Conductor (`main.py`)**
    This is the central entry point that acts as the "conductor." Its only job is to:
    * Load the `config.json`.
    * Create one instance of the UI (`WeatherWindow`).
    * Create one instance of *each* service.
    * Connect the **signals** from the services to the **slots** in the UI.
    * Start all the services and run the application.

This design means if the NWS API changes, we only need to edit `core/WeatherService.py`. The rest of the application is completely unaffected.

## Code Summary

Here is a summary of each file in the project.

### `main.py`
This is the main entry point for the application. It contains no logic. It simply initializes all the service classes and the UI class, and then connects their signals and slots to orchestrate the flow of data.

### `config.json`
The central settings file for the entire application. It stores all API keys, hardware pin numbers, screen resolution, locations, and image URLs. This allows for complete configuration without touching any Python code.

### `config_utils.py`
A simple, safe utility to load the `config.json` file. It checks for file-not-found errors and invalid JSON, exiting gracefully if the config is missing or broken.

### `ui/WeatherWindow.py`
This is the *only* file that contains Qt5 UI code (widgets, layouts, etc.).
* It creates all visual elements (labels, images).
* It manages the `QStackedWidget` to switch between the "local radar" frame and the "national map" frame.
* It defines all the public **slots** (e.g., `@pyqtSlot(dict) def on_weather_ready(self, data):`) that the services send data to.
* It handles the logic for the animated radar (`QMovie`) by loading the GIFs that the services provide.

### `core/WeatherService.py`
Handles all weather data fetching.
* Fetches current conditions from **OpenWeatherMap** (for the visual display).
* Fetches the detailed, human-written **NWS Zone Forecast Product (ZFP)** for the specified NWS office and zone.
* Includes a robust fallback to use OWM's forecast data if the NWS fetch fails.
* Emits a `weather_data_ready` signal with a dictionary of all the data.

### `core/MapService.py`
A generic, reusable service for fetching animated images.
* Reads a URL and refresh timer from its config.
* Downloads the file, handling `User-Agent` headers to avoid being blocked by servers.
* Checks if the downloaded file is a valid `image/gif`.
* Saves the GIF to a local temporary file (e.g., `_radar.gif`).
* Emits a `map_file_ready` signal with the file path.
* *(Note: `main.py` creates two instances of this service: one for the local radar and one for the national map.)*

### `core/NewsService.py`
Manages the scrolling news ticker at the bottom of the screen.
* Fetches headlines from the **NewsAPI**.
* Manages two internal timers: one to fetch new headlines periodically and one to "scroll" the text.
* Emits a `news_ticker_updated` signal with the new text string on every scroll tick.

### `core/HardwareService.py`
Manages all physical hardware on the Raspberry Pi.
* Safely imports `RPi.GPIO` and `bme280` so the app can run on a PC (in debug mode) without crashing.
* Polls the **BME280** sensor and emits `bme_data_ready` with local temp/humidity.
* Polls the GPIO buttons, applies debouncing, and emits a `button_pressed` signal with the *action name* (e.g., "next_frame") from the config.

### `core/TTSService.py`
Manages all text-to-speech audio.
* Provides a public `speak(text)` slot that acts as a **play/stop toggle**.
* Executes the `espeak-ng | aplay` command in a subprocess.
* Uses the `aplay_device` and `espeak_voice` from `config.json` to ensure audio works correctly for the `pi` user.
* Emits an `audio_state_changed(bool)` signal so the UI can show/hide the "o)))" speaker icon.


