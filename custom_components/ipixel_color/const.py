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

# BLE characteristics
SERVICE_UUID: Final = "0000fff0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_WRITE: Final = "0000fff3-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_NOTIFY: Final = "0000fff4-0000-1000-8000-00805f9b34fb"

# Display modes
DISPLAY_MODE_TEXT: Final = "text"
DISPLAY_MODE_IMAGE: Final = "image"
DISPLAY_MODE_CLOCK: Final = "clock"
DISPLAY_MODE_ANIMATION: Final = "animation"
DISPLAY_MODE_DIY: Final = "diy"
DISPLAY_MODE_OFF: Final = "off"

DISPLAY_MODES: Final = [
    DISPLAY_MODE_TEXT,
    DISPLAY_MODE_IMAGE,
    DISPLAY_MODE_CLOCK,
    DISPLAY_MODE_ANIMATION,
    DISPLAY_MODE_DIY,
    DISPLAY_MODE_OFF,
]

# Clock modes
CLOCK_MODE_DIGITAL: Final = "digital"
CLOCK_MODE_ANALOG: Final = "analog"
CLOCK_MODE_CUSTOM: Final = "custom"

CLOCK_MODES: Final = [
    CLOCK_MODE_DIGITAL,
    CLOCK_MODE_ANALOG,
    CLOCK_MODE_CUSTOM,
]

# Animation effects
EFFECT_STATIC: Final = "static"
EFFECT_SCROLL_LEFT: Final = "scroll_left"
EFFECT_SCROLL_RIGHT: Final = "scroll_right"
EFFECT_SCROLL_UP: Final = "scroll_up"
EFFECT_SCROLL_DOWN: Final = "scroll_down"
EFFECT_BLINK: Final = "blink"
EFFECT_FADE: Final = "fade"

EFFECTS: Final = [
    EFFECT_STATIC,
    EFFECT_SCROLL_LEFT,
    EFFECT_SCROLL_RIGHT,
    EFFECT_SCROLL_UP,
    EFFECT_SCROLL_DOWN,
    EFFECT_BLINK,
    EFFECT_FADE,
]

# Attributes
ATTR_DISPLAY_MODE: Final = "display_mode"
ATTR_TEXT: Final = "text"
ATTR_IMAGE_PATH: Final = "image_path"
ATTR_CLOCK_MODE: Final = "clock_mode"
ATTR_ANIMATION_SPEED: Final = "animation_speed"
ATTR_SCROLL_SPEED: Final = "scroll_speed"
