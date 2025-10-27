"""iPixel Color integration."""
from __future__ import annotations
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from .const import DOMAIN

PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.TEXT,
    Platform.SWITCH,
    Platform.SENSOR,
    Platform.BUTTON,
]

_LOGGER = logging.getLogger(__name__)

type IPixelColorConfigEntry = ConfigEntry[Any]

async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the iPixel Color integration."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: IPixelColorConfigEntry) -> bool:
    """Set up iPixel Color from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(options_update_listener))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: IPixelColorConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update - apply changes to running device without reload."""
    _LOGGER.debug("Options updated for %s: %s", entry.entry_id, dict(entry.options))
    # Here: forward changes to device layer (runtime_data) for instant apply
