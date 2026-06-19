"""Binary sensor platform for ESPTimeCast."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ESPTimeCastEntity, value_at


@dataclass(frozen=True, kw_only=True)
class ESPTimeCastBinarySensorDescription(BinarySensorEntityDescription):
    """Describe an ESPTimeCast binary sensor."""

    paths: tuple[str, ...]


BINARY_SENSORS = (
    ESPTimeCastBinarySensorDescription(key="time_synced", name="Time synced", translation_key="time_synced", paths=("time_synced",), device_class=BinarySensorDeviceClass.CONNECTIVITY),
    ESPTimeCastBinarySensorDescription(key="display_busy", name="Display busy", translation_key="display_busy", paths=("displayBusy",), icon="mdi:progress-clock"),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up ESPTimeCast binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(ESPTimeCastBinarySensor(coordinator, description) for description in BINARY_SENSORS)


class ESPTimeCastBinarySensor(ESPTimeCastEntity, BinarySensorEntity):
    """ESPTimeCast binary sensor."""

    entity_description: ESPTimeCastBinarySensorDescription

    def __init__(self, coordinator, description: ESPTimeCastBinarySensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name

    @property
    def is_on(self) -> bool | None:
        """Return binary state."""
        value: Any = value_at(self.coordinator.data, *self.entity_description.paths)
        if value is None:
            return None
        return bool(value)
