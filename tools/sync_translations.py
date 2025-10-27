"""Sync translation keys from strings.json to all language files."""
from __future__ import annotations
import json
from pathlib import Path

SECTIONS = ["config", "options", "entity", "services"]
BASE = Path(__file__).resolve().parents[1] / "custom_components" / "ipixel_color"
STRINGS = BASE / "strings.json"
TRANS = BASE / "translations"

def deep_merge_missing(dst, src):
    """Merge missing keys from src into dst."""
    for k, v in src.items():
        if isinstance(v, dict):
            dst.setdefault(k, {})
            if isinstance(dst[k], dict):
                deep_merge_missing(dst[k], v)
            else:
                dst[k] = v
        else:
            dst.setdefault(k, v)

def main():
    """Sync all translation files."""
    if not STRINGS.exists():
        raise FileNotFoundError(f"Missing {STRINGS}")

    base = json.loads(STRINGS.read_text(encoding="utf-8"))
    base_subset = {k: base.get(k, {}) for k in SECTIONS}

    for p in sorted(TRANS.glob("*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        for sec in SECTIONS:
            data.setdefault(sec, {})
            deep_merge_missing(data[sec], base_subset[sec])
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Synced {p.name}")

    print("Translation sync complete!")

if __name__ == "__main__":
    main()
