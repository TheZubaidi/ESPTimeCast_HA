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

    path: str
    action: str


SWITCHES = (
    ESPTimeCastSwitchDescription(key="display", translation_key="display", path="displayOff", action="display_off", icon="mdi:monitor"),
    ESPTimeCastSwitchDescription(key="flip_display", translation_key="flip_display", path="config.flipDisplay", action="flip", icon="mdi:rotate-3d-variant"),
    ESPTimeCastSwitchDescription(key="twelve_hour", translation_key="twelve_hour", path="config.twelveHourToggle", action="twelve_hour", icon="mdi:clock-time-four-outline"),
    ESPTimeCastSwitchDescription(key="show_date", translation_key="show_date", path="config.showDate", action="show_date", icon="mdi:calendar"),
    ESPTimeCastSwitchDescription(key="show_humidity", translation_key="show_humidity", path="config.showHumidity", action="humidity", icon="mdi:water-percent"),
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
        value: Any = value_at(self.coordinator.data, self.entity_description.path)
        if value is None:
            return None
        if self.entity_description.key == "display":
            return not bool(value)
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
            await self.coordinator.api.action(self.entity_description.action, int(state))
        await self.coordinator.async_request_refresh()
