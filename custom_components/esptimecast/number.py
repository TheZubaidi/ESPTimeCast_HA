"""Number platform for ESPTimeCast."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ESPTimeCastEntity, value_at


@dataclass(frozen=True, kw_only=True)
class ESPTimeCastNumberDescription(NumberEntityDescription):
    """Describe an ESPTimeCast number."""

    paths: tuple[str, ...]
    save_field: str | None = None
    action: str | None = None


NUMBERS = (
    ESPTimeCastNumberDescription(
        key="brightness",
        name="Display brightness",
        translation_key="brightness",
        paths=("brightness",),
        action="brightness",
        native_min_value=0,
        native_max_value=15,
        native_step=1,
        mode=NumberMode.SLIDER,
        icon="mdi:brightness-6",
    ),
    ESPTimeCastNumberDescription(
        key="clock_duration",
        name="Clock duration",
        translation_key="clock_duration",
        paths=("config.clockDuration", "clockDuration"),
        save_field="clockDuration",
        native_min_value=1,
        native_max_value=3600,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        mode=NumberMode.BOX,
        icon="mdi:clock-start",
    ),
    ESPTimeCastNumberDescription(
        key="weather_duration",
        name="Weather duration",
        translation_key="weather_duration",
        paths=("config.weatherDuration", "weatherDuration"),
        save_field="weatherDuration",
        native_min_value=1,
        native_max_value=3600,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        mode=NumberMode.BOX,
        icon="mdi:weather-partly-cloudy",
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up ESPTimeCast number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(ESPTimeCastNumber(coordinator, description) for description in NUMBERS)


class ESPTimeCastNumber(ESPTimeCastEntity, NumberEntity):
    """ESPTimeCast number control."""

    entity_description: ESPTimeCastNumberDescription

    def __init__(self, coordinator, description: ESPTimeCastNumberDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name

    @property
    def native_value(self) -> int | None:
        """Return current number value."""
        value: Any = value_at(self.coordinator.data, *self.entity_description.paths)
        return None if value is None else int(value)

    async def async_set_native_value(self, value: float) -> None:
        """Set number value."""
        if self.entity_description.action:
            await self.coordinator.api.action(self.entity_description.action, int(value))
        elif self.entity_description.save_field:
            await self.coordinator.api.save_config({self.entity_description.save_field: int(value)})
        await self.coordinator.async_request_refresh()
