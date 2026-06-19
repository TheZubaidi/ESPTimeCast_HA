"""Button platform for ESPTimeCast."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ESPTimeCastEntity


@dataclass(frozen=True, kw_only=True)
class ESPTimeCastButtonDescription(ButtonEntityDescription):
    """Describe an ESPTimeCast button."""

    action: str


BUTTONS = (
    ESPTimeCastButtonDescription(key="clear_message", translation_key="clear_message", action="clear_message", icon="mdi:message-off-outline"),
    ESPTimeCastButtonDescription(key="next_mode", translation_key="next_mode", action="next_mode", icon="mdi:skip-next"),
    ESPTimeCastButtonDescription(key="previous_mode", translation_key="previous_mode", action="prev_mode", icon="mdi:skip-previous"),
    ESPTimeCastButtonDescription(key="restart", translation_key="restart", action="restart", icon="mdi:restart"),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up ESPTimeCast buttons."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(ESPTimeCastButton(coordinator, description) for description in BUTTONS)


class ESPTimeCastButton(ESPTimeCastEntity, ButtonEntity):
    """ESPTimeCast action button."""

    entity_description: ESPTimeCastButtonDescription

    def __init__(self, coordinator, description: ESPTimeCastButtonDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Run the button action."""
        await self.coordinator.api.action(self.entity_description.action)
        await self.coordinator.async_request_refresh()
