"""Sensor platform for ESPTimeCast."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ESPTimeCastEntity, value_at


@dataclass(frozen=True, kw_only=True)
class ESPTimeCastSensorDescription(SensorEntityDescription):
    """Describe an ESPTimeCast sensor."""

    paths: tuple[str, ...]


SENSORS: tuple[ESPTimeCastSensorDescription, ...] = (
    ESPTimeCastSensorDescription(key="mode", translation_key="mode", paths=("mode",), icon="mdi:view-dashboard"),
    ESPTimeCastSensorDescription(key="current_message", translation_key="current_message", paths=("customMessage", "message"), icon="mdi:message-text"),
    ESPTimeCastSensorDescription(key="local_time", translation_key="local_time", paths=("localTime",), icon="mdi:clock-outline"),
    ESPTimeCastSensorDescription(
        key="wifi_signal",
        translation_key="wifi_signal",
        paths=("wifi_signal",),
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ESPTimeCastSensorDescription(
        key="temperature",
        translation_key="temperature",
        paths=("weather.currentTemperature",),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ESPTimeCastSensorDescription(
        key="humidity",
        translation_key="humidity",
        paths=("weather.currentHumidity",),
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ESPTimeCastSensorDescription(key="firmware_version", translation_key="firmware_version", paths=("version",), icon="mdi:chip"),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up ESPTimeCast sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(ESPTimeCastSensor(coordinator, description) for description in SENSORS)


class ESPTimeCastSensor(ESPTimeCastEntity, SensorEntity):
    """ESPTimeCast sensor."""

    entity_description: ESPTimeCastSensorDescription

    def __init__(self, coordinator, description: ESPTimeCastSensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return sensor value."""
        value = value_at(self.coordinator.data, *self.entity_description.paths)
        if value == "":
            return None
        return value

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return temperature unit according to device config."""
        if self.entity_description.key != "temperature":
            return self.entity_description.native_unit_of_measurement
        if value_at(self.coordinator.data, "config.weatherUnits", "weatherUnits") == "imperial":
            return UnitOfTemperature.FAHRENHEIT
        return UnitOfTemperature.CELSIUS
