"""Light platform for iPixel Color integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, EFFECTS
from .coordinator import IPixelColorDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the iPixel Color light."""
    coordinator: IPixelColorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IPixelColorLight(coordinator, entry)])


class IPixelColorLight(CoordinatorEntity, LightEntity):
    """Representation of an iPixel Color light."""

    _attr_has_entity_name = True
    _attr_name = "Display"
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_supported_features = LightEntityFeature.EFFECT

    def __init__(
        self,
        coordinator: IPixelColorDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_light"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["device_address"])},
        }

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.coordinator.data.get("is_on", False)

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        return self.coordinator.data.get("brightness", 255)

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Return the rgb color value."""
        return self.coordinator.data.get("rgb_color", (255, 255, 255))

    @property
    def color_mode(self) -> ColorMode:
        """Return the color mode of the light."""
        return ColorMode.RGB

    @property
    def effect(self) -> str | None:
        """Return the current effect."""
        return self.coordinator.data.get("effect")

    @property
    def effect_list(self) -> list[str]:
        """Return the list of supported effects."""
        return EFFECTS

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        rgb_color = kwargs.get(ATTR_RGB_COLOR)
        effect = kwargs.get(ATTR_EFFECT)

        await self.coordinator.async_turn_on(
            brightness=brightness,
            rgb_color=rgb_color,
            effect=effect,
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.coordinator.async_turn_off()
