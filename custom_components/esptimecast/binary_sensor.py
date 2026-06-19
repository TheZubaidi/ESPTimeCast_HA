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

    path: str


BINARY_SENSORS = (
    ESPTimeCastBinarySensorDescription(key="time_synced", translation_key="time_synced", path="time_synced", device_class=BinarySensorDeviceClass.CONNECTIVITY),
    ESPTimeCastBinarySensorDescription(key="display_busy", translation_key="display_busy", path="displayBusy", icon="mdi:progress-clock"),
    ESPTimeCastBinarySensorDescription(key="allow_interrupt", translation_key="allow_interrupt", path="allowInterrupt", icon="mdi:message-alert-outline"),
    ESPTimeCastBinarySensorDescription(key="countdown_enabled", translation_key="countdown_enabled", path="countdown.enabled", icon="mdi:calendar-clock"),
    ESPTimeCastBinarySensorDescription(key="nightscout_active", translation_key="nightscout_active", path="nightscout.active", icon="mdi:diabetes"),
    ESPTimeCastBinarySensorDescription(key="nightscout_outdated", translation_key="nightscout_outdated", path="nightscout.isOutdated", device_class=BinarySensorDeviceClass.PROBLEM),
    ESPTimeCastBinarySensorDescription(key="dimming_enabled", translation_key="dimming_enabled", path="dimming.dimmingEnabled", icon="mdi:brightness-4"),
    ESPTimeCastBinarySensorDescription(key="auto_dimming_enabled", translation_key="auto_dimming_enabled", path="dimming.autoDimmingEnabled", icon="mdi:weather-sunset"),
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

    @property
    def is_on(self) -> bool | None:
        """Return binary state."""
        value: Any = value_at(self.coordinator.data, self.entity_description.path)
        if value is None:
            return None
        return bool(value)
