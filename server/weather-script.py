#!/usr/bin/python

# Kindle Weather Display
# Originally by Matthew Petroff (http://www.mpetroff.net/)
# Modified by John Kua (http://john.kua.fm)
# March 2014

import urllib2
from xml.dom import minidom
import datetime
import codecs
import sys

# Get location from command line
if len(sys.argv) >= 3:
	latitude = sys.argv[1]
	longitude = sys.argv[2]
	if len(sys.argv) >= 4:
		wundergroundApiKey = sys.argv[3]
else:
	latitude = 37
	longitude = -122

#
# Download and parse weather data
#

useWunderground = True

if useWunderground == True:
	iconDict = dict()
	iconDict['chanceflurries']='sn' #bad
	iconDict['chancerain']='hi_shwrs'
	iconDict['chancesleet']='ip' #bad
	iconDict['chancesnow']='sn' #bad
	iconDict['chancetstorms']='scttsra'
	iconDict['clear']='skc'
	iconDict['cloudy']='ovc'
	iconDict['flurries']='sn' # not a good match
	iconDict['fog']='fg'
	iconDict['haze']='du' #eh
	iconDict['mostlycloudy']='bkn'
	iconDict['partlysunny']='bkn'
	iconDict['mostlysunny']='sct'
	iconDict['partlycloudy']='sct'
	iconDict['rain']='ra'
	iconDict['sleet']='ip'
	iconDict['snow']='sn'
	iconDict['tstorms']='tsra'
	iconDict['unknown']='skc' #bad


	weatherXml = urllib2.urlopen('http://api.wunderground.com/api/' + wundergroundApiKey + '/astronomy/conditions/forecast10day/hourly10day/tide/yesterday/q/' + str(latitude) + ',' + str(longitude) + '.xml').read()
	dom = minidom.parseString(weatherXml)
	simpleForecastXml = dom.getElementsByTagName('simpleforecast')
	forecastDayXml = simpleForecastXml[0].getElementsByTagName('forecastday')
	highs = []
	lows = []
	icons = []
	pop = []
	qpf_day =[]
	qpf_night = []
	snow_day = []
	snow_night = []
	for forecastDay in forecastDayXml:
		tempsXml = forecastDay.getElementsByTagName('fahrenheit')
		highs.append(tempsXml[0].firstChild.nodeValue)
		lows.append(tempsXml[1].firstChild.nodeValue)
		iconXml = forecastDay.getElementsByTagName('icon')
		icons.append(iconDict[iconXml[0].firstChild.nodeValue])
		popXml = forecastDay.getElementsByTagName('pop')
		pop.append(int(popXml[0].firstChild.nodeValue))
		rainQuantityXml = forecastDay.getElementsByTagName('in')
		qpf_day.append(float(rainQuantityXml[0].firstChild.nodeValue))
		qpf_night.append(float(rainQuantityXml[1].firstChild.nodeValue))
		snow_day.append(float(rainQuantityXml[2].firstChild.nodeValue))
		snow_night.append(float(rainQuantityXml[3].firstChild.nodeValue))
	day = int(forecastDayXml[0].getElementsByTagName('day')[0].firstChild.nodeValue)
	month = int(forecastDayXml[0].getElementsByTagName('month')[0].firstChild.nodeValue)
	year = int(forecastDayXml[0].getElementsByTagName('year')[0].firstChild.nodeValue)
	day_one = datetime.date(year, month, day)

	txtForecastXml = dom.getElementsByTagName('txt_forecast')
	txtForecastDayXml = txtForecastXml[0].getElementsByTagName('forecastday')
	pop_day = []
	pop_night = []
	for i, forecastDay in enumerate(txtForecastDayXml):
		popXml = forecastDay.getElementsByTagName('pop')
		if i % 2 == 0:
			pop_day.append(int(popXml[0].firstChild.nodeValue))
		else:
			pop_night.append(int(popXml[0].firstChild.nodeValue))

	currentObservationXml = dom.getElementsByTagName('current_observation')
	currentTemperatureXml = currentObservationXml[0].getElementsByTagName('temp_f')
	currentTemperature = str(int(round(float(currentTemperatureXml[0].firstChild.nodeValue))))
	windSpeedXml = currentObservationXml[0].getElementsByTagName('wind_mph')
	windSpeed = windSpeedXml[0].firstChild.nodeValue
	windDirectionXml = currentObservationXml[0].getElementsByTagName('wind_dir')
	windDirection = windDirectionXml[0].firstChild.nodeValue

	moonPhaseXml = dom.getElementsByTagName('moon_phase')[0]
	moonPercentIlluminated = moonPhaseXml.getElementsByTagName('percentIlluminated')[0].firstChild.nodeValue
	moonAge = moonPhaseXml.getElementsByTagName('ageOfMoon')[0].firstChild.nodeValue
	sunriseXml = moonPhaseXml.getElementsByTagName('sunrise')[0]
	sunriseHour = sunriseXml.getElementsByTagName('hour')[0].firstChild.nodeValue
	sunriseMinute = sunriseXml.getElementsByTagName('minute')[0].firstChild.nodeValue
	sunsetXml = moonPhaseXml.getElementsByTagName('sunset')[0]
	sunsetHour = sunsetXml.getElementsByTagName('hour')[0].firstChild.nodeValue
	sunsetMinute = sunsetXml.getElementsByTagName('minute')[0].firstChild.nodeValue
	sunrise = datetime.time(int(sunriseHour),int(sunriseMinute))
	sunset = datetime.time(int(sunsetHour),int(sunsetMinute))

else:
	# Fetch data (change lat and lon to desired location)
	weather_xml = urllib2.urlopen('http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php?whichClient=NDFDgenByDay&lat=' + latitude + '&lon=' + longitude + '&format=24+hourly&numDays=4&Unit=e').read()
	dom = minidom.parseString(weather_xml)

	# Parse temperatures
	xml_temperatures = dom.getElementsByTagName('temperature')
	highs = [None]*4
	lows = [None]*4
	for item in xml_temperatures:
		if item.getAttribute('type') == 'maximum':
			values = item.getElementsByTagName('value')
			for i in range(len(values)):
				highs[i] = int(values[i].firstChild.nodeValue)
		if item.getAttribute('type') == 'minimum':
			values = item.getElementsByTagName('value')
			for i in range(len(values)):
				lows[i] = int(values[i].firstChild.nodeValue)

	
	# Parse icons
	xml_icons = dom.getElementsByTagName('icon-link')
	icons = [None]*4
	for i in range(len(xml_icons)):
		icons[i] = xml_icons[i].firstChild.nodeValue.split('/')[-1].split('.')[0].rstrip('0123456789')

	# Parse dates
	xml_day_one = dom.getElementsByTagName('start-valid-time')[0].firstChild.nodeValue[0:10]
	day_one = datetime.datetime.strptime(xml_day_one, '%Y-%m-%d')



#
# Preprocess SVG
#

# Open SVG to process
if useWunderground == True:
	output = codecs.open('weather-script-wunderground-preprocess.svg', 'r', encoding='utf-8').read()
	output = output.replace('TEMP_NOW',currentTemperature)
	output = output.replace('SUNRISE',sunriseHour + ':' + sunrise.strftime('%M'))
	output = output.replace('SUNSET',str(sunset.hour-12) + ':' + sunset.strftime('%M'))
	output = output.replace('MOON_ILLUMINATION',moonPercentIlluminated)
	output = output.replace('MOON_AGE',moonAge)
	output = output.replace('WIND_SPEED',windSpeed)
	output = output.replace('WIND_DIR',windDirection)

	if pop[0] > 10:
		percentPrecipitation = '<g font-family="DejaVu Sans">\n'
		percentPrecipitation += '<text style="text-anchor:end;" font-size="20px" y="300" x="380">Day: ' + str(pop_day[0]) +'%</text>\n'
		percentPrecipitation += '<text style="text-anchor:end;" font-size="20px" y="325" x="380">Night: ' + str(pop_night[0]) +'%</text>\n'
		percentPrecipitation += '</g>\n</svg>' 
		output = output.replace('</svg>',percentPrecipitation)

	if pop[1] > 10:
		percentPrecipitation = '<g font-family="DejaVu Sans">\n'
		percentPrecipitation += '<text style="text-anchor:end;" font-size="15px" y="580" x="180">' + str(pop[1]) +'%</text>\n'
		percentPrecipitation += '</g>\n</svg>' 
		output = output.replace('</svg>',percentPrecipitation)

	if pop[2] > 10:
		percentPrecipitation = '<g font-family="DejaVu Sans">\n'
		percentPrecipitation += '<text style="text-anchor:end;" font-size="15px" y="580" x="380">' + str(pop[2]) +'%</text>\n'
		percentPrecipitation += '</g>\n</svg>' 
		output = output.replace('</svg>',percentPrecipitation)

	if pop[3] > 10:
		percentPrecipitation = '<g font-family="DejaVu Sans">\n'
		percentPrecipitation += '<text style="text-anchor:end;" font-size="15px" y="580" x="580">' + str(pop[3]) +'%</text>\n'
		percentPrecipitation += '</g>\n</svg>' 
		output = output.replace('</svg>',percentPrecipitation)
else:
	output = codecs.open('weather-script-preprocess.svg', 'r', encoding='utf-8').read()

# Insert icons and temperatures
output = output.replace('ICON_ONE',icons[0]).replace('ICON_TWO',icons[1]).replace('ICON_THREE',icons[2]).replace('ICON_FOUR',icons[3])
output = output.replace('HIGH_ONE',str(highs[0])).replace('HIGH_TWO',str(highs[1])).replace('HIGH_THREE',str(highs[2])).replace('HIGH_FOUR',str(highs[3]))
output = output.replace('LOW_ONE',str(lows[0])).replace('LOW_TWO',str(lows[1])).replace('LOW_THREE',str(lows[2])).replace('LOW_FOUR',str(lows[3]))

# Insert days of week
one_day = datetime.timedelta(days=1)
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
now = datetime.datetime.now()
if day_one.day > now.day:
	output = output.replace('DAY_ONE','Tomorrow').replace('DAY_TWO',days_of_week[(day_one + one_day).weekday()])
else:
	output = output.replace('DAY_ONE','Today').replace('DAY_TWO','Tomorrow')
output = output.replace('DAY_THREE',days_of_week[(day_one + 2*one_day).weekday()]).replace('DAY_FOUR',days_of_week[(day_one + 3*one_day).weekday()])

# Insert processing time
output = output.replace('DATE_STRING',now.strftime('%H:%M %B %d, %Y'))

# Write output
codecs.open('weather-script-output.svg', 'w', encoding='utf-8').write(output)
