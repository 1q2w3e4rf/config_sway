#!/usr/bin/env python3
import json
import subprocess

def get_notifications():
    try:
        count = int(subprocess.check_output(["swaync-client", "-c"]).decode())
        dnd = subprocess.check_output(["swaync-client", "-D"]).decode().strip() == "true"
        icon = "" if dnd else "" if count > 0 else ""
        return {
            "text": str(count) if count > 0 else "",
            "tooltip": f"{count} уведомлений" if count > 0 else "Режим 'Не беспокоить'" if dnd else "Нет уведомлений",
            "class": "dnd" if dnd else "active" if count > 0 else "inactive"
        }
    except:
        return {"text": "", "tooltip": "Ошибка уведомлений"}

print(json.dumps(get_notifications()))
