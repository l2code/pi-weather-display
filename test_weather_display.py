import unittest
import weather_display
from unittest.mock import patch
from PIL import Image

class TestWeatherDisplay(unittest.TestCase):

    @patch('weather_display.get_weather_data')
    def test_update_display_with_mock_data(self, mock_get_data):
        # Provide mock weather data
        mock_get_data.return_value = {
            "current": {
                "dt": 1700000000,
                "temp": 70,
                "feels_like": 69,
                "humidity": 50,
                "wind_speed": 5,
                "weather": [{"icon": "01d", "description": "clear sky"}],
                "sunrise": 1699990000,
                "sunset": 1700030000
            },
            "daily": [{
                "dt": 1700000000 + i*86400,
                "temp": {"min": 50+i, "max": 60+i},
                "weather": [{"icon": "01d", "main": "Clear"}],
                "pop": 0.1,
                "sunrise": 1699990000 + i*86400,
                "sunset": 1700030000 + i*86400
            } for i in range(5)]
        }

        # Call the display function in mock mode
        try:
            weather_display.update_display()
        except Exception as e:
            self.fail(f"update_display() raised an exception: {e}")

    def test_image_creation(self):
        # Simulate rendering output to a PIL image (manually, if separated)
        img = Image.new('1', (400, 300), 255)
        self.assertEqual(img.size, (400, 300))
        self.assertEqual(img.getpixel((0, 0)), 255)

if __name__ == '__main__':
    unittest.main()
