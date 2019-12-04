import time
import sqlite3
from flask import Flask
import json

app = Flask(__name__)

wxlon = -97.232325
wxlat = 32.827043

@app.route("/")
def index():
	weewxconn = sqlite3.connect('/var/lib/weewx/weewx.sdb')
	wxcursor = weewxconn.cursor()
	weatherdata = {"coord": {"lon":-97.232325,"lat":32.827043 },
	"main": {},
	"wind": {},
	"timezone":21600,
	"id":4715292,
	"name": "KC5EDF",
	"cod": 200
	}
	# Get latest data from BYOWS database
	wxcursor.execute("SELECT dateTime,outTemp,outHumidity,barometer,windSpeed,windDir FROM archive ORDER BY dateTime DESC")
	wxresult = wxcursor.fetchone()

	weatherdata["dt"] = wxresult[0]
	weatherdata["main"]["temp"] = wxresult[1]
	weatherdata["main"]["pressure"] = wxresult[2]
	weatherdata["main"]["humidity"] = wxresult[3]
	weatherdata["wind"]["speed"] = wxresult[4]
	weatherdata["wind"]["deg"] = wxresult[5]

	return json.dumps(weatherdata, ensure_ascii=False)

if __name__=="__main__":
	app.run(host="0.0.0.0")
