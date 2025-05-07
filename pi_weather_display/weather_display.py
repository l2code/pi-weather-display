import sys
import os
import time
import requests
import json
from datetime import datetime
import logging
from PIL import Image, ImageFont
import traceback
import argparse
from importlib import import_module

logging.basicConfig(level=logging.INFO)

args = None
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weather Display")
    parser.add_argument('--mock', action='store_true', help='Use mock display instead of real Waveshare e-Paper')
    args = parser.parse_args()
else:
    class Args:
        mock = False
    args = Args()

script_dir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(script_dir, 'external', 'waveshare', 'RaspberryPi_JetsonNano', 'python', 'lib')
picdir = os.path.join(script_dir, 'assets', 'icons')

template_dir = os.path.join(script_dir, 'templates')
sys.path.append(template_dir)

if os.path.exists(libdir):
    sys.path.append(libdir)

if args.mock:
    print("[INFO] Mock mode enabled")
    from pi_weather_display.mock_epd import EPD
    class epd4in2b_V2:
        EPD = EPD
else:
    try:
        from waveshare_epd import epd4in2b_V2
    except (ImportError, OSError, AttributeError):
        print("[WARNING] Hardware import failed, falling back to mock mode")
        from pi_weather_display.mock_epd import EPD
        class epd4in2b_V2:
            EPD = EPD

def get_api_key():
    try:
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
        logging.critical(f"API key error: {e}")
        sys.exit(1)

API_KEY = get_api_key()

def load_config():
    try:
        config_path = os.path.join(script_dir, 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.critical(f"Failed to load config.json: {e}")
        sys.exit(1)

config = load_config()
LAT = config.get('lat')
LON = config.get('lon')
UNITS = config.get('units', 'imperial')
LOCATION_NAME = config.get('location_name', 'Unknown Location')
TEMPLATE_NAME = config.get('template', 'classic_single_display')

URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&units={UNITS}&appid={API_KEY}"

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fonts = {
    "header": ImageFont.truetype(font_path, 22),
    "temp": ImageFont.truetype(font_path, 64),
    "large": ImageFont.truetype(font_path, 18),
    "medium": ImageFont.truetype(font_path, 16),
    "small": ImageFont.truetype(font_path, 12),
}

def get_weather_data():
    try:
        if not API_KEY:
            return None
        response = requests.get(URL)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return None

def load_template(template_name):
    try:
        module = import_module(template_name)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and hasattr(attr, 'render'):
                return attr(fonts=fonts, icons_path=picdir, location_name=LOCATION_NAME)
        raise ImportError(f"No valid template class found in module '{template_name}'")
    except ModuleNotFoundError:
        logging.warning(f"Template '{template_name}' not found. Falling back to 'split_am_pm'.")
        import split_am_pm as fallback
        return fallback.SplitAmPmTemplate(fonts=fonts, icons_path=picdir, location_name=LOCATION_NAME)
    except Exception as e:
        logging.critical(f"Failed to load template '{template_name}': {e}")
        sys.exit(1)

def update_display():
    try:
        data = get_weather_data()
        epd = epd4in2b_V2.EPD()
        epd.init()
        epd.Clear()

        template = load_template(TEMPLATE_NAME)
        black_img = template.render(data, epd.width, epd.height)
        red_img = Image.new("1", (epd.width, epd.height), 255)

        epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))
        epd.sleep()
    except Exception as e:
        logging.error("Error updating display")
        logging.error(traceback.format_exc())

def run_display(use_mock=False):
    global args
    args.mock = use_mock
    update_display()

if __name__ == '__main__':
    update_display()
