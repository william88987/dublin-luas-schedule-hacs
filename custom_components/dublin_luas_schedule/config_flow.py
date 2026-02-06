"""Config flow for Dublin Luas Schedule integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, LUAS_STOPS, ALL_STOPS

_LOGGER = logging.getLogger(__name__)


class LuasScheduleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dublin Luas Schedule."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._selected_line: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - select Luas line."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._selected_line = user_input["line"]
            return await self.async_step_stop()

        # Build line selection schema
        lines = list(LUAS_STOPS.keys())
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("line"): vol.In(lines),
                }
            ),
            errors=errors,
        )

    async def async_step_stop(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle stop selection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            stop_code = user_input["stop"]
            stop_name = ALL_STOPS[stop_code]

            # Check if this stop is already configured
            await self.async_set_unique_id(stop_code)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=stop_name,
                data={
                    "stop_code": stop_code,
                    "stop_name": stop_name,
                    "line": self._selected_line,
                },
            )

        # Build stop selection schema for selected line
        if self._selected_line and self._selected_line in LUAS_STOPS:
            stops = LUAS_STOPS[self._selected_line]
            # Create a dict with code as key and "Name (CODE)" as value for display
            stop_options = {code: f"{name}" for code, name in stops.items()}
        else:
            stop_options = {code: name for code, name in ALL_STOPS.items()}

        return self.async_show_form(
            step_id="stop",
            data_schema=vol.Schema(
                {
                    vol.Required("stop"): vol.In(stop_options),
                }
            ),
            errors=errors,
            description_placeholders={"line": self._selected_line or "All Lines"},
        )
