# PiClock
Mods to https://github.com/n0bel/PiClock weather display

Use case to provide an API call to retrieve current data from a raspberry pi weather station using (for now) weewx weather station software. Project will investigate:

1. Does weewx supply a json xfer agent. If not, we'll need to write one and contribute it.
2. Does weewx supply a xfer agent to AWEKAS. If it requires an external address, an additional feature will be needed to push via json to AWEKAS.
3. Get data from AWEKAS to the PiClock. This will need to be added.
4. Write json xfer agent for Raspberry Pi foundation version of weather station.
