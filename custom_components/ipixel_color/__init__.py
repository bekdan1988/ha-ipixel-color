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
