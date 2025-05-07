from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import datetime
import os

class SplitAmPmTemplate:
    def __init__(self, fonts, icons_path, location_name):
        self.fonts = fonts
        self.icons_path = icons_path
        self.location_name = location_name

    def get_weather_icon(self, icon_code, size='current', is_night=False):
        dimension = 80 if size == 'current' else 44
        suffix = '_n' if is_night else '_d'
        filename = f"icon_{icon_code}_{dimension}.png"
        icon_path = os.path.join(self.icons_path, filename)
        return icon_path

    def draw_header(self, draw, width):
        today_str = datetime.now().strftime("%a, %b %d")
        draw.text((10, 5), f"{self.location_name}        {today_str}", font=self.fonts["header"], fill=0)

    def draw_current_conditions(self, draw, morning_data, evening_data, daily, width, is_night, black_img):
        center_x = width // 2

        draw.text((12, 35), "AM", font=self.fonts["medium"], fill=0)
        draw.text((10, 52), f"{int(morning_data['temp'])}°", font=self.fonts["temp"], fill=0)
        icon_path = self.get_weather_icon(morning_data['weather']['icon'], size='current', is_night=False)
        if os.path.exists(icon_path):
            icon = Image.open(icon_path).convert("L").convert("1")
            icon_size = 60
            black_img.paste(icon.resize((icon_size, icon_size), Image.LANCZOS), (center_x - 70, 40))

        draw.text((center_x + 12, 35), "PM", font=self.fonts["medium"], fill=0)
        draw.text((center_x + 10, 52), f"{int(evening_data['temp'])}°", font=self.fonts["temp"], fill=0)
        icon_path = self.get_weather_icon(evening_data['weather']['icon'], size='current', is_night=True)
        if os.path.exists(icon_path):
            icon = Image.open(icon_path).convert("L").convert("1")
            icon_size = 60
            black_img.paste(icon.resize((icon_size, icon_size), Image.LANCZOS), (width - 70, 40))

        y_base = 120
        draw.text((10, y_base+10), morning_data['weather']['description'].title(), font=self.fonts["medium"], fill=0)
        draw.text((center_x + 10, y_base+10), evening_data['weather']['description'].title(), font=self.fonts["medium"], fill=0)
        draw.text((10, y_base + 30), f"High {int(daily[0]['temp']['max'])}°F / Low {int(daily[0]['temp']['min'])}°F", font=self.fonts["medium"], fill=0)

    def draw_forecast(self, draw, daily, width, is_night, black_img):
        days = [datetime.fromtimestamp(d['dt']).strftime('%a') for d in daily[1:6]]
        cell_width = width // 5
        icon_size = 44
        y_base = 210
        y_icon = y_base + 18
        y_text = y_icon + icon_size + 2

        for i, day in enumerate(days):
            x_center = i * cell_width + (cell_width // 2)
            draw.text((x_center - 20, y_base-25), day, font=self.fonts["large"], fill=0)
            icon_path = self.get_weather_icon(daily[i+1]['weather'][0]['icon'], size='forecast', is_night=is_night)
            if os.path.exists(icon_path):
                icon = Image.open(icon_path).convert("L").convert("1")
                black_img.paste(icon.resize((icon_size, icon_size), Image.LANCZOS), (x_center - icon_size // 2, y_icon-20))
            temp_text = f"{int(daily[i+1]['temp']['max'])}/{int(daily[i+1]['temp']['min'])}"
            temp_width = draw.textlength(temp_text, font=self.fonts["small"])
            draw.text((x_center - temp_width // 2, y_text-15), temp_text, font=self.fonts["small"], fill=0)

    def draw_update_time(self, draw, update_time, width, height):
        updated_label = f"Updated: {update_time}"
        update_width = draw.textlength(updated_label, font=self.fonts["small"])
        draw.text((width - update_width - 6, height - 18), updated_label, font=self.fonts["small"], fill=0)

    def render(self, data, width, height):
        black_img = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(black_img)

        if not data:
            draw.text((10, 10), "Weather Unavailable", font=self.fonts["header"], fill=0)
            return black_img

        curr = data['current']
        daily = data['daily']
        dt = datetime.fromtimestamp(curr['dt'])
        sunrise = datetime.fromtimestamp(curr['sunrise'])
        sunset = datetime.fromtimestamp(curr['sunset'])
        is_night = not (sunrise <= dt <= sunset)
        update_time = dt.strftime("%I:%M %p")

        morning_data = {
            'temp': daily[0]['temp'].get('morn', daily[0]['temp']['day']),
            'weather': daily[0]['weather'][0],
        }

        evening_data = {
            'temp': daily[0]['temp'].get('eve', daily[0]['temp']['day']),
            'weather': daily[0]['weather'][0],
        }

        self.draw_header(draw, width)
        self.draw_current_conditions(draw, morning_data, evening_data, daily, width, is_night, black_img)
        self.draw_forecast(draw, daily, width, is_night, black_img)
        self.draw_update_time(draw, update_time, width, height)

        return black_img
