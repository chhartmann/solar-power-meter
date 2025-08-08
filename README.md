# Solar Power Meter

A MicroPython-based solar power and energy usage monitor using NeoPixel LEDs and MQTT.

## Features
- Displays solar power and power usage on LED strip
- Connects to WiFi and MQTT broker
- Configurable via `config.json`

## Usage
1. Configure WiFi, MQTT, and NeoPixel settings in `config.json`.
2. Flash `boot.py` to your device.
3. Power on and monitor LED status.

## Notes
- `config.json` is ignored by git for security.
- Designed for ESP32/ESP8266 with MicroPython.
