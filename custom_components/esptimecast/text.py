"""Text platform for ESPTimeCast."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.text import TextEntity, TextEntityDescription, TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ESPTimeCastEntity, value_at


@dataclass(frozen=True, kw_only=True)
class ESPTimeCastTextDescription(TextEntityDescription):
    """Describe an ESPTimeCast text entity."""

    paths: tuple[str, ...]
    save_field: str | None = None
    action: str | None = None
    send_message: bool = False


TEXTS = (
    ESPTimeCastTextDescription(
        key="time_zone",
        translation_key="time_zone",
        paths=("config.timeZone", "timeZone"),
        save_field="timeZone",
        native_max=80,
        mode=TextMode.TEXT,
        icon="mdi:map-clock",
    ),
    ESPTimeCastTextDescription(
        key="language",
        translation_key="language",
        paths=("config.language", "language"),
        save_field="language",
        action="language",
        native_max=16,
        mode=TextMode.TEXT,
        icon="mdi:translate",
    ),
    ESPTimeCastTextDescription(
        key="weather_city",
        translation_key="weather_city",
        paths=("config.openWeatherCity", "openWeatherCity"),
        save_field="openWeatherCity",
        native_max=64,
        mode=TextMode.TEXT,
        icon="mdi:map-marker",
    ),
    ESPTimeCastTextDescription(
        key="weather_country",
        translation_key="weather_country",
        paths=("config.openWeatherCountry", "openWeatherCountry"),
        save_field="openWeatherCountry",
        native_max=64,
        mode=TextMode.TEXT,
        icon="mdi:earth",
    ),
    ESPTimeCastTextDescription(
        key="message_to_send",
        translation_key="message_to_send",
        paths=("customMessage", "message"),
        send_message=True,
        native_max=255,
        mode=TextMode.TEXT,
        icon="mdi:message-arrow-right-outline",
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up ESPTimeCast text entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(ESPTimeCastText(coordinator, description) for description in TEXTS)


class ESPTimeCastText(ESPTimeCastEntity, TextEntity):
    """ESPTimeCast text entity."""

    entity_description: ESPTimeCastTextDescription

    def __init__(self, coordinator, description: ESPTimeCastTextDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> str | None:
        """Return current text value."""
        value: Any = value_at(self.coordinator.data, *self.entity_description.paths)
        if value in (None, ""):
            return None
        return str(value)

    async def async_set_value(self, value: str) -> None:
        """Set text value."""
        if self.entity_description.send_message:
            await self.coordinator.api.send_message(value)
        else:
            if self.entity_description.action:
                await self.coordinator.api.action(self.entity_description.action, value)
            if self.entity_description.save_field:
                await self.coordinator.api.save_config({self.entity_description.save_field: value})
        await self.coordinator.async_request_refresh()
