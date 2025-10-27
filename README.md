**DISCLAIMER:**: This is a custom integration and is not officially affiliated with the iPixel Color manufacturer.

# iPixel Color - Home Assistant Integration

[![License: MIT](https://img.shields.io/badge/apache-2-0.svg)](https://opensource.org/licenses/apache-2-0)

A complete Home Assistant custom integration for controlling iPixel Color LED matrix panels via Bluetooth LE and WiFi.

## Features

- 🎨 **Full iPixel Color App Feature Parity**
- ⚙️ **GUI Customizable** - all settings via Options menu, no YAML needed
- 📊 **Dashboard Cards** - ready-to-use Lovelace cards
- 🔌 **BLE & WiFi Support** - flexible connectivity
- 🕐 **Customizable Clock** - multiple formats and styles
- 🎭 **Visual Effects** - rainbow, breathing, wave, sparkle, music rhythm
- 🖼️ **Image & Animation** - display custom images and GIFs
- 🎨 **Doodle Mode** - pixel-by-pixel drawing

### Prerequisites
- Home Assistant 2024.1.0 or newer
- Bluetooth adapter with BLE support (for BLE connection)
- WiFi network (for WiFi connection)
- iPixel Color LED matrix panel
  
## Supported Devices

- CHICIRIS 20×64 LED Panel
- UDITER Pixel Rider
- Generic 16×32, 16×64, 16×96, 20×64, 32×32 iPixel Color compatible panels

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

### Setup via UI

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "iPixel Color"
4. Follow the setup wizard:
   - Choose language
   - Select matrix size
   - Configure connectivity (BLE or WiFi)
5. Use **Options** menu to customize anytime

## Created Entities

After setup, the following entities will be created:

### Light Entity
- **light.ipixel_matrix**: Main control for the LED matrix

### Select Entities
- **select.ipixel_display_mode**: Choose display mode
- **select.ipixel_clock_format**: Select clock format
- **select.ipixel_text_effect**: Choose text animation effect
- **select.ipixel_visual_effect**: Select visual effect pattern

### Number Entities
- **number.ipixel_brightness**: Brightness control (0-255)
- **number.ipixel_scroll_speed**: Text scroll speed (1-100)
- **number.ipixel_effect_speed**: Effect animation speed (1-100)
- **number.ipixel_music_sensitivity**: Music sensitivity (1-100)

### Text Entities
- **text.ipixel_display_text**: Enter text to display
- **text.ipixel_custom_time_format**: Custom time format string

### Switch Entities
- **switch.ipixel_show_date**: Toggle date display
- **switch.ipixel_show_seconds**: Toggle seconds display
- **switch.ipixel_auto_brightness**: Enable automatic brightness
- **switch.ipixel_music_rhythm**: Music rhythm mode

### Sensor Entities
- **sensor.ipixel_connection_status**: Connection status
- **sensor.ipixel_device_info**: Device information
- **sensor.ipixel_current_mode**: Currently active display mode

### Button Entities
- **button.ipixel_clear_screen**: Clear the display
- **button.ipixel_reload_config**: Reload configuration

## Services

### `ipixel_color.display_image`
Display a custom image on the matrix.

### `ipixel_color.display_animation`
Display a GIF animation.

### `ipixel_color.set_custom_clock`
Configure custom clock display.

### `ipixel_color.clear_screen`
Clear the screen.

### `ipixel_color.doodle_set_pixel`
Set a single pixel in doodle mode.

### `ipixel_color.music_rhythm`
Enable music rhythm effect.

## Troubleshooting

### Connection Issues
1. Ensure Bluetooth is enabled
2. Check that the LED matrix is powered on
3. Verify the matrix is not connected to another device

### Display Not Updating
1. Check connection status
2. Verify the matrix is powered on
3. Try clearing the screen

## Development

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

Apache License, Version 2.0 - see LICENSE file

## Credits

- Developed for Home Assistant
- Based on reverse engineering of the iPixel Color app protocol
- Uses the Bleak library for Bluetooth communication
  
## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check the documentation
