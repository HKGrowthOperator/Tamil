#!/usr/bin/env python3
"""Baut artifact.html aus index.html: ohne doctype/html/head/body, Schriften, Bilder und Punktbogen als data-URI.

Aufruf im Ordner: python3 bauen.py
"""
import base64
import pathlib
import re

ORT = pathlib.Path(__file__).parent
TYP = {".webp": "image/webp", ".svg": "image/svg+xml", ".woff2": "font/woff2"}


def daten(pfad: str) -> str:
    datei = ORT / pfad
    return f"data:{TYP[datei.suffix]};base64,{base64.b64encode(datei.read_bytes()).decode()}"


html = (ORT / "index.html").read_text(encoding="utf-8")
titel = re.search(r"<title>.*?</title>", html).group(0)
stil = re.search(r"<style>.*?</style>", html, re.S).group(0)
rumpf = re.search(r"<body>(.*)</body>", html, re.S).group(1)

# Verweise auf lokale Dateien ersetzen: url("…") im CSS, src="…" im Rumpf
stil = re.sub(r'url\("([^"]+\.(?:webp|svg|woff2))"\)', lambda m: f'url("{daten(m.group(1))}")', stil)
rumpf = re.sub(r'src="([^"]+\.webp)"', lambda m: f'src="{daten(m.group(1))}"', rumpf)

aus = f'{titel}\n<meta name="viewport" content="width=device-width, initial-scale=1">\n{stil}\n{rumpf.strip()}\n'
(ORT / "artifact.html").write_text(aus, encoding="utf-8")
print(f"artifact.html: {len(aus.encode()) / 1024:.0f} KB")
