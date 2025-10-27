from __future__ import annotations

from typing import Any, Final
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    MATRIX_SIZES,
    DISPLAY_MODES,
    CLOCK_FORMATS,
    VISUAL_EFFECTS,
    CONF_MATRIX_WIDTH,
    CONF_MATRIX_HEIGHT,
    CONF_MATRIX_ORIENTATION,
    CONF_MAC_ADDRESS,
    CONF_TRANSPORT,
    CONF_HOST,
    CONF_PORT,
    DEFAULT_WIFI_PORT,
)

LANGUAGES: list[tuple[str, str]] = [
    ("auto", "Auto"),
    ("en", "English"),
    ("hu", "Magyar"),
]

CONF_LANGUAGE: Final = "language"

DEFAULT_WIDTH: Final = 96
DEFAULT_HEIGHT: Final = 16
DEFAULT_ORIENTATION: Final = 0

SETUP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MATRIX_WIDTH, default=DEFAULT_WIDTH): vol.All(int, vol.Range(min=8, max=256)),
        vol.Required(CONF_MATRIX_HEIGHT, default=DEFAULT_HEIGHT): vol.All(int, vol.Range(min=8, max=256)),
        vol.Required(CONF_MATRIX_ORIENTATION, default=DEFAULT_ORIENTATION): vol.In([0, 90, 180, 270]),
        vol.Optional(CONF_MAC_ADDRESS, default=""): str,
        vol.Optional(CONF_TRANSPORT, default="ble"): vol.In(["ble", "wifi"]),
        vol.Optional(CONF_HOST, default=""): str,
        vol.Optional(CONF_PORT, default=DEFAULT_WIFI_PORT): vol.All(int, vol.Range(min=1, max=65535)),
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional("display_mode", default="clock"): vol.In(DISPLAY_MODES),
        vol.Optional("clock_format", default="24h"): vol.In(CLOCK_FORMATS),
        vol.Optional("show_date", default=True): bool,
        vol.Optional("show_seconds", default=False): bool,
        vol.Optional("scroll_speed", default=50): vol.All(int, vol.Range(min=1, max=100)),
        vol.Optional("effect", default="off"): vol.In(VISUAL_EFFECTS),
        vol.Optional("effect_speed", default=50): vol.All(int, vol.Range(min=1, max=100)),
        vol.Optional("music_rhythm", default=False): bool,
        vol.Optional("music_sensitivity", default=50): vol.All(int, vol.Range(min=1, max=100)),
        vol.Optional(CONF_MATRIX_WIDTH): vol.All(int, vol.Range(min=8, max=256)),
        vol.Optional(CONF_MATRIX_HEIGHT): vol.All(int, vol.Range(min=8, max=256)),
        vol.Optional(CONF_MATRIX_ORIENTATION): vol.In([0, 90, 180, 270]),
        vol.Optional(CONF_LANGUAGE, default="auto"): vol.In([code for code, _ in LANGUAGES]),
        vol.Optional(CONF_TRANSPORT, default="ble"): vol.In(["ble", "wifi"]),
        vol.Optional(CONF_HOST, default=""): str,
        vol.Optional(CONF_PORT, default=DEFAULT_WIFI_PORT): vol.All(int, vol.Range(min=1, max=65535)),
    }
)

LANG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_LANGUAGE, default="hu"): vol.In([code for code, _ in LANGUAGES]),
    }
)


class IPixelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for iPixel Color."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        self._selected_language: str = "hu"

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Entry point: language selection first."""
        if user_input is None:
            return await self.async_step_language()
        return await self.async_step_language()

    async def async_step_language(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Language selection step."""
        if user_input is not None:
            self._selected_language = user_input.get(CONF_LANGUAGE, "hu")
            return await self.async_step_setup()

        return self.async_show_form(
            step_id="language",
            data_schema=LANG_SCHEMA,
            description_placeholders={
                "language_hint": "Choose the language for this integration",
            },
        )

    async def async_step_setup(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Matrix size/orientation and optional MAC address."""
        errors: dict[str, str] = {}

        if user_input is not None:
            width = user_input[CONF_MATRIX_WIDTH]
            height = user_input[CONF_MATRIX_HEIGHT]

            if (width, height) not in MATRIX_SIZES.values():
                pass

            data = dict(user_input)
            data[CONF_LANGUAGE] = self._selected_language

            unique_id = None
            mac = (user_input.get(CONF_MAC_ADDRESS) or "").strip().upper()
            if mac:
                unique_id = mac

            if unique_id:
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

            return self.async_create_entry(title="iPixel Color", data=data)

        return self.async_show_form(
            step_id="setup",
            data_schema=SETUP_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Options flow instance."""
        return IPixelOptionsFlow(config_entry)


class IPixelOptionsFlow(config_entries.OptionsFlow):
    """Options Flow: GUI-editable settings."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Options initial step."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        suggested = dict(self.config_entry.options)
        for k in (CONF_MATRIX_WIDTH, CONF_MATRIX_HEIGHT, CONF_MATRIX_ORIENTATION, CONF_LANGUAGE, CONF_TRANSPORT, CONF_HOST, CONF_PORT):
            if k not in suggested and k in self.config_entry.data:
                suggested[k] = self.config_entry.data[k]

        schema = self.add_suggested_values_to_schema(OPTIONS_SCHEMA, suggested)
        return self.async_show_form(step_id="init", data_schema=schema)
