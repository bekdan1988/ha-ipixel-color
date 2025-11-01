"""Sensor platform for iPixel Color integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
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
    """Set up the iPixel Color sensors."""
    coordinator: IPixelColorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        IPixelColorStatusSensor(coordinator, entry),
        IPixelColorFirmwareSensor(coordinator, entry),
    ])


class IPixelColorStatusSensor(CoordinatorEntity, SensorEntity):
    """Representation of iPixel Color connection status sensor."""

    _attr_has_entity_name = True
    _attr_name = "Connection Status"

    def __init__(
        self,
        coordinator: IPixelColorDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_sensor_status"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["device_address"])},
        }

    @property
    def native_value(self) -> str:
        """Return the connection status."""
        return self.coordinator.data.get("connection_status", "disconnected")


class IPixelColorFirmwareSensor(CoordinatorEntity, SensorEntity):
    """Representation of iPixel Color firmware version sensor."""

    _attr_has_entity_name = True
    _attr_name = "Firmware Version"

    def __init__(
        self,
        coordinator: IPixelColorDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_sensor_firmware"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["device_address"])},
        }

    @property
    def native_value(self) -> str:
        """Return the firmware version."""
        return self.coordinator.data.get("firmware_version", "Unknown")
