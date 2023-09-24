# PiClock

A Raspberry Pi XWindows (via QT) Weather and Wall Clock. This had to be rebuilt from https://github.com/n0bel/PiClock, which is QT4 and hadn't been updated since 2016ish.

More goals:
- Adding BME280 internal information Done: weewx device for RPi raw sensors at https://github.com/jardiamj/BYOWS_RPi
- Adding calls to weewx for external weather station
- Move to openweathermap.org for weather data and forcasting.
- Add "headless" feature to allow for a few buttons on the RPi to change screens, restart, and turn of NOAA weather radio
- Remove the ugly hack that turns GPIO into keypresses, and put it in natively

File structure:
- PiClock is the main directory
  - Clock is the directory the code runs out of
    - icons is the directory the openweathermap icons are at
    - Pictures is where the slideshow pictures are  

Screen Object Reference

Code starts running at "class MyMain" where initialization happens: it picks up Config.py for preferences.

Config.py contains the preferences for the radar box sizes. There are five different radar styles:
1. Center=primary_location, Zoom=5, color=6, smooth=1, snow=1, marker at primary location (Frame 1)
2. Center=primary_location, Zoom=10, color=8, smooth=1, snow=1, marker at primary location (Frame 1)
3. Center=primary_location, Zoom=6, color=6, smooth=1, snow=1, marker at primary location (Frame 2)
4. Center=primary_location, Zoom=11, color=6, smooth=1, snow=1, marker at primary location (Frame 2)
5. Center=primary_location, Zoom=9, color=6, smooth=1, snow=1, marker at primary location (Frame 3)

keyPressEvent captures keypress/GPIO events:
- F4 = Quit
- F2 = WxRadio stream toggle
- Space/Right Arrow = Next Frame
- Left Arrow = Previous Frame
- F9 Hide/Show
