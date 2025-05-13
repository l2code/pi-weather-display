import sys
import os
import time
import requests
import json
from datetime import datetime
import logging
from PIL import Image, ImageFont, ImageDraw
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

# Import battery module
try:
    # Try to import with package name
    from pi_weather_display.battery import get_battery_status, add_battery_symbol_to_image, update_charging_history, add_last_charge_time_to_image
    battery_module_available = True
    logging.info("Battery module loaded successfully")
except ImportError:
    try:
        # Try without package name
        from battery import get_battery_status, add_battery_symbol_to_image, update_charging_history, add_last_charge_time_to_image
        battery_module_available = True
        logging.info("Battery module loaded successfully")
    except ImportError:
        battery_module_available = False
        logging.warning("Battery module not available. Battery display will be disabled.")

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

def add_battery_info(img, battery_pct):
    if battery_pct < 0:
        return img  # No valid battery percentage
    
    # Create a copy of the image to avoid modifying the original
    result = img.copy()
    draw = ImageDraw.Draw(result)
    
    # Format the battery text
    battery_text = f"Batt: {battery_pct:.1f}%"
    
    # Use the small font from fonts dictionary
    font = fonts["small"]
    
    # Calculate position in top right with some padding
    text_bbox = draw.textbbox((0, 0), battery_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Draw text in top right corner with some padding
    draw.text((img.width - text_width - 10, 10), 
              battery_text, 
              font=font, 
              fill=0)  # 0 is black for 1-bit images
    
    return result

def update_display():
    try:
        # Get weather data
        data = get_weather_data()
        
        # Initialize display
        epd = epd4in2b_V2.EPD()
        epd.init()
        epd.Clear()

        # Render template
        template = load_template(TEMPLATE_NAME)
        black_img = template.render(data, epd.width, epd.height)
        
        # Add battery information to the black image if available
        if battery_module_available:
            try:
                # Get battery status
                battery_pct, is_charging, current_mA = get_battery_status()
                
                # Update charging history
                update_charging_history(battery_pct, is_charging, current_mA)
                
                # Add battery symbol with charging indicator
                black_img = add_battery_symbol_to_image(black_img, battery_pct, is_charging, font=fonts["small"])
                logging.info(f"Added battery info: {battery_pct:.1f}%")
                
                # Add last charge time at the bottom
                black_img = add_last_charge_time_to_image(black_img, font=fonts["small"])
            except Exception as e:
                logging.error(f"Error adding battery info: {e}")
                import traceback
                logging.error(traceback.format_exc())
        
        # Create red image (empty in this case)
        red_img = Image.new("1", (epd.width, epd.height), 255)

        # Display the images
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
