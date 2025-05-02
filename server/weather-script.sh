#!/bin/sh

cd "$(dirname "$0")"
PATH=$PATH:/home/jkua/bin
# Oakland
python3 weather-script.py 37.811645 -122.264835 America/Los_Angeles

cp -f weather-script-output.svg /home/jkua/john.kua.fm/kindle-weather/weather-script-output.svg
cairosvg weather-script-output.svg -b white -o weather-script-output.png
pngcrush -c 0 -ow weather-script-output.png
cp -f weather-script-output.png /home/jkua/john.kua.fm/kindle-weather/weather-script-output.png
