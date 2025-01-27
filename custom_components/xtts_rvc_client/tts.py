"""Integration support for the XTTS + RVC platform."""

from typing import Any
import re

from .client import XTTSRVCClient
from .types import GenerateAudioRequest
from homeassistant.components.tts import TextToSpeechEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    STATE_OK,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


SUPPORT_LANGUAGES = ["en"]
DEFAULT_LANG = "en"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the TTS platform for XTTS + RVC Client."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([XTTSRVC(DEFAULT_LANG, config)])


class XTTSRVC(TextToSpeechEntity):
    """Main TTS entity."""

    _attr_has_entity_name = True

    def __init__(self, lang: str, config: dict[str, Any]) -> None:
        """Initialize prerequisites."""
        self._lang = lang

        self._status = STATE_UNKNOWN
        self.host = config[CONF_HOST]
        self.port = config[CONF_PORT]

        self.client = XTTSRVCClient(self.host, self.port)

    @property
    def name(self) -> str:
        """Return the name of the TTS entity."""
        return "XTTS + RVC Client"

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the entity."""
        return f"xtts_rvc_client_{self.entity_id}"

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return self._lang

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return SUPPORT_LANGUAGES

    @property
    def should_poll(self) -> bool:
        """Return True to enable polling."""
        return True

    async def async_update(self):
        """Periodically update the status of the TTS service."""
        try:
            if await self.client.health_check():
                self._status = STATE_OK
                return
            self._status = STATE_UNAVAILABLE
        except Exception:
            self._status = STATE_UNAVAILABLE

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ):
        """Load tts audio file from the engine."""

        msg_clean = re.sub(r'[^\w\s\.\?!,]', '', message)
        request_data = GenerateAudioRequest(message=msg_clean)
        wav_data = await self.client.generate_audio(request_data)
        return ("wav", wav_data)
