"""Device communication layer for iPixel Color."""
from __future__ import annotations
from typing import Optional

class IPixelColorDevice:
    """Represents an iPixel Color device."""

    def __init__(self, mac_address: str | None = None, host: str | None = None, port: int = 8800):
        """Initialize device."""
        self._mac = mac_address
        self._host = host
        self._port = port
        self._connected = False

    async def async_connect(self):
        """Connect to device (BLE or WiFi)."""
        self._connected = True

    async def async_disconnect(self):
        """Disconnect from device."""
        self._connected = False

    async def apply_options(self, **opts):
        """Apply options changes instantly (called by options_update_listener)."""
        # Implementation: parse opts and send commands to device
        pass
