"""Config flow for iPixel Color integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from bleak import BleakScanner
from bleak.backends.device import BLEDevice

from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.const import CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_DEVICE_ADDRESS,
    CONF_DEVICE_NAME,
    CONF_DISPLAY_WIDTH,
    CONF_DISPLAY_HEIGHT,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
)

_LOGGER = logging.getLogger(__name__)


class IPixelColorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iPixel Color."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: dict[str, BLEDevice] = {}
        self._selected_device: BLEDevice | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_DEVICE_ADDRESS]
            device = self._discovered_devices.get(address)
            
            if device is None:
                errors["base"] = "device_not_found"
            else:
                await self.async_set_unique_id(address)
                self._abort_if_unique_id_configured()
                
                self._selected_device = device
                return await self.async_step_device_config()

        # Discover BLE devices
        discovered_devices = await self._async_discover_devices()
        
        if not discovered_devices:
            return self.async_abort(reason="no_devices_found")

        device_options = {
            address: f"{device.name or 'Unknown'} ({address})"
            for address, device in discovered_devices.items()
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_ADDRESS): vol.In(device_options),
                }
            ),
            errors=errors,
        )

    async def async_step_device_config(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure device settings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_DEVICE_NAME],
                data={
                    CONF_DEVICE_ADDRESS: self._selected_device.address,
                    CONF_DEVICE_NAME: user_input[CONF_DEVICE_NAME],
                    CONF_DISPLAY_WIDTH: user_input[CONF_DISPLAY_WIDTH],
                    CONF_DISPLAY_HEIGHT: user_input[CONF_DISPLAY_HEIGHT],
                },
                options={
                    CONF_UPDATE_INTERVAL: user_input.get(
                        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                    ),
                },
            )

        return self.async_show_form(
            step_id="device_config",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DEVICE_NAME,
                        default=self._selected_device.name or "iPixel Color Display",
                    ): cv.string,
                    vol.Required(
                        CONF_DISPLAY_WIDTH, default=DEFAULT_WIDTH
                    ): vol.All(vol.Coerce(int), vol.Range(min=8, max=128)),
                    vol.Required(
                        CONF_DISPLAY_HEIGHT, default=DEFAULT_HEIGHT
                    ): vol.All(vol.Coerce(int), vol.Range(min=8, max=128)),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
                }
            ),
            errors=errors,
        )

    async def _async_discover_devices(self) -> dict[str, BLEDevice]:
        """Discover iPixel Color devices via Bluetooth."""
        _LOGGER.debug("Discovering iPixel Color devices")
        
        discovered = {}
        
        # Use Home Assistant's bluetooth integration if available
        if bluetooth.async_scanner_count(self.hass) > 0:
            devices = bluetooth.async_discovered_service_info(self.hass)
            for device_info in devices:
                if device_info.name and "ipixel" in device_info.name.lower():
                    discovered[device_info.address] = BLEDevice(
                        address=device_info.address,
                        name=device_info.name,
                        details={},
                        rssi=device_info.rssi,
                    )
        else:
            # Fallback to direct Bleak scanning
            devices = await BleakScanner.discover(timeout=10.0)
            for device in devices:
                if device.name and "ipixel" in device.name.lower():
                    discovered[device.address] = device
        
        self._discovered_devices = discovered
        return discovered

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> IPixelColorOptionsFlowHandler:
        """Get the options flow for this handler."""
        return IPixelColorOptionsFlowHandler(config_entry)


class IPixelColorOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for iPixel Color."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
                }
            ),
        )
