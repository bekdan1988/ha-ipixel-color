# iPixel Color - Home Assistant Integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A complete Home Assistant custom integration for controlling iPixel Color LED matrix panels via Bluetooth LE and WiFi.

## Features

- 🎨 **Full iPixel Color App Feature Parity**
- 🌐 **35+ Language Support** with complete localization
- ⚙️ **GUI Customizable** - all settings via Options menu, no YAML needed
- 📊 **Dashboard Cards** - ready-to-use Lovelace cards
- 🔌 **BLE & WiFi Support** - flexible connectivity
- 🕐 **Customizable Clock** - multiple formats and styles
- 🎭 **Visual Effects** - rainbow, breathing, wave, sparkle, music rhythm
- 🖼️ **Image & Animation** - display custom images and GIFs
- 🎨 **Doodle Mode** - pixel-by-pixel drawing

## Installation

### Via HACS (Recommended)

1. Open HACS → Integrations
2. Click ⋮ → Custom repositories
3. Add this repository URL
4. Select "Integration" category
5. Click "Add"
6. Find "iPixel Color"
7. Click "Download"
8. Restart Home Assistant

### Manual Installation

1. Copy `custom_components/ipixel_color` to your `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "iPixel Color"
4. Follow the setup wizard:
   - Choose language
   - Select matrix size
   - Configure connectivity (BLE or WiFi)
5. Use **Options** menu to customize anytime

## Supported Devices

- CHICIRIS 20×64 LED Panel
- UDITER Pixel Rider
- Generic 16×32, 16×64, 16×96, 20×64, 32×32 iPixel Color compatible panels

## Dashboard Cards

See `README.md` for ready-to-use Lovelace card examples.

## Documentation

- [English Documentation](README.md)
- [Magyar dokumentáció](README.hu.md)

## License

MIT License - see LICENSE file

## Support

- [GitHub Issues](https://github.com/bekdan1988/ha-ipixel-color/issues)
- [Home Assistant Community](https://community.home-assistant.io/)
