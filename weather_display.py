import sys
import os
import time
import requests
import json
from datetime import datetime
import logging
from PIL import Image, ImageDraw, ImageFont
import traceback
import math

logging.basicConfig(level=logging.INFO)

libdir = '/home/rissac/e-Paper/RaspberryPi_JetsonNano/python/lib'
picdir = '/home/rissac/e-Paper/RaspberryPi_JetsonNano/python/pic'

if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd4in2b_V2

def get_api_key():
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        api_key_path = os.path.join(script_dir, 'api_key.txt')
        if not os.path.exists(api_key_path):
            logging.error("API key file not found")
            return None
        with open(api_key_path, 'r') as f:
            api_key = f.read().strip()
        if not api_key or api_key.startswith('#'):
            logging.error("API key not set correctly")
            return None
        return api_key
    except Exception as e:
        logging.error(f"Error reading API key: {e}")
        return None

API_KEY = get_api_key()
LAT = 40.7293
LON = -74.2583
UNITS = "imperial"

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_header = ImageFont.truetype(font_path, 22)
font_temp = ImageFont.truetype(font_path, 64)
font_large = ImageFont.truetype(font_path, 18)
font_medium = ImageFont.truetype(font_path, 16)
font_small = ImageFont.truetype(font_path, 12)


def get_weather_data():
    try:
        if not API_KEY:
            return None
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&units={UNITS}&appid={API_KEY}"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return None

def get_weather_icon(icon_code, size='current', is_night=False):
    suffix = '_n' if is_night else '_d'
    dimension = 80 if size == 'current' else 44
    filename = f"icon_{icon_code}_{dimension}.png"
    return os.path.join(picdir, filename)

def update_display():
    try:
        epd = epd4in2b_V2.EPD()
        epd.init()
        epd.Clear()
        black_img = Image.new('1', (epd.width, epd.height), 255)
        red_img = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(black_img)

        data = get_weather_data()
        if not data:
            draw.text((10, 10), "Weather Unavailable", font=font_header, fill=0)
        else:
            curr = data['current']
            daily = data['daily']
            dt = datetime.fromtimestamp(curr['dt'])
            sunrise = datetime.fromtimestamp(curr['sunrise'])
            sunset = datetime.fromtimestamp(curr['sunset'])
            is_night = not (sunrise <= dt <= sunset)
            update_time = dt.strftime("%I:%M %p")

            draw.rectangle((0, 0, epd.width - 1, epd.height - 1), outline=0, width=2)
            draw.text((10, 5), "Bloomfield, NJ", font=font_header, fill=0)

            draw.text((10, 28), f"{int(curr['temp'])}°F", font=font_temp, fill=0)
            icon_path = get_weather_icon(curr['weather'][0]['icon'], size='current', is_night=is_night)
            if os.path.exists(icon_path):
                icon = Image.open(icon_path).convert("L").convert("1")
                black_img.paste(icon.resize((80, 80), Image.LANCZOS), (epd.width - 90, 28))

            draw.text((10, 108), f"Feels: {int(curr['feels_like'])}°F", font=font_large, fill=0)
            draw.text((10, 130), f"Humid: {curr['humidity']}%", font=font_large, fill=0)
            draw.text((170, 108), curr['weather'][0]['description'].title(), font=font_large, fill=0)
            draw.text((170, 130), f"Wind: {int(curr['wind_speed'])} mph", font=font_large, fill=0)
            draw.text((10, 152), f"High: {int(daily[0]['temp']['max'])}°F", font=font_large, fill=0)
            draw.text((170, 152), f"Low: {int(daily[0]['temp']['min'])}°F", font=font_large, fill=0)

            days = [datetime.fromtimestamp(d['dt']).strftime('%a') for d in daily[:5]]
            cell_width = epd.width // 5
            icon_size = 44
            y_base = 195
            y_icon = y_base + 16
            y_text = y_icon + icon_size + 2

            for i, day in enumerate(days):
                x_center = i * cell_width + (cell_width // 2)
                draw.text((x_center - 15, y_base), day, font=font_medium, fill=0)
                icon_path = get_weather_icon(daily[i]['weather'][0]['icon'], size='forecast', is_night=is_night)
                if os.path.exists(icon_path):
                    icon = Image.open(icon_path).convert("L").convert("1")
                    black_img.paste(icon.resize((icon_size, icon_size), Image.LANCZOS), (x_center - icon_size // 2, y_icon))
                temp_text = f"{int(daily[i]['temp']['max'])}/{int(daily[i]['temp']['min'])}"
                temp_width = draw.textlength(temp_text, font=font_small)
                draw.text((x_center - temp_width // 2, y_text), temp_text, font=font_small, fill=0)

            updated_label = f"Updated: {update_time}"
            update_width = draw.textlength(updated_label, font=font_small)
            draw.text((epd.width - update_width - 6, epd.height - 22), updated_label, font=font_small, fill=0)

        epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))
        epd.sleep()

    except Exception as e:
        logging.error("Error updating display")
        print(traceback.format_exc())

if __name__ == '__main__':
    update_display()
