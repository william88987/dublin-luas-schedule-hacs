"""Dublin Luas Schedule integration for Home Assistant."""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import LuasDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

CARD_FILENAME = "luas-schedule-card.js"
COMMUNITY_DIR_NAME = "dublin-luas-schedule"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Dublin Luas Schedule component."""
    hass.data.setdefault(DOMAIN, {})

    # Copy the Lovelace card JS to /config/www/community/ and register it
    try:
        await _copy_card_to_www(hass)

        card_url = f"/hacsfiles/{COMMUNITY_DIR_NAME}/{CARD_FILENAME}"
        add_extra_js_url(hass, card_url)

        _LOGGER.info(
            "Registered Luas Schedule card at %s", card_url
        )
    except Exception:  # noqa: BLE001
        _LOGGER.exception("Failed to copy Luas Schedule card to www/community")

    return True


async def _copy_card_to_www(hass: HomeAssistant) -> None:
    """Copy the Lovelace card JS to /config/www/community/dublin-luas-schedule/."""
    source = Path(__file__).parent / "www" / CARD_FILENAME
    dest_dir = Path(hass.config.path("www")) / "community" / COMMUNITY_DIR_NAME
    dest_file = dest_dir / CARD_FILENAME

    def _do_copy() -> None:
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source), str(dest_file))

    await hass.async_add_executor_job(_do_copy)
    _LOGGER.info(
        "Copied %s to %s", CARD_FILENAME, dest_dir
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dublin Luas Schedule from a config entry."""
    stop_code = entry.data["stop_code"]
    stop_name = entry.data["stop_name"]

    coordinator = LuasDataUpdateCoordinator(hass, stop_code, stop_name)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok






