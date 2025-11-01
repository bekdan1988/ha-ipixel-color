"""Switch platform for iPixel Color integration."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import IPixelColorDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the iPixel Color switch."""
    coordinator: IPixelColorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IPixelColorPowerSwitch(coordinator, entry)])


class IPixelColorPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an iPixel Color power switch."""

    _attr_has_entity_name = True
    _attr_name = "Power"

    def __init__(
        self,
        coordinator: IPixelColorDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_switch_power"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["device_address"])},
        }

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.coordinator.data.get("is_on", False)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the display."""
        await self.coordinator.async_turn_on()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the display."""
        await self.coordinator.async_turn_off()
