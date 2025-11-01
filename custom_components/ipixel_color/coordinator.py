"""Complete iPixel Color integration coordinator with refined BLE protocol handling."""

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

# Command IDs based on iPixel Color BLE protocol
CMD_MAPPING = {
    "turn_on": 0x01,
    "turn_off": 0x02,
    "set_mode": 0x03,
    "display_text": 0x04,
    "display_image": 0x05,
    "display_animation": 0x06,
}

def crc32(data: bytes) -> int:
    """Calculate CRC32 checksum."""
    return binascii.crc32(data) & 0xFFFFFFFF


class IPixelColorDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages communication with iPixel Color LED matrix."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
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
        """Fetch latest device state."""
        try:
            if not self.client or not self.client.is_connected:
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
            _LOGGER.error("Failed updating data: %s", err)
            raise UpdateFailed(f"Failed updating data: {err}") from err

    async def _async_connect(self) -> None:
        """Connect BLE client to device."""
        if self.client and self.client.is_connected:
            return
        try:
            self.client = BleakClient(self.device_address)
            await self.client.connect()
            _LOGGER.info("Connected to device at %s", self.device_address)
        except BleakError as err:
            _LOGGER.error("Connection failed: %s", err)
            raise UpdateFailed(f"Connection failed: {err}") from err

    async def _async_get_device_info(self) -> dict[str, Any]:
        """Get device information."""
        return {
            "firmware_version": "1.0.0",
            "mcu_version": "1.0.0",
        }

    async def async_turn_on(
        self,
        brightness: Optional[int] = None,
        rgb_color: Optional[tuple[int, int, int]] = None,
        effect: Optional[str] = None,
    ) -> None:
        """Turn on light with optional settings."""
        self._is_on = True
        if brightness is not None:
            self._brightness = brightness
        if rgb_color is not None:
            self._rgb_color = rgb_color
        if effect is not None:
            self._effect = effect

        await self._send_command("turn_on")
        await self.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn off light."""
        self._is_on = False
        await self._send_command("turn_off")
        await self.async_request_refresh()

    async def async_set_display_mode(self, mode: str) -> None:
        """Change display mode."""
        self._display_mode = mode
        await self._send_command("set_mode", {"mode": mode})
        await self.async_request_refresh()

    async def async_display_text(
        self, text: str, color: Optional[list[int]] = None, speed: int = 1
    ) -> None:
        """Display scrolling text on the matrix."""
        color = color or [255, 255, 255]
        text_bytes = text.encode("utf-8")
        payload = bytearray()
        payload.append(CMD_MAPPING["display_text"])
        payload.append(speed)  # Speed byte
        payload.extend(color[:3])  # RGB color bytes
        payload.append(len(text_bytes))
        payload.extend(text_bytes)
        checksum = crc32(payload)
        payload.extend(checksum.to_bytes(4, "little"))

        await self._send_raw(payload)

    async def async_display_image(self, image_path: str) -> None:
        """Display an image file on the matrix."""
        with open(image_path, "rb") as f:
            image_data = f.read()
        payload = bytearray()
        payload.append(CMD_MAPPING["display_image"])
        payload.extend(image_data)
        checksum = crc32(payload)
        payload.extend(checksum.to_bytes(4, "little"))

        await self._send_raw(payload)

    async def async_display_animation(self, animation_name: str) -> None:
        """Play a predefined animation."""
        anim_bytes = animation_name.encode("utf-8")
        payload = bytearray()
        payload.append(CMD_MAPPING["display_animation"])
        payload.append(len(anim_bytes))
        payload.extend(anim_bytes)
        checksum = crc32(payload)
        payload.extend(checksum.to_bytes(4, "little"))

        await self._send_raw(payload)

    async def _send_command(self, command: str, params: Optional[dict[str, Any]] = None) -> None:
        """Construct and send a command with optional parameters."""
        cmd_id = CMD_MAPPING.get(command)
        if cmd_id is None:
            _LOGGER.error("Unknown command: %s", command)
            return

        payload = bytearray([cmd_id])

        if params:
            if command == "set_mode":
                mode_bytes = params.get("mode", "").encode("utf-8")
                payload.append(len(mode_bytes))
                payload.extend(mode_bytes)

        checksum = crc32(payload)
        payload.extend(checksum.to_bytes(4, "little"))

        await self._send_raw(payload)

    async def _send_raw(self, payload: bytearray) -> None:
        """Send raw bytes payload to BLE device."""
        if not self.client or not self.client.is_connected:
            await self._async_connect()

        try:
            _LOGGER.debug("Sending to BLE: %s", payload.hex())
            await self.client.write_gatt_char(CHARACTERISTIC_WRITE, payload)
        except Exception as err:
            _LOGGER.error("Failed to send BLE command: %s", err)
            raise UpdateFailed(f"Failed to send BLE command: {err}") from err

    async def async_shutdown(self) -> None:
        """Disconnect cleanly."""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
