"""Data update coordinator for iPixel Color."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from bleak import BleakClient, BleakError

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


class IPixelColorDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching iPixel Color data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.device_address = entry.data[CONF_DEVICE_ADDRESS]
        self.client: BleakClient | None = None
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
        """Update data via library."""
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
        """Get device information."""
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

    async def async_display_text(self, text: str, **kwargs) -> None:
        """Display text on the matrix."""
        await self._async_send_command("display_text", {"text": text, **kwargs})

    async def async_display_image(self, image_data: bytes) -> None:
        """Display image on the matrix."""
        await self._async_send_command("display_image", {"image": image_data})

    async def _async_send_command(self, command: str, data: dict[str, Any] | None = None) -> None:
        """Send command to device."""
        if self.client is None or not self.client.is_connected:
            await self._async_connect()
        
        _LOGGER.debug("Sending command: %s with data: %s", command, data)

    async def async_shutdown(self) -> None:
        """Shutdown coordinator."""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
