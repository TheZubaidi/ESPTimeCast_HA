"""Switch platform for ESPTimeCast."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ESPTimeCastEntity, value_at


@dataclass(frozen=True, kw_only=True)
class ESPTimeCastSwitchDescription(SwitchEntityDescription):
    """Describe an ESPTimeCast switch."""

    paths: tuple[str, ...]
    action: str | None = None
    save_field: str | None = None
    on_value: str = "1"
    off_value: str = "0"


SWITCHES = (
    ESPTimeCastSwitchDescription(key="display", translation_key="display", paths=("displayOff",), icon="mdi:monitor"),
    ESPTimeCastSwitchDescription(key="flip_display", translation_key="flip_display", paths=("config.flipDisplay", "flipDisplay"), action="flip", save_field="flipDisplay", icon="mdi:rotate-3d-variant"),
    ESPTimeCastSwitchDescription(key="show_day_of_week", translation_key="show_day_of_week", paths=("config.showDayOfWeek", "showDayOfWeek"), action="show_dayofweek", save_field="showDayOfWeek", icon="mdi:calendar-week"),
    ESPTimeCastSwitchDescription(key="animated_seconds", translation_key="animated_seconds", paths=("config.colonBlinkEnabled", "colonBlinkEnabled"), action="animated_seconds", save_field="colonBlinkEnabled", icon="mdi:timer-sand"),
    ESPTimeCastSwitchDescription(key="show_date", translation_key="show_date", paths=("config.showDate", "showDate"), action="show_date", save_field="showDate", icon="mdi:calendar"),
    ESPTimeCastSwitchDescription(key="twelve_hour", translation_key="twelve_hour", paths=("config.twelveHourToggle", "twelveHourToggle"), action="twelve_hour", save_field="twelveHourToggle", icon="mdi:clock-time-four-outline"),
    ESPTimeCastSwitchDescription(key="imperial_units", translation_key="imperial_units", paths=("config.weatherUnits", "weatherUnits"), action="units", save_field="weatherUnits", on_value="imperial", off_value="metric", icon="mdi:temperature-fahrenheit"),
    ESPTimeCastSwitchDescription(key="show_humidity", translation_key="show_humidity", paths=("config.showHumidity", "showHumidity"), action="humidity", save_field="showHumidity", icon="mdi:water-percent"),
    ESPTimeCastSwitchDescription(key="show_weather_description", translation_key="show_weather_description", paths=("config.showWeatherDescription", "showWeatherDescription"), action="show_weather_desc", save_field="showWeatherDescription", icon="mdi:weather-cloudy"),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up ESPTimeCast switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(ESPTimeCastSwitch(coordinator, description) for description in SWITCHES)


class ESPTimeCastSwitch(ESPTimeCastEntity, SwitchEntity):
    """ESPTimeCast switch."""

    entity_description: ESPTimeCastSwitchDescription

    def __init__(self, coordinator, description: ESPTimeCastSwitchDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return current switch state."""
        value: Any = value_at(self.coordinator.data, *self.entity_description.paths)
        if value is None:
            return None
        if self.entity_description.key == "display":
            return not bool(value)
        if self.entity_description.key == "imperial_units":
            return value == "imperial"
        return bool(value)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the feature on."""
        await self._set_state(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the feature off."""
        await self._set_state(False)

    async def _set_state(self, state: bool) -> None:
        """Set switch state through /action."""
        if self.entity_description.key == "display":
            if state:
                await self.coordinator.api.action("brightness", max(self.coordinator.data.get("brightness") or 7, 1))
            else:
                await self.coordinator.api.action("display_off")
        else:
            value = self.entity_description.on_value if state else self.entity_description.off_value
            if self.entity_description.action:
                await self.coordinator.api.action(self.entity_description.action, value)
            if self.entity_description.save_field:
                await self.coordinator.api.save_config({self.entity_description.save_field: value})
        await self.coordinator.async_request_refresh()
