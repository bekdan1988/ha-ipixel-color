"""Complete iPixel Color integration coordinator with notify + chunked writes."""

from __future__ import annotations

import asyncio
import binascii
import logging
from datetime import timedelta
from typing import Any, Optional

from bleak import BleakClient, BleakError
from bleak.backends.characteristic import BleakGATTCharacteristic

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_DEVICE_ADDRESS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

# Command IDs (példák; igazítsd az eszköz protokolljához)
CMD_MAPPING = {
    "turn_on": 0x01,
    "turn_off": 0x02,
    "set_mode": 0x03,
    "display_text": 0x04,
    "display_image": 0x05,
    "display_animation": 0x06,
}


def crc32( bytes) -> int:
    """Calculate CRC32 checksum."""
    return binascii.crc32(data) & 0xFFFFFFFF


class IPixelColorDataUpdateCoordinator(DataUpdateCoordinator):
    """Manage BLE comms with iPixel Color LED matrix."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.entry = entry
        self.device_address: str = entry.data[CONF_DEVICE_ADDRESS]
        self.client: Optional[BleakClient] = None
        self.write_characteristic: Optional[BleakGATTCharacteristic] = None
        self.notify_characteristics: list[BleakGATTCharacteristic] = []

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
            _LOGGER.error("Failed updating  %s", err)
            raise UpdateFailed(f"Failed updating  {err}") from err

    async def _async_connect(self) -> None:
        """Connect BLE and prepare characteristics/notifications."""
        if self.client and self.client.is_connected:
            return
        try:
            self.client = BleakClient(self.device_address)
            await self.client.connect()
            _LOGGER.info("Connected to BLE device %s", self.device_address)

            # Service/char discovery
            await self._discover_characteristics()

            # Enable notifications if any notify char is present
            await self._enable_notifications()

        except BleakError as err:
            _LOGGER.error("Connection failed: %s", err)
            raise UpdateFailed(f"Connection failed: {err}") from err

    async def _discover_characteristics(self) -> None:
        """Discover writable and notifiable characteristics."""
        if not self.client or not self.client.is_connected:
            raise UpdateFailed("Client not connected for discovery")

        # Ensure services are populated/refreshed
        services = await self.client.get_services()
        self.write_characteristic = None
        self.notify_characteristics = []

        for service in services:
            for char in service.characteristics:
                props = set(char.properties or [])
                if "write_without_response" in props or "write" in props:
                    # Prefer write_without_response where possible
                    if not self.write_characteristic:
                        self.write_characteristic = char
                if "notify" in props:
                    self.notify_characteristics.append(char)

        if not self.write_characteristic:
            raise UpdateFailed("No writable GATT characteristic found")

        _LOGGER.info(
            "Writable characteristic: %s | Notifies: %s",
            self.write_characteristic.uuid,
            [c.uuid for c in self.notify_characteristics],
        )

    async def _enable_notifications(self) -> None:
        """Enable notifications for all notify characteristics (if any)."""
        if not self.client or not self.client.is_connected:
            return

        async def _notify_cb(sender: BleakGATTCharacteristic,  bytearray) -> None:
            _LOGGER.debug("Notify from %s: %s", sender.uuid, data.hex())

        for ch in self.notify_characteristics:
            try:
                await self.client.start_notify(ch, _notify_cb)
                _LOGGER.debug("Notifications enabled on %s", ch.uuid)
            except Exception as e:
                _LOGGER.debug("Failed enabling notify on %s: %s", ch.uuid, e)

    async def _async_get_device_info(self) -> dict[str, Any]:
        """Return basic device info (placeholder)."""
        return {
            "firmware_version": "1.0.0",
            "mcu_version": "1.0.0",
        }

    # Public control API

    async def async_turn_on(
        self,
        brightness: Optional[int] = None,
        rgb_color: Optional[tuple[int, int, int]] = None,
        effect: Optional[str] = None,
    ) -> None:
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
        self._is_on = False
        await self._send_command("turn_off")
        await self.async_request_refresh()

    async def async_set_display_mode(self, mode: str) -> None:
        self._display_mode = mode
        await self._send_command("set_mode", {"mode": mode})
        await self.async_request_refresh()

    async def async_display_text(
        self, text: str, color: Optional[list[int]] = None, speed: int = 1
    ) -> None:
        color = color or [255, 255, 255]
        text_bytes = text.encode("utf-8")

        payload = bytearray()
        payload.append(CMD_MAPPING["display_text"])
        payload.append(max(0, min(speed, 10)))  # clamp speed 0..10
        payload.extend(color[:3])  # RGB
        payload.append(len(text_bytes))
        payload.extend(text_bytes)

        checksum = crc32(payload)
        payload.extend(checksum.to_bytes(4, "little"))

        await self._send_raw(payload)

    async def async_display_image(self, image_path: str) -> None:
        with open(image_path, "rb") as f:
            image_data = f.read()

        payload = bytearray()
        payload.append(CMD_MAPPING["display_image"])
        payload.extend(image_data)

        checksum = crc32(payload)
        payload.extend(checksum.to_bytes(4, "little"))

        await self._send_raw(payload)

    async def async_display_animation(self, animation_name: str) -> None:
        anim_bytes = animation_name.encode("utf-8")

        payload = bytearray()
        payload.append(CMD_MAPPING["display_animation"])
        payload.append(len(anim_bytes))
        payload.extend(anim_bytes)

        checksum = crc32(payload)
        payload.extend(checksum.to_bytes(4, "little"))

        await self._send_raw(payload)

    # Low-level send utilities

    async def _send_command(
        self, command: str, params: Optional[dict[str, Any]] = None
    ) -> None:
        cmd_id = CMD_MAPPING.get(command)
        if cmd_id is None:
            _LOGGER.error("Unknown command: %s", command)
            return

        payload = bytearray([cmd_id])

        if params and command == "set_mode":
            mode_bytes = params.get("mode", "").encode("utf-8")
            payload.append(len(mode_bytes))
            payload.extend(mode_bytes)

        checksum = crc32(payload)
        payload.extend(checksum.to_bytes(4, "little"))

        await self._send_raw(payload)

    async def _send_raw(self, payload: bytearray) -> None:
        """Chunked write with notify enabled and max-size detection."""
        if not self.client or not self.client.is_connected:
            await self._async_connect()
        if not self.write_characteristic:
            raise UpdateFailed("Writable characteristic not found")

        # Prefer write_without_response if supported to reach higher throughput
        props = set(self.write_characteristic.properties or [])
        use_response = "write" in props and "write_without_response" not in props

        # Determine max chunk size
        max_chunk = await self._resolve_max_write_without_response_size(self.write_characteristic)
        _LOGGER.debug(
            "Write props=%s | response=%s | max_chunk=%d | total=%d",
            props, use_response, max_chunk, len(payload)
        )

        # Chunked transfer
        offset = 0
        while offset < len(payload):
            chunk = payload[offset : offset + max_chunk]
            await self.client.write_gatt_char(
                self.write_characteristic, chunk, response=use_response
            )
            offset += len(chunk)
            # Tiny pacing to avoid overrun on some stacks
            await asyncio.sleep(0.005)

    async def _resolve_max_write_without_response_size(
        self, char: BleakGATTCharacteristic
    ) -> int:
        """Get the maximum chunk size; wait briefly if initially 20."""
        # Bleak exposes characteristic.max_write_without_response_size (preferred)
        # Some backends may report 20 first, then a higher value a bit later.
        try:
            # Try a short wait loop to see if it increases beyond default 20
            deadline = self.hass.loop.time() + 2.0
            size = getattr(char, "max_write_without_response_size", 20)
            if callable(size):
                # Older API shape
                size = size()
            while size == 20 and self.hass.loop.time() < deadline:
                await asyncio.sleep(0.1)
                size = getattr(char, "max_write_without_response_size", 20)
                if callable(size):
                    size = size()
            # Fallback floor 20, floor ceiling to something reasonable
            if not isinstance(size, int) or size < 20:
                size = 20
            return int(size)
        except Exception:
            return 20

    async def async_shutdown(self) -> None:
        """Disconnect gracefully."""
        if self.client and self.client.is_connected:
            # Stop notifications
            for ch in self.notify_characteristics:
                try:
                    await self.client.stop_notify(ch)
                except Exception:
                    pass
            await self.client.disconnect()