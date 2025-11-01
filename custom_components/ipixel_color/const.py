"""Constants for the iPixel Color integration."""
from typing import Final

DOMAIN: Final = "ipixel_color"

# Configuration keys
CONF_DEVICE_ADDRESS: Final = "device_address"
CONF_DEVICE_NAME: Final = "device_name"
CONF_DISPLAY_WIDTH: Final = "display_width"
CONF_DISPLAY_HEIGHT: Final = "display_height"
CONF_UPDATE_INTERVAL: Final = "update_interval"

# Default values
DEFAULT_UPDATE_INTERVAL: Final = 30
DEFAULT_WIDTH: Final = 32
DEFAULT_HEIGHT: Final = 32

# BLE characteristics (UUID-k)
SERVICE_UUID: Final = "0000fff0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_WRITE: Final = "0000fff3-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_NOTIFY: Final = "0000fff4-0000-1000-8000-00805f9b34fb"
