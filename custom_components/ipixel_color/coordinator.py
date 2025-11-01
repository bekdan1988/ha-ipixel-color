"""Data update coordinator for iPixel Color."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Optional

import binascii
from bleak import BleakClient, BleakError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_DEVICE_ADDRESS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    CHARACTERISTIC_WRITE,
)

_LOGGER = logging.getLogger(__name__)


def crc32(data: bytes) -> int:
    """Calculate CRC32 checksum."""
    return binascii.crc32(data) & 0xFFFFFFFF


class IPixelColorDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching iPixel Color data and sending commands."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.device_address = entry.data[CONF_DEVICE_ADDRESS]
        self.client: Optional[BleakClient] = None
        self._is_on = False
        self._brightness = 255
        self._rgb_color = (255, 255, 255)
        self._effect = "static"
        self._display_mode = "off"

        update_interval = timedelta(
            seconds=entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via BLE (placeholder)."""
        try:
            if self.client is None or not self.client.is_connected:
                await self._async_connect()

            device_info = await self._async_get_device_info()

            return {
                "is_on": self._is_on,
                "brightness": self._brightness,
                "rgb_color": self._rgb_color,
                "effect": self._effect,
                "display_mode": self._display_mode,
                "connection_status": "connected",
                "firmware_version": device_info.get("firmware_version", "Unknown"),
            }
        except Exception as err:
            _LOGGER.error("Error communicating with device: %s", err)
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    async def _async_connect(self) -> None:
        """Connect to the device."""
        try:
            self.client = BleakClient(self.device_address)
            await self.client.connect()
            _LOGGER.info("Connected to iPixel Color device at %s", self.device_address)
        except BleakError as err:
            _LOGGER.error("Failed to connect to device: %s", err)
            raise UpdateFailed(f"Failed to connect: {err}") from err

    async def _async_get_device_info(self) -> dict[str, Any]:
        """Get device information (placeholder)."""
        # Implement actual info query if supported by device
        return {
            "firmware_version": "1.0.0",
            "mcu_version": "1.0.0",
        }

    async def async_turn_on(
        self,
        brightness: int | None = None,
        rgb_color: tuple[int, int, int] | None = None,
        effect: str | None = None,
    ) -> None:
        """Turn on the display."""
        self._is_on = True
        if brightness is not None:
            self._brightness = brightness
        if rgb_color is not None:
            self._rgb_color = rgb_color
        if effect is not None:
            self._effect = effect

        await self._async_send_command("turn_on")
        await self.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn off the display."""
        self._is_on = False
        await self._async_send_command("turn_off")
        await self.async_request_refresh()

    async def async_set_display_mode(self, mode: str) -> None:
        """Set display mode."""
        self._display_mode = mode
        await self._async_send_command("set_mode", {"mode": mode})
        await self.async_request_refresh()

    async def async_display_text(
        self, text: str, color: list[int] | None = None, speed: int = 1
    ) -> None:
        """Display text on the matrix."""
        color = color or [255, 255, 255]
        # Command IDs example mapping
        CMD_MAPPING = {
            "display_text": 0x04,
        }
        cmd_id = CMD_MAPPING["display_text"]
        payload = bytearray()
        payload.append(cmd_id)
        payload.append(speed)
        payload.extend(color[:3])
        text_bytes = text.encode('utf-8')
        payload.append(len(text_bytes))
        payload.extend(text_bytes)
        checksum = crc32(payload)
        payload.extend(checksum.to_bytes(4, 'little'))
        await self._send_ble_command(payload)

    async def async_display_image(self, image_path: str) -> None:
        """Display image on the matrix."""
        # Read image bytes
        with open(image_path, "rb") as img_file:
            image_data = img_file.read()
        CMD_MAPPING = {
            "display_image": 0x05,
        }
        cmd_id = CMD_MAPPING["display_image"]
        payload = bytearray()
        payload.append(cmd_id)
        payload.extend(image_data)
        checksum = crc32(payload)
        payload.extend(checksum.to_bytes(4, 'little'))
        await self._send_ble_command(payload)

    async def async_display_animation(self, animation_name: str) -> None:
        """Play a built-in animation."""
        CMD_MAPPING = {
            "display_animation": 0x06,
        }
        cmd_id = CMD_MAPPING["display_animation"]
        payload = bytearray()
        payload.append(cmd_id)
        anim_bytes = animation_name.encode('utf-8')
        payload.append(len(anim_bytes))
        payload.extend(anim_bytes)
        checksum = crc32(payload)
        payload.extend(checksum.to_bytes(4, 'little'))
        await self._send_ble_command(payload)

    async def _send_ble_command(self, payload: bytearray) -> None:
        """Write the command payload to BLE device."""
        if self.client is None or not self.client.is_connected:
            await self._async_connect()
        _LOGGER.debug("Sending BLE command: %s", payload.hex())
        await self.client.write_gatt_char(CHARACTERISTIC_WRITE, payload)

    async def async_shutdown(self) -> None:
        """Shutdown coordinator cleanly."""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
