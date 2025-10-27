# iPixel Color - Home Assistant Integráció

[![Licenc: MIT](https://img.shields.io/badge/apache-2-0.svg)](https://opensource.org/license/apache-2-0)

Teljes körű Home Assistant egyedi integráció iPixel Color LED mátrix panelek vezérléséhez Bluetooth LE és WiFi kapcsolaton keresztül.

## Jellemzők

- 🎨 **Teljes iPixel Color App Funkcióparitás**
- ⚙️ **GUI-ból Testreszabható** - minden beállítás Opciók menüből, YAML nélkül
- 📊 **Dashboard Kártyák** - használatra kész Lovelace kártyák
- 🔌 **BLE és WiFi Támogatás** - rugalmas kapcsolódás
- 🕐 **Testreszabható Óra** - több formátum és stílus
- 🎭 **Vizuális Effektek** - szivárvány, pulzálás, hullám, csillogás, zenei ritmus
- 🖼️ **Kép és Animáció** - egyedi képek és GIF-ek megjelenítése
- 🎨 **Doodle Mód** - pixelenkénti rajzolás

## Telepítés

### HACS-on keresztül (Ajánlott)

1. HACS megnyitása → Integrációk
2. ⋮ → Egyedi tárolók
3. Repository URL hozzáadása
4. "Integráció" kategória kiválasztása
5. "Hozzáadás"
6. "iPixel Color" keresése
7. "Letöltés"
8. Home Assistant újraindítása

### Kézi Telepítés

1. `custom_components/ipixel_color` másolása a `config/custom_components/` könyvtárba
2. Home Assistant újraindítása

## Konfiguráció

1. Beállítások → Eszközök és szolgáltatások
2. "+ Integráció hozzáadása"
3. "iPixel Color" keresése
4. Beállítási varázsló követése:
   - Nyelv választás
   - Mátrix méret
   - Kapcsolat beállítása (BLE vagy WiFi)
5. **Opciók** menü használata bármikor történő testreszabáshoz

## Támogatott Eszközök

- CHICIRIS 20×64 LED Panel
- UDITER Pixel Rider
- Általános 16×32, 16×64, 16×96, 20×64, 32×32 iPixel Color kompatibilis panelek

## Dashboard Kártyák

Lásd a `README.md` fájlt a használatra kész Lovelace kártya példákért.

## Dokumentáció

- [English Documentation](README.md)
- [Magyar dokumentáció](README.hu.md)

## Licenc

Apache License, Version 2.0 - lásd LICENSE fájl

## Támogatás

- [GitHub Issues](https://github.com/bekdan1988/ha-ipixel-color/issues)
- [Home Assistant Közösség](https://community.home-assistant.io/)
