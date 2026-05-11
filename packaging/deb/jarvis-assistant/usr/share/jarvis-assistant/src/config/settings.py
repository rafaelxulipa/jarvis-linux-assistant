import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_FILE = os.path.join(BASE_DIR, "config", "jarvis.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")

DEFAULT_CONFIG = {
    "user_name": "Otávio",
    "voice_enabled": True,
    "voice_speed": 1.0,
    "tts_engine": "piper",          # "piper" | "espeak" | "gtts"
    "voice_gender": "male",         # "male" | "female"
    "voice_recognition": False,
    "wake_word": "jarvis",
    "openai_api_key": "",
    "favorite_projects": [],
    "browser": "firefox",
    "terminal": "gnome-terminal",
    "editor": "code",
    "show_weather": False,
    "weather_city": "São Paulo",
    "animations_enabled": True,
    "scanlines": True,
    "window_opacity": 0.95,
    "accent_color": "#00d4ff",
    "secondary_color": "#0066ff",
    "theme": "dark",
    "autostart": True,
    "boot_sounds": True,
    "update_interval_ms": 2000,
}

COLORS = {
    "bg_primary":     "#020a12",
    "bg_secondary":   "#041525",
    "bg_panel":       "#061e33",
    "bg_panel_alpha": "rgba(6,30,51,0.85)",
    "accent":         "#00d4ff",
    "accent2":        "#0066ff",
    "accent3":        "#00ff88",
    "accent_warn":    "#ffaa00",
    "accent_danger":  "#ff3355",
    "text_primary":   "#c8f0ff",
    "text_secondary": "#5a8fa8",
    "text_dim":       "#2a4a5e",
    "glow_cyan":      "rgba(0,212,255,0.3)",
    "glow_blue":      "rgba(0,102,255,0.3)",
    "border":         "rgba(0,212,255,0.25)",
    "border_bright":  "rgba(0,212,255,0.6)",
    "scanline":       "rgba(0,0,0,0.08)",
}

FONTS = {
    "mono":    "Courier New",
    "display": "Courier New",
    "ui":      "Segoe UI",
}


def load_config() -> dict:
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            cfg.update(saved)
        except Exception:
            pass
    return cfg


def save_config(cfg: dict) -> None:
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
