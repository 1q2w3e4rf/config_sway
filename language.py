#!/usr/bin/env python3
import json
import subprocess

def get_lang():
    try:
        output = subprocess.check_output(["swaymsg", "-t", "get_inputs"]).decode()
        data = json.loads(output)
        for device in data:
            if device["type"] == "keyboard":
                lang = device["xkb_active_layout_name"]
                icon = "🇷🇺" if "Russian" in lang else "🇺🇸" if "English" in lang else "⌨️"
                return {"text": f"{icon} {lang.split()[0]}", "tooltip": f"Язык: {lang}"}
        return {"text": "⌨️ None", "tooltip": "Не удалось определить раскладку"}
    except:
        return {"text": "⌨️ Error", "tooltip": "Ошибка получения раскладки"}

print(json.dumps(get_lang()))
