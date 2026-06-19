"""HTTP client for ESPTimeCast devices."""

from __future__ import annotations

import async_timeout
from aiohttp import ClientError, ClientResponseError, ClientSession

from .const import REQUEST_TIMEOUT


class ESPTimeCastError(Exception):
    """Base ESPTimeCast error."""


class ESPTimeCastConnectionError(ESPTimeCastError):
    """Raised when the device cannot be reached."""


class ESPTimeCastConflictError(ESPTimeCastError):
    """Raised when a protected message refuses interruption."""


class ESPTimeCastApi:
    """Small async client for the ESPTimeCast local API."""

    def __init__(self, session: ClientSession, host: str, port: int) -> None:
        self._session = session
        self.host = host.strip()
        self.port = port

    @property
    def base_url(self) -> str:
        """Return the base device URL."""
        return f"http://{self.host}:{self.port}"

    async def status(self) -> dict:
        """Fetch device status."""
        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT):
                response = await self._session.get(f"{self.base_url}/status")
                response.raise_for_status()
                data = await response.json(content_type=None)
        except (ClientError, TimeoutError) as err:
            raise ESPTimeCastConnectionError(str(err)) from err

        if not isinstance(data, dict):
            raise ESPTimeCastConnectionError("Unexpected status response")
        return data

    async def action(self, action: str, value: str | int | None = None) -> None:
        """Send a generic action to the device."""
        payload = {action: "" if value is None else str(value)}
        await self._post_action(payload)

    async def send_message(
        self,
        message: str,
        *,
        seconds: int | None = None,
        scrolls: int | None = None,
        speed: int | None = None,
        big_numbers: bool | None = None,
        interrupt: bool | None = None,
    ) -> None:
        """Display a temporary message."""
        payload: dict[str, str | int] = {"message": message}
        if seconds is not None:
            payload["seconds"] = seconds
        if scrolls is not None:
            payload["scrolls"] = scrolls
        if speed is not None:
            payload["speed"] = speed
        if big_numbers is not None:
            payload["bignumbers"] = int(big_numbers)
        if interrupt is not None:
            payload["interrupt"] = int(interrupt)
        await self._post_action(payload)

    async def clear_message(self) -> None:
        """Clear the current temporary message."""
        await self.action("clear_message")

    async def _post_action(self, payload: dict[str, str | int]) -> None:
        """POST form data to /action."""
        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT):
                response = await self._session.post(
                    f"{self.base_url}/action",
                    data=payload,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                if response.status == 409:
                    raise ESPTimeCastConflictError("Device is showing a protected message")
                response.raise_for_status()
        except ESPTimeCastConflictError:
            raise
        except (ClientResponseError, ClientError, TimeoutError) as err:
            raise ESPTimeCastConnectionError(str(err)) from err
