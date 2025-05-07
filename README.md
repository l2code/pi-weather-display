# Pi Weather Display

This project displays current and forecast weather data on a Waveshare 4.2" e-paper display using a Raspberry Pi. It uses the OpenWeatherMap API and supports local development and testing with a mock display environment.

---

## 📁 Project Structure

```
pi-weather-display/
├── pi_weather_display/
│   ├── main.py                  # Entry point
│   ├── weather_display.py       # Core logic
│   ├── mock_epd.py              # Mock display class
│   ├── config.json              # Location and units config
│   ├── api_key.txt              # API key (ignored in Git)
│   ├── assets/icons/            # Weather icons
│   └── external/waveshare/      # Waveshare drivers
├── tests/
│   ├── test_weather_display.py  # Snapshot test
│   ├── update_golden.py         # Golden snapshot updater
│   └── snapshots/
│       ├── golden_output.png
│       └── test_output.png
├── requirements.txt
├── setup.py
└── .gitignore
```

---

## 🔧 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/pi-weather-display.git
cd pi-weather-display
```

### 2. Install Requirements

#### 💻 Local or venv (for development)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 🧑‍💻 On Raspberry Pi (system-wide install)

```bash
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt
```

### 3. Add Your API Key

Create a file `pi_weather_display/api_key.txt` with:

```
YOUR_OPENWEATHERMAP_API_KEY
```

### 4. Configure Location and Units

Edit `pi_weather_display/config.json`:

```json
{
  "lat": 40.7293,
  "lon": -74.2583,
  "units": "imperial",
  "location_name": "Bloomfield, NJ",
  "template": "classic_single_display"
}
```

---

## 🚀 Running the App

### 🖥️ On Raspberry Pi with Real Display

```bash
python3 pi_weather_display/main.py
```

### 🦪 On Any System (Mock Mode)

```bash
python3 pi_weather_display/main.py --mock
```

This uses `mock_epd.py` and logs output without needing e-Paper hardware.

---

## 🧪 Running Tests

```bash
python3 -m unittest tests/test_weather_display.py
```

To update the golden snapshot:

```bash
python3 tests/update_golden.py
```

---

## 👏 .gitignore Suggestions

```gitignore
__pycache__/
*.pyc
api_key.txt
tests/snapshots/test_output.png
pi_weather_display/external/
```

---

## 📆 Requirements

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
