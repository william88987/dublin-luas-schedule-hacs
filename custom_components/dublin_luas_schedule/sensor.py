"""Sensor platform for Dublin Luas Schedule."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LuasDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luas sensors from a config entry."""
    coordinator: LuasDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    stop_code = entry.data["stop_code"]
    stop_name = entry.data["stop_name"]

    entities = [
        LuasNextTramSensor(coordinator, stop_code, stop_name, "inbound"),
        LuasNextTramSensor(coordinator, stop_code, stop_name, "outbound"),
        LuasStatusSensor(coordinator, stop_code, stop_name),
    ]

    async_add_entities(entities)


class LuasNextTramSensor(CoordinatorEntity[LuasDataUpdateCoordinator], SensorEntity):
    """Sensor for next tram in a direction."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LuasDataUpdateCoordinator,
        stop_code: str,
        stop_name: str,
        direction: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._stop_code = stop_code
        self._stop_name = stop_name
        self._direction = direction
        
        # Create unique ID and entity name
        self._attr_unique_id = f"{stop_code}_{direction}_next"
        self._attr_name = f"{stop_name} {direction.title()} Next"
        self._attr_icon = "mdi:tram" if direction == "inbound" else "mdi:tram-side"

    @property
    def native_value(self) -> str | None:
        """Return the next tram time."""
        if not self.coordinator.data:
            return None
        
        trams = self.coordinator.data.get(self._direction, [])
        if trams:
            return trams[0].get("due", "Unknown")
        return "No trams"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}
        
        trams = self.coordinator.data.get(self._direction, [])
        next_tram = trams[0] if trams else {}
        
        return {
            "destination": next_tram.get("destination", ""),
            "arrival_time": next_tram.get("arrival_time", ""),
            "stop_name": self._stop_name,
            "stop_code": self._stop_code,
            "direction": self._direction,
            "message": self.coordinator.data.get("message", ""),
            "all_trams": trams,
        }


class LuasStatusSensor(CoordinatorEntity[LuasDataUpdateCoordinator], SensorEntity):
    """Sensor for Luas service status at a stop."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:information-outline"

    def __init__(
        self,
        coordinator: LuasDataUpdateCoordinator,
        stop_code: str,
        stop_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._stop_code = stop_code
        self._stop_name = stop_name
        
        self._attr_unique_id = f"{stop_code}_status"
        self._attr_name = f"{stop_name} Status"

    @property
    def native_value(self) -> str | None:
        """Return the service status message."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("message", "Unknown")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}
        
        return {
            "stop_name": self._stop_name,
            "stop_code": self._stop_code,
            "inbound_count": len(self.coordinator.data.get("inbound", [])),
            "outbound_count": len(self.coordinator.data.get("outbound", [])),
        }
