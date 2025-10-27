"""Light platform for iPixel Color."""
from homeassistant.components.light import LightEntity

class IPixelLight(LightEntity):
    """iPixel Matrix Light."""
    @property
    def name(self):
        return "iPixel Matrix"
