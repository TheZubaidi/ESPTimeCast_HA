"""Data coordinator for ESPTimeCast."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ESPTimeCastApi, ESPTimeCastError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ESPTimeCastCoordinator(DataUpdateCoordinator[dict]):
    """Coordinate status polling."""

    def __init__(self, hass, api: ESPTimeCastApi, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.api = api
        self.entry = entry

    async def _async_update_data(self) -> dict:
        """Fetch data from the ESPTimeCast device."""
        try:
            return await self.api.status()
        except ESPTimeCastError as err:
            raise UpdateFailed(str(err)) from err
