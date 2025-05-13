from PIL import Image, ImageDraw, ImageFont
import os
import logging

# Try to import battery module
try:
    from pi_weather_display.battery import get_battery_percentage, add_battery_symbol_to_image
    battery_module_available = True
except ImportError:
    try:
        from battery import get_battery_percentage, add_battery_symbol_to_image
        battery_module_available = True
    except ImportError:
        battery_module_available = False
        logging.warning("Battery module not available in mock_epd")

SHOW_IMAGE = os.environ.get("SHOW_IMAGE", "1") == "1"

class EPD:
    width = 400
    height = 300

    def __init__(self):
        self._font = None
        try:
            # Try to load the same font used in the main application
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            self._font = ImageFont.truetype(font_path, 12)
        except (IOError, OSError):
            # Fallback to default
            self._font = ImageFont.load_default()

    def init(self):
        print("[MOCK] epd.init()")

    def Clear(self):
        print("[MOCK] epd.Clear()")

    def getbuffer(self, image):
        return image

    def display(self, black_img, red_img=None):
        print("[MOCK] Display called.")
        
        # Convert to RGB for display
        try:
            # Create an RGB image for display
            img = Image.new("RGB", (self.width, self.height), "white")
            if black_img is not None:
                img.paste(black_img.convert("RGB"))
            
            # Display the image
            if SHOW_IMAGE:
                img.show()
                print("[MOCK] Image displayed in viewer")
        except Exception as e:
            print(f"[MOCK] Error displaying image: {e}")

    def sleep(self):
        print("[MOCK] epd.sleep()")