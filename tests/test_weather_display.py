import unittest
from unittest.mock import patch
from weather_display import render_weather_to_image
from PIL import Image, ImageChops
import os

# Directory-aware paths for test outputs and golden images
BASE_DIR = os.path.dirname(__file__)
SNAPSHOT_PATH = os.path.join(BASE_DIR, "snapshots", "test_output.png")
GOLDEN_PATH = os.path.join(BASE_DIR, "snapshots", "golden_output.png")

class TestWeatherSnapshot(unittest.TestCase):

    @patch('weather_display.get_weather_data')
    def test_snapshot_matches_golden(self, mock_get_data):
        # Provide mock weather data
        mock_get_data.return_value = {
            "current": {
                "dt": 1700000000,
                "temp": 72,
                "feels_like": 71,
                "humidity": 60,
                "wind_speed": 5,
                "weather": [{"icon": "01d", "description": "clear sky"}],
                "sunrise": 1699990000,
                "sunset": 1700030000
            },
            "daily": [{
                "dt": 1700000000 + i * 86400,
                "temp": {
                    "min": 50 + i, 
                    "max": 65 + i,
                    "morn": 58 + i,
                    "day": 63 + i,
                    "eve": 61 + i,
                    "night": 52 + i
                },
                "feels_like": {
                    "morn": 56 + i,
                    "day": 62 + i,
                    "eve": 59 + i,
                    "night": 50 + i
                },
                "weather": [{"icon": "01d", "description": "clear sky", "main": "Clear"}],
                "pop": 0.1,
                "humidity": 60,
                "wind_speed": 5 + i,
                "sunrise": 1699990000 + i * 86400,
                "sunset": 1700030000 + i * 86400
            } for i in range(6)]
        }

        # Generate test output
        black_img, _ = render_weather_to_image(mock_get_data.return_value)

        # Save snapshot image
        os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
        black_img.save(SNAPSHOT_PATH)
        self.assertTrue(os.path.exists(SNAPSHOT_PATH))
        print(f"✅ Snapshot saved to: {SNAPSHOT_PATH}")

        # Compare with golden image
        self.assertTrue(os.path.exists(GOLDEN_PATH), f"Golden image not found at {GOLDEN_PATH}")
        generated = Image.open(SNAPSHOT_PATH).convert("RGB")
        golden = Image.open(GOLDEN_PATH).convert("RGB")
        diff = ImageChops.difference(generated, golden)

        self.assertIsNone(diff.getbbox(), "❌ Snapshot image does not match golden image!")

if __name__ == '__main__':
    unittest.main()
