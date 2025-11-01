# coordinator.py – kódrészlet: notify engedélyezés, szeletelés, robusztus write

from bleak.backends.characteristic import BleakGATTCharacteristic

class IPixelColorDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(...):
        ...
        self.write_characteristic: BleakGATTCharacteristic | None = None
        self.notify_characteristics: list[BleakGATTCharacteristic] = []

    async def _async_connect(self) -> None:
        if self.client and self.client.is_connected:
            return
        try:
            self.client = BleakClient(self.device_address)
            await self.client.connect()
            _LOGGER.info("Connected to %s", self.device_address)
            await self._discover_characteristics()
            await self._enable_notifications()
        except BleakError as err:
            raise UpdateFailed(f"Connection failed: {err}") from err

    async def _discover_characteristics(self) -> None:
        # Bleak a connect után tölti fel a services-t backendtől függően
        services = self.client.services
        self.write_characteristic = None
        self.notify_characteristics = []
        for service in services:
            for char in service.characteristics:
                props = set(char.properties or [])
                if "write_without_response" in props or "write" in props:
                    # Első írható karakterisztika
                    if not self.write_characteristic:
                        self.write_characteristic = char
                if "notify" in props:
                    self.notify_characteristics.append(char)
        if not self.write_characteristic:
            _LOGGER.error("No writable characteristic found")

    async def _enable_notifications(self) -> None:
        # Nem minden eszköz igényli, de tipikus a szükségessége
        async def _noop_cb(handle: int, data: bytearray) -> None:
            _LOGGER.debug("Notify %s: %s", handle, data.hex())
        for ch in self.notify_characteristics:
            try:
                await self.client.start_notify(ch, _noop_cb)
            except Exception as e:
                _LOGGER.debug("Notify enable failed on %s: %s", ch.uuid, e)

    def _max_write_size(self) -> int:
        # Bleak API: max write without response méret lekérdezése (backend-függő)
        # Ha nem elérhető, fallback: 20 bájt (MTU 23 -> 23-3)
        try:
            # A Bleak doksi szerint elérhető maximum write size response=False módban
            # Backendtől függően property vagy metódus lehet elérhető.
            size = getattr(self.client, "mtu_size", None)
            if isinstance(size, int) and size > 3:
                return max(20, size - 3)
        except Exception:
            pass
        return 20

    async def _send_raw(self, payload: bytearray) -> None:
        if not self.client or not self.client.is_connected:
            await self._async_connect()
        if not self.write_characteristic:
            raise UpdateFailed("Writable characteristic not found")

        max_chunk = self._max_write_size()
        offset = 0
        # Előny: write_without_response, ha a karakterisztika támogatja
        use_response = "write" in set(self.write_characteristic.properties or []) and \
                       "write_without_response" not in set(self.write_characteristic.properties or [])

        while offset < len(payload):
            chunk = payload[offset: offset + max_chunk]
            await self.client.write_gatt_char(self.write_characteristic, chunk, response=use_response)
            offset += len(chunk)