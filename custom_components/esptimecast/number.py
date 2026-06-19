"""Number platform for ESPTimeCast."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ESPTimeCastEntity

BRIGHTNESS = NumberEntityDescription(
    key="brightness",
    translation_key="brightness",
    native_min_value=0,
    native_max_value=15,
    native_step=1,
    mode=NumberMode.SLIDER,
    icon="mdi:brightness-6",
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up ESPTimeCast number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ESPTimeCastBrightnessNumber(coordinator)])


class ESPTimeCastBrightnessNumber(ESPTimeCastEntity, NumberEntity):
    """ESPTimeCast brightness control."""

    entity_description = BRIGHTNESS

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "brightness")

    @property
    def native_value(self) -> int | None:
        """Return current brightness."""
        return self.coordinator.data.get("brightness")

    async def async_set_native_value(self, value: float) -> None:
        """Set display brightness."""
        await self.coordinator.api.action("brightness", int(value))
        await self.coordinator.async_request_refresh()
