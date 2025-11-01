"""The iPixel Color integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_DEVICE_ADDRESS
from .coordinator import IPixelColorDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.SWITCH,
    Platform.SENSOR,
]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration and register services."""

    async def handle_display_text(service_call: Any) -> None:
        entity_id = service_call.data["entity_id"]
        text = service_call.data["text"]
        color = service_call.data.get("color", [255, 255, 255])
        speed = service_call.data.get("speed", 1)

        coordinator = None
        for coord in hass.data.get(DOMAIN, {}).values():
            if hasattr(coord, "async_display_text"):
                coordinator = coord
                break

        if coordinator is None:
            _LOGGER.error("Coordinator not found to display text")
            return

        await coordinator.async_display_text(text, color=color, speed=speed)

    async def handle_display_image(service_call: Any) -> None:
        entity_id = service_call.data["entity_id"]
        image_path = service_call.data["image_path"]

        coordinator = None
        for coord in hass.data.get(DOMAIN, {}).values():
            if hasattr(coord, "async_display_image"):
                coordinator = coord
                break

        if coordinator is None:
            _LOGGER.error("Coordinator not found to display image")
            return

        await coordinator.async_display_image(image_path)

    async def handle_display_animation(service_call: Any) -> None:
        entity_id = service_call.data["entity_id"]
        animation = service_call.data["animation"]

        coordinator = None
        for coord in hass.data.get(DOMAIN, {}).values():
            if hasattr(coord, "async_display_animation"):
                coordinator = coord
                break

        if coordinator is None:
            _LOGGER.error("Coordinator not found to display animation")
            return

        await coordinator.async_display_animation(animation)

    hass.services.async_register(
        DOMAIN,
        "display_text",
        handle_display_text,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.entity_id,
                vol.Required("text"): cv.string,
                vol.Optional("color"): vol.All(
                    cv.ensure_list,
                    [vol.All(vol.Coerce(int), vol.Range(min=0, max=255))],
                ),
                vol.Optional("speed", default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        "display_image",
        handle_display_image,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.entity_id,
                vol.Required("image_path"): cv.string,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        "display_animation",
        handle_display_animation,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.entity_id,
                vol.Required("animation"): cv.string,
            }
        ),
    )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up iPixel Color from a config entry."""
    _LOGGER.debug("Setting up iPixel Color integration")
    
    coordinator = IPixelColorDataUpdateCoordinator(hass, entry)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Unable to connect to device: {err}") from err
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.data[CONF_DEVICE_ADDRESS])},
        name=entry.data.get("device_name", "iPixel Color Display"),
        manufacturer="Heaton Technology",
        model="iPixel Color LED Matrix",
        sw_version=coordinator.data.get("firmware_version", "Unknown"),
    )
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        coordinator: IPixelColorDataUpdateCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    
    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
