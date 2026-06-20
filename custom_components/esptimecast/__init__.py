"""The ESPTimeCast integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client, config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .api import (
    ESPTimeCastApi,
    ESPTimeCastConflictError,
    ESPTimeCastConnectionError,
)
from .const import (
    ATTR_ACTION,
    ATTR_BIG_NUMBERS,
    ATTR_CONFIG_ENTRY_ID,
    ATTR_DEVICE_ID,
    ATTR_INTERRUPT,
    ATTR_MESSAGE,
    ATTR_SCROLLS,
    ATTR_SECONDS,
    ATTR_SPEED,
    ATTR_VALUE,
    CONF_PORT,
    DEFAULT_PORT,
    DOMAIN,
    PLATFORMS,
    SERVICE_ACTION,
    SERVICE_CLEAR_MESSAGE,
    SERVICE_SEND_MESSAGE,
)
from .coordinator import ESPTimeCastCoordinator

_LOGGER = logging.getLogger(__name__)

OBSOLETE_ENTITY_KEYS = {
    "binary_sensor": {
        "allow_interrupt",
        "auto_dimming_enabled",
        "countdown_enabled",
        "dimming_enabled",
        "nightscout_active",
        "nightscout_outdated",
    },
    "button": {
        "pomodoro_stop",
        "stopwatch_stop",
        "timer_stop",
    },
    "sensor": {
        "board",
        "countdown_label",
        "countdown_remaining",
        "device_runtime",
        "instagram_followers",
        "language",
        "message",
        "nightscout_glucose",
        "nightscout_trend",
        "session_runtime",
        "sns_type",
        "timezone",
        "version",
        "weather_description",
        "youtube_subscribers",
    },
}

SEND_MESSAGE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Optional(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_SECONDS): vol.All(vol.Coerce(int), vol.Range(min=0, max=3600)),
        vol.Optional(ATTR_SCROLLS): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_SPEED): vol.All(vol.Coerce(int), vol.Range(min=10, max=200)),
        vol.Optional(ATTR_BIG_NUMBERS): cv.boolean,
        vol.Optional(ATTR_INTERRUPT): cv.boolean,
    }
)

ACTION_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Optional(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_ACTION): cv.string,
        vol.Optional(ATTR_VALUE): vol.Any(cv.string, vol.Coerce(int), cv.boolean),
    }
)

CLEAR_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Optional(ATTR_DEVICE_ID): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ESPTimeCast from a config entry."""
    session = aiohttp_client.async_get_clientsession(hass)
    api = ESPTimeCastApi(
        session,
        entry.data[CONF_HOST],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
    )
    coordinator = ESPTimeCastCoordinator(hass, api, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    _async_remove_obsolete_entities(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _async_register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_SEND_MESSAGE)
            hass.services.async_remove(DOMAIN, SERVICE_CLEAR_MESSAGE)
            hass.services.async_remove(DOMAIN, SERVICE_ACTION)
    return unload_ok


def _async_register_services(hass: HomeAssistant) -> None:
    """Register integration services once."""
    if hass.services.has_service(DOMAIN, SERVICE_SEND_MESSAGE):
        return

    async def send_message(call: ServiceCall) -> None:
        coordinator = _get_service_coordinator(hass, call)
        try:
            await coordinator.api.send_message(
                call.data[ATTR_MESSAGE],
                seconds=call.data.get(ATTR_SECONDS),
                scrolls=call.data.get(ATTR_SCROLLS),
                speed=call.data.get(ATTR_SPEED),
                big_numbers=call.data.get(ATTR_BIG_NUMBERS),
                interrupt=call.data.get(ATTR_INTERRUPT),
            )
        except ESPTimeCastConflictError as err:
            raise HomeAssistantError(str(err)) from err
        except ESPTimeCastConnectionError as err:
            raise HomeAssistantError(f"Could not send ESPTimeCast message: {err}") from err
        await coordinator.async_request_refresh()

    async def clear_message(call: ServiceCall) -> None:
        coordinator = _get_service_coordinator(hass, call)
        try:
            await coordinator.api.clear_message()
        except ESPTimeCastConnectionError as err:
            raise HomeAssistantError(f"Could not clear ESPTimeCast message: {err}") from err
        await coordinator.async_request_refresh()

    async def action(call: ServiceCall) -> None:
        coordinator = _get_service_coordinator(hass, call)
        try:
            await coordinator.api.action(call.data[ATTR_ACTION], call.data.get(ATTR_VALUE))
        except ESPTimeCastConflictError as err:
            raise HomeAssistantError(str(err)) from err
        except ESPTimeCastConnectionError as err:
            raise HomeAssistantError(f"Could not run ESPTimeCast action: {err}") from err
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, SERVICE_SEND_MESSAGE, send_message, SEND_MESSAGE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_CLEAR_MESSAGE, clear_message, CLEAR_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_ACTION, action, ACTION_SCHEMA)


def _async_remove_obsolete_entities(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove entities from older ESPTimeCast versions that are no longer created."""
    registry = er.async_get(hass)
    for entity_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        obsolete_keys = OBSOLETE_ENTITY_KEYS.get(entity_entry.domain)
        if not obsolete_keys:
            continue
        unique_id = entity_entry.unique_id or ""
        if any(unique_id.endswith(f"_{key}") for key in obsolete_keys):
            registry.async_remove(entity_entry.entity_id)


def _get_service_coordinator(hass: HomeAssistant, call: ServiceCall) -> ESPTimeCastCoordinator:
    """Get the target coordinator for a service call."""
    coordinators: dict[str, ESPTimeCastCoordinator] = hass.data.get(DOMAIN, {})
    entry_id = call.data.get(ATTR_CONFIG_ENTRY_ID)
    if entry_id:
        if entry_id not in coordinators:
            raise HomeAssistantError(f"Unknown ESPTimeCast config entry: {entry_id}")
        return coordinators[entry_id]

    device_id = call.data.get(ATTR_DEVICE_ID)
    if device_id:
        device = dr.async_get(hass).async_get(device_id)
        if device is None:
            raise HomeAssistantError(f"Unknown ESPTimeCast device: {device_id}")
        for device_entry_id in device.config_entries:
            if device_entry_id in coordinators:
                return coordinators[device_entry_id]
        raise HomeAssistantError("Selected device is not an ESPTimeCast device")

    if len(coordinators) == 1:
        return next(iter(coordinators.values()))

    raise HomeAssistantError("Set config_entry_id when more than one ESPTimeCast device is configured")
