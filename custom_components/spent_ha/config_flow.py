from __future__ import annotations

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_SPENT_URL, DEFAULT_URL, DOMAIN

STEP_SCHEMA = vol.Schema({
    vol.Required(CONF_SPENT_URL, default=DEFAULT_URL): str,
})


class SpentConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            url = user_input[CONF_SPENT_URL].rstrip("/")
            try:
                session = async_get_clientsession(self.hass)
                async with session.get(f"{url}/api/health", timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        await self.async_set_unique_id(url)
                        self._abort_if_unique_id_configured()
                        return self.async_create_entry(
                            title="Spent Finance",
                            data={CONF_SPENT_URL: url},
                        )
                    errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_SCHEMA,
            errors=errors,
        )
