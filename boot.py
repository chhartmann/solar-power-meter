import json
import time
import math
from machine import Pin
import neopixel
from umqtt.simple import MQTTClient
import gc
import network

# Configuration file
CONFIG_FILE = 'config.json'
TOPIC_SOLAR_METER = "tele/balkonkraftwerk/SENSOR"
TOPIC_POWER_METER = "tele/heizung/RESULT"
TOPIC_HOT_WATER = "tele/solarthermie/RESULT"

class SolarPowerMeter:
    def __init__(self):
        # Stage 1: Power on, set first LED yellow
        self.config = self.load_config()
        self.np = neopixel.NeoPixel(
            Pin(self.config['neopixel']['pin']), 
            self.config['neopixel']['num_leds']
        )
        self.brightness = self.config['neopixel']['brightness']

        self.clear_leds()
        self.np[0] = self._apply_brightness((255, 255, 255))  # White - power on
        self.np.write()

        # Stage 2: Config file read, set second LED yellow
        self.np[1] = self._apply_brightness((255, 255, 0))  # Yellow - config file read
        self.np.write()

        # Network
        self.wlan = None
        self.wifi_connected = False

        # MQTT data
        self.solar_power = 0
        self.power_usage = 0
        self.hot_water_temp = 0
        self.last_mqtt_time = time.time()
        self.mqtt_timeout = 60  # 1 minute timeout

        # MQTT client
        self.client = None
        self.mqtt_connected = False

        # Stage 3: WiFi connection
        self.setup_wifi()
        if self.wifi_connected:
            self.np[2] = self._apply_brightness((0, 255, 0))  # Red - WiFi connected
            self.np.write()

        # Stage 4: MQTT connection
        if self.wifi_connected:
            self.setup_mqtt()
            if self.mqtt_connected:
                self.np[3] = self._apply_brightness((0, 0, 255))  # Blue - MQTT connected
                self.np.write()
                time.sleep(0.5)
                self.clear_leds()

    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config
        except (OSError, ValueError):
            print("Config file not found or invalid, aborting startup")
            raise
    
    def setup_mqtt(self):
        """Setup MQTT client and subscriptions"""
        try:
            mqtt_config = self.config['mqtt']
            use_tls = mqtt_config.get('use_tls', False)
            # Default ports if not explicitly set in config
            port = mqtt_config.get('port', 8883 if use_tls else 1883)
            # Provide minimal SSL params for SNI when using hostnames
            ssl_params = {"server_hostname": mqtt_config['server']} if use_tls else {}
            self.client = MQTTClient(
                mqtt_config['client_id'],
                mqtt_config['server'],
                port=port,
                user=mqtt_config['username'] if mqtt_config['username'] else None,
                password=mqtt_config['password'] if mqtt_config['password'] else None,
                ssl=use_tls,
                ssl_params=ssl_params
            )
            
            # Set callback for incoming messages
            self.client.set_callback(self.mqtt_callback)
            
            # Connect to MQTT server
            self.client.connect()
            print("Connected to MQTT server")
            self.mqtt_connected = True
            
            # Subscribe to topics
            self.client.subscribe(TOPIC_SOLAR_METER)
            self.client.subscribe(TOPIC_POWER_METER)
            print("Subscribed to MQTT topics")
            
        except Exception as e:
            print(f"MQTT setup failed: {e}")
            self.client = None
            self.mqtt_connected = False

    def setup_wifi(self):
        """Connect to WiFi using config credentials."""
        try:
            wifi_cfg = self.config.get('wifi', {})
            ssid = wifi_cfg.get('ssid') or ""
            password = wifi_cfg.get('password') or ""
            hostname = wifi_cfg.get('hostname') or None

            if not ssid:
                print("WiFi SSID not configured; skipping WiFi connection")
                self.wifi_connected = False
                return

            if self.wlan is None:
                self.wlan = network.WLAN(network.STA_IF)
                # Set hostname BEFORE activating interface
                if hostname:
                    try:
                        self.wlan.config(hostname=hostname)
                        print(f"WiFi hostname set to: {hostname}")
                    except Exception as e:
                        print(f"Failed to set WiFi hostname: {e}")
                self.wlan.active(True)
            else:
                if not self.wlan.active():
                    self.wlan.active(True)

            if not self.wlan.isconnected():
                print(f"Connecting to WiFi SSID '{ssid}'...")
                self.wlan.connect(ssid, password)

                # Wait for connection with timeout
                start = time.time()
                timeout_seconds = 15
                while not self.wlan.isconnected() and (time.time() - start) < timeout_seconds:
                    time.sleep(0.1)

            self.wifi_connected = self.wlan.isconnected()
            if self.wifi_connected:
                print("WiFi connected, IP:", self.wlan.ifconfig()[0])
            else:
                print("WiFi connection failed")
        except Exception as e:
            print(f"WiFi setup error: {e}")
            self.wifi_connected = False
    
    def mqtt_callback(self, topic, msg):
        """Callback for MQTT messages"""
        try:
            topic_str = topic.decode('utf-8')
            value = json.loads(msg.decode('utf-8'))

            if topic_str == TOPIC_SOLAR_METER:
                self.solar_power = int(value["ENERGY"]["Power"])
                print(f"Received solar power: {self.solar_power} W")
            elif topic_str == TOPIC_POWER_METER:
                self.power_usage = int(value["1-0:16.7.0*255"]["value"])
                print(f"Received power usage: {self.power_usage} W")
            elif topib_str == TOPIC_HOT_WATER:
                self.hot_water_temp = int(value["temperature"]["value"])
                print(f"Received hot water temperature: {self.hot_water_temp} °C")
            
            self.last_mqtt_time = time.time()
            
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
    
    def _apply_brightness(self, color_rgb_tuple):
        """Scale a (r,g,b) tuple by brightness (0-100)."""
        factor = max(0, min(1, self.brightness / 100))
        r, g, b = color_rgb_tuple
        return (int(r * factor), int(g * factor), int(b * factor))

    def _blink_first_led(self, color_rgb_tuple):
        """Blink the first LED with the given color; clear others."""
        current_time = time.time()
        if int(current_time) % 2 == 0:
            self.np[0] = self._apply_brightness(color_rgb_tuple)
        else:
            self.np[0] = (0, 0, 0)

        for i in range(1, self.config['neopixel']['num_leds']):
            self.np[i] = (0, 0, 0)
        self.np.write()
        
    def update_led_display(self):
        """Update the LED display based on current values"""
        current_time = time.time()
        
        # Priority of error indication:
        # 1) WiFi not connected -> blink green
        if not self.wifi_connected:
            self._blink_first_led((0, 255, 0))
            return

        # 2) MQTT not connected -> blink blue
        if not self.mqtt_connected:
            self._blink_first_led((0, 0, 255))
            return

        # 3) MQTT connected but no data for timeout -> blink red
        if (current_time - self.last_mqtt_time) > self.mqtt_timeout:
            self._blink_first_led((255, 0, 0))
            return

        available_leds = self.np.n
        leds_power_generatated = round(min(self.solar_power, 600) / 600 * available_leds)
        leds_power_available = 0
        if (self.power_usage < 0):
            leds_power_available = abs(round(min(self.power_usage,600) / 600 * available_leds))

        leds_power_consumption = leds_power_generatated - leds_power_available

        for i in range(available_leds):
            if i < leds_power_consumption:
                self.np[i] = (int(255 * self.brightness / 100), 0, 0)
            elif i < (leds_power_consumption + leds_power_available):
                self.np[i] = (0, int(255 * self.brightness / 100), 0)
            else:
                self.np[i] = (0, 0, 0)  # Clear remaining LEDs        
        
        self.np.write()
    
    def run(self):
        """Main loop"""
        print("Solar Power Meter started")
        
        last_wifi_retry = 0
        last_mqtt_retry = 0

        while True:
            try:
                # Maintain WiFi connection
                if self.wlan is not None:
                    self.wifi_connected = self.wlan.isconnected()

                if not self.wifi_connected and (time.time() - last_wifi_retry) > 5:
                    last_wifi_retry = time.time()
                    self.setup_wifi()

                # Maintain/attempt MQTT connection when WiFi is up
                if self.wifi_connected:
                    if not self.mqtt_connected and (time.time() - last_mqtt_retry) > 5:
                        last_mqtt_retry = time.time()
                        self.setup_mqtt()

                # Check for MQTT messages
                if self.client and self.mqtt_connected:
                    try:
                        self.client.check_msg()
                    except Exception as e:
                        print(f"MQTT check_msg error: {e}")
                        self.mqtt_connected = False
                        try:
                            self.client.disconnect()
                        except Exception:
                            pass
                        self.client = None
                
                # Update LED display
                self.update_led_display()
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
                # Garbage collection
                if gc.mem_free() < 10000:
                    gc.collect()
                    
            except Exception as e:
                time.sleep(1)

# Create and run the application
if __name__ == '__main__':
    app = SolarPowerMeter()
    app.run()
