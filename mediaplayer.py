#!/usr/bin/env python3
# /etc/xdg/waybar/
import json
import subprocess

def get_media():
    try:
        status = subprocess.check_output(["playerctl", "status"]).decode().strip()
        if status == "Playing":
            artist = subprocess.check_output(["playerctl", "metadata", "artist"]).decode().strip()
            title = subprocess.check_output(["playerctl", "metadata", "title"]).decode().strip()
            text = f"{artist} - {title}" if artist else title
            return {
                "text": text[:40] + "..." if len(text) > 40 else text,
                "tooltip": f"Сейчас играет: {text}",
                "class": "playing"
            }
        return {"text": "", "tooltip": "Нет активного плеера"}
    except:
        return {"text": "", "tooltip": "Ошибка плеера"}

print(json.dumps(get_media()))
