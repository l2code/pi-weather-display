# pi_weather_display/main.py

import sys
import os

# Allow top-level project dir to be added to sys.path when run directly
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pi_weather_display.weather_display import run_display

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mock', action='store_true', help='Run in mock display mode')
    args = parser.parse_args()

    run_display(use_mock=args.mock)

if __name__ == "__main__":
    main()
