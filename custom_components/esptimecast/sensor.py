"""Sensor platform for ESPTimeCast."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ESPTimeCastEntity, value_at


@dataclass(frozen=True, kw_only=True)
class ESPTimeCastSensorDescription(SensorEntityDescription):
    """Describe an ESPTimeCast sensor."""

    path: str


SENSORS = (
    ESPTimeCastSensorDescription(key="mode", translation_key="mode", path="mode", icon="mdi:view-dashboard"),
    ESPTimeCastSensorDescription(key="message", translation_key="message", path="message", icon="mdi:message-text"),
    ESPTimeCastSensorDescription(key="version", translation_key="version", path="version", icon="mdi:chip"),
    ESPTimeCastSensorDescription(key="board", translation_key="board", path="board", icon="mdi:developer-board"),
    ESPTimeCastSensorDescription(
        key="wifi_signal",
        translation_key="wifi_signal",
        path="wifi_signal",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ESPTimeCastSensorDescription(
        key="session_runtime",
        translation_key="session_runtime",
        path="session_runtime",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    ESPTimeCastSensorDescription(key="device_runtime", translation_key="device_runtime", path="device_runtime", icon="mdi:timer-outline"),
    ESPTimeCastSensorDescription(key="local_time", translation_key="local_time", path="localTime", icon="mdi:clock-outline"),
    ESPTimeCastSensorDescription(
        key="temperature",
        translation_key="temperature",
        path="weather.currentTemperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ESPTimeCastSensorDescription(
        key="humidity",
        translation_key="humidity",
        path="weather.currentHumidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ESPTimeCastSensorDescription(key="weather_description", translation_key="weather_description", path="weather.weatherDescription", icon="mdi:weather-partly-cloudy"),
    ESPTimeCastSensorDescription(key="countdown_label", translation_key="countdown_label", path="countdown.label", icon="mdi:calendar-clock"),
    ESPTimeCastSensorDescription(
        key="countdown_remaining",
        translation_key="countdown_remaining",
        path="countdown.remaining",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ESPTimeCastSensorDescription(
        key="nightscout_glucose",
        translation_key="nightscout_glucose",
        path="nightscout.glucose",
        native_unit_of_measurement="mg/dL",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:diabetes",
    ),
    ESPTimeCastSensorDescription(key="nightscout_trend", translation_key="nightscout_trend", path="nightscout.trend", icon="mdi:trending-up"),
    ESPTimeCastSensorDescription(key="sns_type", translation_key="sns_type", path="sns.type", icon="mdi:account-group"),
    ESPTimeCastSensorDescription(key="youtube_subscribers", translation_key="youtube_subscribers", path="sns.youtubeSubscribers", icon="mdi:youtube"),
    ESPTimeCastSensorDescription(key="instagram_followers", translation_key="instagram_followers", path="sns.instagramFollowers", icon="mdi:instagram"),
    ESPTimeCastSensorDescription(key="timezone", translation_key="timezone", path="config.timeZone", icon="mdi:map-clock"),
    ESPTimeCastSensorDescription(key="language", translation_key="language", path="config.language", icon="mdi:translate"),
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
        value = value_at(self.coordinator.data, self.entity_description.path)
        if value == "":
            return None
        return value

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return temperature unit according to device config."""
        if self.entity_description.key != "temperature":
            return self.entity_description.native_unit_of_measurement
        if value_at(self.coordinator.data, "config.weatherUnits") == "imperial":
            return UnitOfTemperature.FAHRENHEIT
        return UnitOfTemperature.CELSIUS
