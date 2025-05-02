#!/usr/bin/env python3

# Kindle Weather Display
# Originally by Matthew Petroff (http://www.mpetroff.net/)
# Modified by John Kua (http://john.kua.fm)

import urllib.request
import urllib.error
import json
import datetime
import codecs
import sys
import ephem

def getWebpage(url):
	try:
		response = urllib.request.urlopen(url)
		webpage = response.read().decode('utf-8')
	except urllib.error.URLError as e:
		print(f"Error opening URL: {e}")
	except Exception as e:
		print(f"An unexpected error occurred: {e}")

	return webpage


class WeatherData:
	def __init__(self):
		self.latitude = None
		self.longitude = None
		self.timezone = None
		self.temperature_unit = None
		self.precipitation_unit = None
		self.wind_speed_unit = None

		self.forecast_retrieval_time = None
		self.forecast_source = ''
		self.date = None
		self.weather_code = None
		self.temperature_high = None
		self.temperature_low = None
		self.temperature_current = None
		self.precipitation_probability_max = None
		self.precipitation_probability_day = None
		self.precipitation_probability_night = None
		self.wind_speed = None
		self.wind_direction = None
		self.sunrise = None
		self.sunset = None
		self.moon_phase = None
		self.moon_age = None

	def compute_moon_info(self):
		if self.date is None or self.latitude is None or self.longitude is None:
			return

		# Create observer object for the given date and location
		observer = ephem.Observer()
		observer.lat = str(self.latitude)
		observer.lon = str(self.longitude)
		observer.date = self.date

		# Get the moon phase and age
		self.moon_phase = ephem.Moon(observer).phase

		date_ephem = ephem.Date(self.date)
		previous_new_moon = ephem.previous_new_moon(date_ephem)
		self.moon_age = date_ephem - previous_new_moon

	@staticmethod
	def get_from_open_meteo(latitude, longitude, timezone='America/Los_Angeles', temperature_unit='fahrenheit', precipitation_unit='inch', wind_speed_unit='mph'):
		url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude:4f}&longitude={longitude:.4f}'
		url += '&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code,sunrise,sunset,wind_speed_10m_max,wind_direction_10m_dominant'
		url += '&hourly=precipitation_probability,is_day'
		url += '&current=temperature_2m'
		url += f'&timezone={timezone}&wind_speed_unit={wind_speed_unit}&temperature_unit={temperature_unit}&precipitation_unit={precipitation_unit}'

		webpage = getWebpage(url)
		response_data = json.loads(webpage)
		forecast_retrieval_time = datetime.datetime.now()

		# Compute day/night max precipitation probabilities
		max_precipitation_probabilities_day = []
		max_precipitation_probabilities_night = []

		state = 'START'
		for time_string, is_day, precipitation_probability in zip(response_data['hourly']['time'], response_data['hourly']['is_day'], response_data['hourly']['precipitation_probability']):
			if state == 'START':
				if not is_day:
					continue
				else:
					state = 'DAY'
					max_precipitation_probabilities_day.append(0)
			elif state == 'DAY':
				if is_day:
					if precipitation_probability > max_precipitation_probabilities_day[-1]:
						max_precipitation_probabilities_day[-1] = precipitation_probability
				else:
					state = 'NIGHT'
					max_precipitation_probabilities_night.append(0)
			elif state == 'NIGHT':
				if not is_day:
					if precipitation_probability > max_precipitation_probabilities_night[-1]:
						max_precipitation_probabilities_night[-1] = precipitation_probability
				else:
					state = 'DAY'
					max_precipitation_probabilities_day.append(0)

		# Save daily forecasts
		daily_forecasts = []
		for i in range(len(response_data['daily']['time'])):
			forecast = WeatherData()
			forecast.latitude = latitude
			forecast.longitude = longitude
			forecast.timezone = timezone
			forecast.temperature_unit = temperature_unit
			forecast.precipitation_unit = precipitation_unit
			forecast.wind_speed_unit = wind_speed_unit

			forecast.forecast_retrieval_time = forecast_retrieval_time
			forecast.forecast_source = 'Open-Meteo'
			
			if i == 0:
				forecast.temperature_current = response_data['current']['temperature_2m']
				
			forecast.date = datetime.date.fromisoformat(response_data['daily']['time'][i])
			forecast.weather_code = response_data['daily']['weather_code'][i]
			forecast.temperature_high = response_data['daily']['temperature_2m_max'][i]
			forecast.temperature_low = response_data['daily']['temperature_2m_min'][i]
			forecast.precipitation_probability_max = response_data['daily']['precipitation_probability_max'][i]
			forecast.precipitation_probability_day = max_precipitation_probabilities_day[i]
			forecast.precipitation_probability_night = max_precipitation_probabilities_night[i]
			forecast.sunrise = datetime.datetime.fromisoformat(response_data['daily']['sunrise'][i])
			forecast.sunset = datetime.datetime.fromisoformat(response_data['daily']['sunset'][i])
			forecast.wind_speed = response_data['daily']['wind_speed_10m_max'][i]
			forecast.wind_direction = response_data['daily']['wind_direction_10m_dominant'][i]

			forecast.compute_moon_info()

			daily_forecasts.append(forecast)

		return daily_forecasts


def update_weather_svg(daily_forecasts):
	icon_dict = {0: 'skc', 1: 'sct', 2: 'bkn', 3: 'ovc', 
			    45: 'fg', 48: 'fg',
			    51: 'ra', 53: 'ra', 55: 'ra',
			    56: 'ip', 57: 'ip',
			    61: 'ra', 63: 'ra', 65: 'ra',
			    66: 'ip', 67: 'ip',
			    71: 'sn', 73: 'sn', 75: 'sn',
			    77: 'sn',
			    80: 'ra', 81: 'ra', 82: 'ra',
			    85: 'sn', 86: 'sn',
			    95: 'tsra', 96: 'tsra', 99: 'tsra'}

	# Open SVG to process
	output = codecs.open('weather-script-preprocess.svg', 'r', encoding='utf-8').read()
	output = output.replace('TEMP_NOW', f'{daily_forecasts[0].temperature_current:.0f}')
	output = output.replace('SUNRISE', daily_forecasts[0].sunrise.strftime('%-I:%M'))
	output = output.replace('SUNSET', daily_forecasts[0].sunset.strftime('%-I:%M'))
	output = output.replace('MOON_ILLUMINATION', str(int(round(daily_forecasts[0].moon_phase))))
	output = output.replace('MOON_AGE', str(int(daily_forecasts[0].moon_age)))
	output = output.replace('WIND_SPEED', f'{daily_forecasts[0].wind_speed:.0f}')
	output = output.replace('WIND_DIR', f'{daily_forecasts[0].wind_direction:0.0f}°')

	output = output.replace('WEATHER_SOURCE', daily_forecasts[0].forecast_source)
	output = output.replace('DATE_STRING', daily_forecasts[0].forecast_retrieval_time.strftime('%H:%M %B %-d, %Y'))

	number_words = ['ONE', 'TWO', 'THREE', 'FOUR']

	for number_word, forecast in zip(number_words, daily_forecasts):
		print(f'Processing forecast for {number_word}: {forecast.date} - High: {forecast.temperature_high}, Low: {forecast.temperature_low}, Weather Code: {forecast.weather_code}')
		output = output.replace(f'ICON_{number_word}', icon_dict[forecast.weather_code])
		output = output.replace(f'HIGH_{number_word}', f'{forecast.temperature_high:.0f}')
		output = output.replace(f'LOW_{number_word}', f'{forecast.temperature_low:.0f}')

		if number_word != 'ONE':
			if number_word == 'TWO':
				day_name = 'Tomorrow'
			else:
				day_name = forecast.date.strftime('%A')
			output = output.replace(f'DAY_{number_word}', day_name)

		if forecast.precipitation_probability_max > 10:
			percent_precip_svg = '<g font-family="DejaVu Sans">\n'
			if number_word == 'ONE':
				percent_precip_svg += '<text style="text-anchor:end;" font-size="20px" y="300" x="380">Day: ' + str(forecast.precipitation_probability_day) +'%</text>\n'
				percent_precip_svg += '<text style="text-anchor:end;" font-size="20px" y="325" x="380">Night: ' + str(forecast.precipitation_probability_night) +'%</text>\n'
			elif number_word == 'TWO':
				percent_precip_svg += '<text style="text-anchor:end;" font-size="15px" y="580" x="180">' + str(forecast.precipitation_probability_max) +'%</text>\n'
			elif number_word == 'THREE':
				percent_precip_svg += '<text style="text-anchor:end;" font-size="15px" y="580" x="380">' + str(forecast.precipitation_probability_max) +'%</text>\n'
			elif number_word == 'FOUR':
				percent_precip_svg += '<text style="text-anchor:end;" font-size="15px" y="580" x="580">' + str(forecast.precipitation_probability_max) +'%</text>\n'
			percent_precip_svg += '</g>\n</svg>' 
			output = output.replace('</svg>',percent_precip_svg)

	codecs.open('weather-script-output.svg', 'w', encoding='utf-8').write(output)


if __name__=='__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('latitude', type=float, default=37.0, help='Latitude of the location (default: 37.0)')
	parser.add_argument('longitude', type=float, default=-122.0, help='Longitude of the location (default: -122.0)')
	parser.add_argument('timezone', type=str, default='America/Los_Angeles', help='Timezone of the location (default: America/Los_Angeles)')
	args = parser.parse_args()

	daily_forecasts = WeatherData.get_from_open_meteo(args.latitude, args.longitude, timezone=args.timezone)

	update_weather_svg(daily_forecasts)
