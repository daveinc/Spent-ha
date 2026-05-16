from __future__ import annotations

from datetime import timedelta
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_SPENT_URL, DOMAIN, SCAN_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)


class SpentCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.spent_url = entry.data[CONF_SPENT_URL]
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict:
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                f"{self.spent_url}/api/home",
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"Spent returned HTTP {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with Spent: {err}") from err
