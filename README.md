# iPixel Color Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/yourusername/ipixel-color-hass.svg)](https://github.com/yourusername/ipixel-color-hass/releases)

Control your iPixel Color LED matrix displays directly from Home Assistant!

## Features

- 🎨 Full RGB color control
- 💡 Brightness adjustment
- 📝 Text display with scrolling
- 🖼️ Image display
- 🕐 Multiple clock modes
- ✨ Built-in effects and animations
- 📱 Full GUI configuration
- 🔄 Automatic device discovery via Bluetooth

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL
6. Select "Integration" as the category
7. Click "Add"
8. Search for "iPixel Color" and install

### Manual Installation

1. Download the latest release
2. Extract the `custom_components/ipixel_color` directory
3. Copy it to your Home Assistant `custom_components` directory
4. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "iPixel Color"
4. Select your device from the discovered list
5. Configure display dimensions
6. Click Submit

## Usage

### As a Light

Control your display as a standard RGB light:
- Turn on/off
- Adjust brightness
- Change colors
- Select effects

### Display Text

Use the `ipixel_color.display_text` service:

```yaml
service: ipixel_color.display_text
data:
  text: "Hello World!"
  color: [255, 0, 0]
  speed: 5
target:
  entity_id: light.ipixel_color_display
