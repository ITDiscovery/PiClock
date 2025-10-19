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

### Prerequisites

This project is designed to run on a Raspberry Pi (3A+ or newer recommended) with Raspberry Pi OS.

* Python 3
* PyQt5
* Requests library

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/ITDiscovery/PiClock.git](https://github.com/ITDiscovery/PiClock.git)
    cd PiClock
    ```

2.  **Install the required Python libraries:**
    ```bash
    pip3 install PyQt5 requests
    ```

3.  **Configure the clock:**
    * Rename the `config.json.template` file to `config.json`.
        ```bash
        mv config.json.template config.json
        ```
    * Edit `config.json` with your own API keys, location, and other preferences.

4.  **Run the application:**
    ```bash
    python3 main.py
    ```

***
## Configuration

All clock settings are managed in the `config.json` file.

```json
{
  "api_keys": {
    "openweathermap": "YOUR_OPENWEATHERMAP_API_KEY",
    "newsapi": "YOUR_NEWS_API_KEY"
  },
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "display": {
    "background_color": "black",
    "font_color": "white",
    "units": "imperial"
  }
}
```
openweathermap: Get a free API key from OpenWeatherMap.

newsapi: Get a free API key from NewsAPI.org.

location: Set the latitude and longitude for your weather data.

units: Use imperial for Fahrenheit or metric for Celsius.
