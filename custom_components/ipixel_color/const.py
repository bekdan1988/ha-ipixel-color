"""Constants for iPixel Color integration."""
from typing import Final

DOMAIN: Final = "ipixel_color"

# Config keys
CONF_MATRIX_WIDTH: Final = "matrix_width"
CONF_MATRIX_HEIGHT: Final = "matrix_height"
CONF_MATRIX_ORIENTATION: Final = "matrix_orientation"
CONF_MAC_ADDRESS: Final = "mac_address"
CONF_TRANSPORT: Final = "transport"
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
DEFAULT_WIFI_PORT: Final = 8800

# Matrix size presets
MATRIX_SIZES = {
    "16x32": (16, 32),
    "16x64": (16, 64),
    "16x96": (16, 96),
    "20x64": (20, 64),
    "32x32": (32, 32),
}

# Display modes
DISPLAY_MODES = ["clock", "text", "image", "animation", "effect", "doodle", "music_rhythm", "off"]
CLOCK_FORMATS = ["24h", "12h", "analog", "binary", "custom"]
VISUAL_EFFECTS = ["rainbow", "breathing", "flash", "wave", "sparkle", "off"]
