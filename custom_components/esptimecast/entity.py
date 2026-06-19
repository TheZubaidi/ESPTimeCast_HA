"""Shared ESPTimeCast entity helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ESPTimeCastCoordinator


def value_at(data: Mapping[str, Any], *paths: str) -> Any:
    """Return a nested value using the first matching dot-notation path."""
    for path in paths:
        current: Any = data
        for part in path.split("."):
            if not isinstance(current, Mapping):
                current = None
                break
            current = current.get(part)
        if current is not None:
            return current
    return None


class ESPTimeCastEntity(CoordinatorEntity[ESPTimeCastCoordinator]):
    """Base ESPTimeCast entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ESPTimeCastCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.device_id}_{key}"

    @property
    def device_id(self) -> str:
        """Return a stable device id."""
        return str(self.coordinator.entry.unique_id or self.coordinator.entry.entry_id).lower()

    @property
    def device_info(self) -> DeviceInfo:
        """Return HA device info."""
        data = self.coordinator.data
        return DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            name=data.get("id") or "ESPTimeCast",
            manufacturer="M-Factory",
            model=data.get("hardware"),
            sw_version=data.get("version"),
            configuration_url=self.coordinator.api.base_url,
        )
