# Pi Weather Display

This project displays current and forecast weather data on a Waveshare 4.2" e-paper display using a Raspberry Pi. It uses the OpenWeatherMap API, and supports local development and testing with a mock display environment.

---

## 📁 Project Structure

```
pi-weather-display/
├── weather_display.py            # Main weather display script
├── config.json                   # Location and units config
├── api_key.txt                   # API key for OpenWeatherMap (not in Git)
├── mock_epd.py                   # Mock display class for local dev
├── assets/icons/                 # Weather icons
├── external/waveshare/           # Waveshare driver (via submodule)
├── tests/
│   ├── test_weather_display.py   # Unit + snapshot tests
│   ├── update_golden.py          # Script to update golden image
│   └── snapshots/
│       ├── golden_output.png     # Golden image for test comparison
│       └── test_output.png       # Generated snapshot from test
└── .gitignore
```

---

## 🔧 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/pi-weather-display.git
cd pi-weather-display
git submodule update --init --recursive
```

### 2. Install Requirements (On Pi or venv)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add Your API Key

Create a file named `api_key.txt` in the root:

```txt
YOUR_OPENWEATHERMAP_API_KEY
```

### 4. Configure Location and Units

Edit `config.json`:

```json
{
  "lat": 40.7293,
  "lon": -74.2583,
  "units": "imperial",
  "location_name": "Bloomfield, NJ"
}
```

---

## 🚀 Running on Raspberry Pi

```bash
python3 weather_display.py
```

## 💻 Running in Mock Mode (on Desktop)

```bash
python3 weather_display.py --mock
```

This will show the rendered output in an image viewer.

---

## 🧪 Running Tests

Run all tests including snapshot comparison:

```bash
python3 -m unittest tests/test_weather_display.py
```

To regenerate the golden image based on the current output:

```bash
python3 tests/update_golden.py
```

---

## 🛑 .gitignore Suggestions

```gitignore
__pycache__/
*.pyc
tests/snapshots/test_output.png
api_key.txt
```

---

## 📦 Requirements

* Python 3.7+
* Pillow
* requests

Install via:

```bash
pip install -r requirements.txt
```

---

## 📜 License

MIT License

---

## 🙌 Credits

* [Waveshare e-Paper Drivers](https://github.com/waveshare/e-Paper)
* OpenWeatherMap API

---

Feel free to fork and customize! PRs welcome.
