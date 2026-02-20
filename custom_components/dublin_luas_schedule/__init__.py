"""Dublin Luas Schedule integration for Home Assistant."""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import LuasDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

CARD_FILENAME = "luas-schedule-card.js"
COMMUNITY_DIR_NAME = "dublin-luas-schedule"
CARD_URL = f"/hacsfiles/{COMMUNITY_DIR_NAME}/{CARD_FILENAME}"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Dublin Luas Schedule component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dublin Luas Schedule from a config entry."""
    stop_code = entry.data["stop_code"]
    stop_name = entry.data["stop_name"]

    coordinator = LuasDataUpdateCoordinator(hass, stop_code, stop_name)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Copy the Lovelace card (only once across all config entries)
    if not hass.data[DOMAIN].get("card_registered"):
        hass.data[DOMAIN]["card_registered"] = True
        await _copy_card_to_www(hass)
        # We no longer auto-register the Lovelace resource due to race conditions
        # that could cause other resources to be overwritten/removed.
        # Users must add it manually or via HACS.

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _copy_card_to_www(hass: HomeAssistant) -> None:
    """Copy the Lovelace card JS to /config/www/community/dublin-luas-schedule/."""
    source = Path(__file__).parent / "www" / CARD_FILENAME
    dest_dir = Path(hass.config.path("www")) / "community" / COMMUNITY_DIR_NAME
    dest_file = dest_dir / CARD_FILENAME

    if not source.exists():
        _LOGGER.error("Luas card source not found: %s", source)
        return

    try:

        def _do_copy() -> None:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source), str(dest_file))

        await hass.async_add_executor_job(_do_copy)
        _LOGGER.info("Copied %s to %s", CARD_FILENAME, dest_file)
    except Exception:
        _LOGGER.exception("Failed to copy Luas card JS")


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
