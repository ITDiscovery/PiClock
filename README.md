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

2. Install the packages using dpkg:
```bash
sudo dpkg -i mbrola_3.01+repack2-5_all.deb mbrola-us1_0.3+repack2-5_all.deb
```

3. Register the voice with espeak-ng by creating a config file:
```bash
sudo nano /usr/share/espeak-ng-data/mbrola_voices
```

