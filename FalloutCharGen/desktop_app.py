"""Wasteland Recruit for Windows: shows the shared web app (../web) in a native window.

Everything is stored next to the .exe so the app stays portable:
  Fallout Characters/   saved character sheet images
  Wasteland Data/       saved characters, edited loot tables, perk cache
"""
import base64
import os
import re
import sys

import webview


def base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def web_dir():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "web")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web")


def safe(name, default="file"):
    return re.sub(r"[^A-Za-z0-9 ._-]+", "", str(name)).strip() or default


class Api:
    """Methods callable from JavaScript as window.pywebview.api.<name>()."""

    def _data(self, key):
        d = os.path.join(base_dir(), "Wasteland Data")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, safe(key, "data") + ".json")

    def load(self, key):
        try:
            with open(self._data(key), encoding="utf-8") as f:
                return f.read()
        except OSError:
            return None

    def save(self, key, text):
        try:
            path = self._data(key)
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, path)  # never leaves a half-written file behind
            return "OK"
        except OSError as e:
            return f"ERROR: {e}"

    def save_image(self, data_url, name):
        try:
            d = os.path.join(base_dir(), "Fallout Characters")
            os.makedirs(d, exist_ok=True)
            path = os.path.join(d, safe(name, "character.png"))
            with open(path, "wb") as f:
                f.write(base64.b64decode(data_url.split(",", 1)[1]))
            return path
        except Exception as e:  # noqa: BLE001 - message goes back to the UI
            return f"ERROR: {e}"


if __name__ == "__main__":
    webview.create_window("Wasteland Recruit", os.path.join(web_dir(), "index.html"),
                          js_api=Api(), width=1180, height=880, min_size=(420, 600),
                          background_color="#16181D", text_select=True)
    webview.start(http_server=True)
