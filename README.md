# PiClock
Mods to https://github.com/n0bel/PiClock weather display

Use case to provide an API call to retrieve current data from a raspberry pi weather station using (for now) weewx weather station software. Project will investigate:

Done: weewx device for RPi raw sensors at https://github.com/jardiamj/BYOWS_RPi

1. Weewx does not supply a xfer agent, so write one using a common RESTful scheme (preferably a standard used by AWEKAS, so you can point PiClock locally or to AWEKAS). It should pull from weewx database.

Call to 127.0.0.1/data/1.0/weather?=local

API Response:

{"coord": { "lon": -139,"lat": 35},  \
  "main": {  \
    "temp": 289.92, \
    "pressure": 1009, \
    "humidity": 92, \
    "temp_min": 288.71, \
    "temp_max": 290.93 \
  }, \
  "wind": {
    "speed": 0.47,
    "deg": 107.538
  },
  "timezone": 32400,
  "id": 1851632,
  "name": "Shuzenji",
  "cod": 200
}



Parameters:

coord \
coord.lon City geo location, longitude
coord.lat City geo location, latitude
weather (more info Weather condition codes)
weather.id Weather condition id
weather.main Group of weather parameters (Rain, Snow, Extreme etc.)
weather.description Weather condition within the group
weather.icon Weather icon id
base Internal parameter
main
main.temp Temperature. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit.
main.pressure Atmospheric pressure (on the sea level, if there is no sea_level or grnd_level data), hPa
main.humidity Humidity, %
main.temp_min Minimum temperature at the moment. This is deviation from current temp that is possible for large cities and megalopolises geographically expanded (use these parameter optionally). Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit.
main.temp_max Maximum temperature at the moment. This is deviation from current temp that is possible for large cities and megalopolises geographically expanded (use these parameter optionally). Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit.
main.sea_level Atmospheric pressure on the sea level, hPa
main.grnd_level Atmospheric pressure on the ground level, hPa
wind
wind.speed Wind speed. Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour.
wind.deg Wind direction, degrees (meteorological)
clouds
clouds.all Cloudiness, %
rain
rain.1h Rain volume for the last 1 hour, mm
rain.3h Rain volume for the last 3 hours, mm
snow
snow.1h Snow volume for the last 1 hour, mm
snow.3h Snow volume for the last 3 hours, mm
dt Time of data calculation, unix, UTC
sys
sys.type Internal parameter
sys.id Internal parameter
sys.message Internal parameter
sys.country Country code (GB, JP etc.)
sys.sunrise Sunrise time, unix, UTC
sys.sunset Sunset time, unix, UTC
timezone Shift in seconds from UTC
id City ID
name City name

Weewx archive table schema:
`dateTime` INTEGER NOT NULL UNIQUE PRIMARY KEY
`usUnits` INTEGER NOT NULL
`interval` INTEGER NOT NULL
`barometer` REAL
`pressure` REAL
`altimeter` REAL
`inTemp` REAL
`outTemp` REAL
`inHumidity` REAL
`outHumidity` REAL
`windSpeed` REAL
`windDir` REAL
`windGust` REAL
`windGustDir` REAL
`rainRate` REAL
`rain` REAL
`dewpoint` REAL
`windchill` REAL
`heatindex` REAL
`ET` REAL
`radiation` REAL
`UV` REAL
`extraTemp1` REAL
`extraTemp2` REAL
`extraTemp3` REAL
`soilTemp1` REAL
`soilTemp2` REAL
`soilTemp3` REAL
`soilTemp4` REAL
`leafTemp1` REAL
`leafTemp2` REAL
`extraHumid1` REAL
`extraHumid2` REAL
`soilMoist1` REAL
`soilMoist2` REAL
`soilMoist3` REAL
`soilMoist4` REAL
`leafWet1` REAL
`leafWet2` REAL
`rxCheckPercent` REAL
`txBatteryStatus` REAL
`consBatteryVoltage` REAL
`hail` REAL
`hailRate` REAL
`heatingTemp` REAL
`heatingVoltage` REAL
`supplyVoltage` REAL
`referenceVoltage` REAL
`windBatteryStatus` REAL
`rainBatteryStatus` REAL
`outTempBatteryStatus` REAL
`inTempBatteryStatus` REAL


2. Weewx does send to AWEKAS, so done.
3. Write a reciever for PiClock that will read the RESTful scheme from local as above.
