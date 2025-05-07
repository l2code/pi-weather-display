from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

class ClassicSingleDisplay:
    def __init__(self, fonts, icons_path, location_name):
        self.fonts = fonts
        self.icons_path = icons_path
        self.location_name = location_name

    def get_weather_icon(self, icon_code, size='current', is_night=False):
        dimension = 80 if size == 'current' else 44
        filename = f"icon_{icon_code}_{dimension}.png"
        return os.path.join(self.icons_path, filename)

    def draw_header(self, draw, width, height):
        draw.rectangle((0, 0, width - 1, height - 1), outline=0, width=2)
        draw.text((10, 5), self.location_name, font=self.fonts["header"], fill=0)

    def draw_current_conditions(self, draw, curr, daily, width, is_night, black_img):
        draw.text((10, 28), f"{int(curr['temp'])}°F", font=self.fonts["temp"], fill=0)

        icon_path = self.get_weather_icon(curr['weather'][0]['icon'], size='current', is_night=is_night)
        if os.path.exists(icon_path):
            icon = Image.open(icon_path).convert("L").convert("1")
            black_img.paste(icon.resize((80, 80), Image.LANCZOS), (width - 90, 28))

        draw.text((10, 108), f"Feels: {int(curr['feels_like'])}°F", font=self.fonts["large"], fill=0)
        draw.text((10, 130), f"Humid: {curr['humidity']}%", font=self.fonts["large"], fill=0)
        draw.text((170, 108), curr['weather'][0]['description'].title(), font=self.fonts["large"], fill=0)
        draw.text((170, 130), f"Wind: {int(curr['wind_speed'])} mph", font=self.fonts["large"], fill=0)
        draw.text((10, 152), f"High: {int(daily[0]['temp']['max'])}°F", font=self.fonts["large"], fill=0)
        draw.text((170, 152), f"Low: {int(daily[0]['temp']['min'])}°F", font=self.fonts["large"], fill=0)

    def draw_forecast(self, draw, daily, width, is_night, black_img):
        days = [datetime.fromtimestamp(d['dt']).strftime('%a') for d in daily[:5]]
        cell_width = width // 5
        icon_size = 44
        y_base = 195
        y_icon = y_base + 16
        y_text = y_icon + icon_size + 2

        for i, day in enumerate(days):
            x_center = i * cell_width + (cell_width // 2)
            draw.text((x_center - 15, y_base), day, font=self.fonts["medium"], fill=0)
            icon_path = self.get_weather_icon(daily[i]['weather'][0]['icon'], size='forecast', is_night=is_night)
            if os.path.exists(icon_path):
                icon = Image.open(icon_path).convert("L").convert("1")
                black_img.paste(icon.resize((icon_size, icon_size), Image.LANCZOS), (x_center - icon_size // 2, y_icon))
            temp_text = f"{int(daily[i]['temp']['max'])}/{int(daily[i]['temp']['min'])}"
            temp_width = draw.textlength(temp_text, font=self.fonts["small"])
            draw.text((x_center - temp_width // 2, y_text), temp_text, font=self.fonts["small"], fill=0)

    def draw_update_time(self, draw, update_time, width, height):
        updated_label = f"Updated: {update_time}"
        update_width = draw.textlength(updated_label, font=self.fonts["small"])
        draw.text((width - update_width - 6, height - 22), updated_label, font=self.fonts["small"], fill=0)

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

        self.draw_header(draw, width, height)
        self.draw_current_conditions(draw, curr, daily, width, is_night, black_img)
        self.draw_forecast(draw, daily, width, is_night, black_img)
        self.draw_update_time(draw, update_time, width, height)

        return black_img
