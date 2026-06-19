"""Config flow for ESPTimeCast."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import voluptuous as vol
from aiohttp import ClientSession
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client, selector

from .api import ESPTimeCastApi, ESPTimeCastError
from .const import CONF_PORT, DEFAULT_PORT, DOMAIN


def _normalize_host_and_port(host_input: str, port_input: Any) -> tuple[str, int]:
    """Normalize a user-entered host or URL into host and port."""
    raw_host = host_input.strip()
    parsed = urlparse(raw_host if "://" in raw_host else f"//{raw_host}")
    host = parsed.hostname or raw_host.split("/")[0]
    port = int(parsed.port or port_input or DEFAULT_PORT)
    return host, port


class ESPTimeCastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an ESPTimeCast config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                host, port = _normalize_host_and_port(
                    user_input[CONF_HOST],
                    user_input.get(CONF_PORT, DEFAULT_PORT),
                )
            except ValueError:
                errors["base"] = "invalid_host"
            else:
                session: ClientSession = aiohttp_client.async_get_clientsession(self.hass)
                api = ESPTimeCastApi(session, host, port)

                try:
                    status = await api.status()
                except ESPTimeCastError:
                    errors["base"] = "cannot_connect"
                else:
                    unique_id = host.lower()
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured(updates={CONF_HOST: host, CONF_PORT: port})

                    title = status.get("id") or f"ESPTimeCast {host}"
                    return self.async_create_entry(
                        title=title,
                        data={CONF_HOST: host, CONF_PORT: port},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    ),
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=65535,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
            errors=errors,
        )
