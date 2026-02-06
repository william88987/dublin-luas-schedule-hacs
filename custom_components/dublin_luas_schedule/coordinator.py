"""Data update coordinator for Dublin Luas Schedule."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any
import xml.etree.ElementTree as ET

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import API_URL, DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class LuasDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Luas schedule data."""

    def __init__(self, hass: HomeAssistant, stop_code: str, stop_name: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Luas {stop_name}",
            update_interval=UPDATE_INTERVAL,
        )
        self.stop_code = stop_code
        self.stop_name = stop_name

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Luas API."""
        try:
            async with async_timeout.timeout(10):
                return await self._fetch_luas_data()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with Luas API: {err}") from err
        except ET.ParseError as err:
            raise UpdateFailed(f"Error parsing Luas XML response: {err}") from err

    async def _fetch_luas_data(self) -> dict[str, Any]:
        """Fetch and parse Luas schedule data."""
        url = f"{API_URL}?action=forecast&stop={self.stop_code}&encrypt=false"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                xml_text = await response.text()

        return self._parse_xml(xml_text)

    def _parse_xml(self, xml_text: str) -> dict[str, Any]:
        """Parse the Luas XML response."""
        root = ET.fromstring(xml_text)
        now = dt_util.now()
        
        data = {
            "stop": root.get("stop", self.stop_name),
            "stop_code": root.get("stopAbv", self.stop_code),
            "message": "",
            "inbound": [],
            "outbound": [],
            "last_updated": now.isoformat(),
        }

        # Get status message
        message_elem = root.find("message")
        if message_elem is not None and message_elem.text:
            data["message"] = message_elem.text

        # Parse directions
        for direction in root.findall("direction"):
            direction_name = direction.get("name", "").lower()
            trams = []
            
            for tram in direction.findall("tram"):
                due_mins = tram.get("dueMins", "")
                destination = tram.get("destination", "")
                
                # Calculate exact arrival time
                arrival_time = None
                arrival_time_str = ""
                if due_mins == "DUE":
                    due_display = "DUE"
                    arrival_time = now
                    arrival_time_str = now.strftime("%H:%M")
                elif due_mins and due_mins.isdigit():
                    due_display = f"{due_mins} min"
                    arrival_time = now + timedelta(minutes=int(due_mins))
                    arrival_time_str = arrival_time.strftime("%H:%M")
                else:
                    due_display = "Unknown"
                
                trams.append({
                    "destination": destination,
                    "due": due_display,
                    "due_mins": due_mins,
                    "arrival_time": arrival_time_str,
                })
            
            if "inbound" in direction_name:
                data["inbound"] = trams
            elif "outbound" in direction_name:
                data["outbound"] = trams

        return data

