"""Complete iPixel Color integration coordinator with BLE discovery."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Optional

import binascii
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
        self.write_characteristic: Optional[BleakGATTCharacteristic] = None
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
            
            # Discover and find writable characteristic
            await self._discover_characteristics()
            
        except BleakError as err:
            _LOGGER.error("Connection failed: %s", err)
            raise UpdateFailed(f"Connection failed: {err}") from err

    async def _discover_characteristics(self) -> None:
        """Discover available characteristics on the device."""
        if not self.client or not self.client.is_connected:
            _LOGGER.error("Client not connected for characteristic discovery")
            return

        try:
            services = self.client.services
            _LOGGER.info("Discovering BLE services and characteristics...")
            
            for service in services:
                _LOGGER.debug(f"Service: {service.uuid}")
                for char in service.characteristics:
                    _LOGGER.debug(
                        f"  Characteristic: {char.uuid}, "
                        f"Properties: {char.properties}"
                    )
                    
                    # Look for writable characteristic
                    if "write" in char.properties or "write-without-response" in char.properties:
                        self.write_characteristic = char
                        _LOGGER.info(
                            f"Found writable characteristic: {char.uuid} "
                            f"with properties: {char.properties}"
                        )
                        
        except Exception as err:
            _LOGGER.error("Failed to discover characteristics: %s", err)

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
