"""Coolify-Betrieb für Tamil.de, ohne dass Geheimnisse in Ausgaben landen.

    python tools/coolify.py status [<uuid> …]           Stand der Apps (Standard: alle aus docs/betrieb.md)
    python tools/coolify.py deploy <uuid> [--force]      Deploy starten, warten, letzte Log-Zeilen zeigen
    python tools/coolify.py warten <deployment-uuid>     auf einen laufenden Deploy warten
    python tools/coolify.py envs <uuid>                  nur die NAMEN der Variablen (mit runtime/buildtime)
    python tools/coolify.py env-setzen <uuid> NAME=wert NAME=@zufall NAME=@datei:/pfad …
    python tools/coolify.py storages <uuid>              Volumes der App
    python tools/coolify.py api GET|POST|PATCH <pfad> [--json datei]   Rohaufruf, Antwort mit geschwärzten Werten

Token: Umgebungsvariable COOLIFY_TOKEN (nie ausgeben, nie in Dateien im Repo). Speichert der Sitzungs-Proxy den Token
für den Coolify-Host, genügt ein beliebiger Platzhalter, der Proxy setzt den echten Wert ein.
Basis-URL: COOLIFY_URL (Standard https://coolify.167.233.76.202.sslip.io).

`env-setzen` schreibt per envs/bulk als Laufzeit-Variable (is_buildtime=false, is_literal=false). `@zufall` erzeugt
einen zufälligen Wert (48 Zeichen) und gibt ihn NICHT aus; `@datei:` liest den Wert aus einer Datei (z. B. einer
Scratch-Datei mit Rechten 600). Angezeigt werden nur die Namen.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASIS = os.environ.get("COOLIFY_URL", "https://coolify.167.233.76.202.sslip.io").rstrip("/") + "/api/v1"
APPS = {"tamil.de (Radar + Cockpit)": "igq37g4vbxzhw5u19efuk9ip"}  # tamil-web wird nach dem Anlegen ergänzt
GEHEIM = ("value", "real_value", "token", "password", "secret", "key", "private", "webhook", "sealed")
ENDE = {"finished", "failed", "cancelled-by-user", "cancelled", "error"}


def schwaerzen(obj):
    """Alle Werte, deren Schlüssel nach Geheimnis klingen, durch *** ersetzen (rekursiv)."""
    if isinstance(obj, dict):
        return {k: ("***" if any(g in k.lower() for g in GEHEIM) and obj[k] not in (None, "", False, True)
                    and not isinstance(obj[k], (dict, list)) else schwaerzen(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [schwaerzen(x) for x in obj]
    return obj


def anfrage(methode: str, pfad: str, daten=None, timeout: int = 60):
    token = os.environ.get("COOLIFY_TOKEN")
    if not token:
        sys.exit("COOLIFY_TOKEN fehlt (siehe docs/betrieb.md). Der Wert wird nie ausgegeben.")
    url = BASIS + (pfad if pfad.startswith("/") else "/" + pfad)
    body = json.dumps(daten).encode() if daten is not None else None
    req = urllib.request.Request(url, data=body, method=methode, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/json",
        **({"Content-Type": "application/json"} if body else {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            roh = r.read()
    except urllib.error.HTTPError as e:
        text = e.read().decode(errors="replace")[:500]
        sys.exit(f"{methode} {pfad} → HTTP {e.code}: {text}")
    return json.loads(roh) if roh else None


def zufall() -> str:
    return secrets.token_urlsafe(36)


def wert_aufloesen(spez: str) -> str:
    if spez == "@zufall":
        return zufall()
    if spez.startswith("@datei:"):
        return Path(spez[7:]).read_text().strip()
    return spez


def cmd_status(args):
    uuids = args.uuid or list(APPS.values())
    namen = {v: k for k, v in APPS.items()}
    for u in uuids:
        a = anfrage("GET", f"/applications/{u}")
        print(f"{namen.get(u, a.get('name', u))}: {a.get('status')}  ·  {a.get('fqdn')}  ·  Branch {a.get('git_branch')}"
              f"  ·  Dockerfile {a.get('dockerfile_location') or '/Dockerfile'}  ·  Port {a.get('ports_exposes')}")


def warten(dep: str, frist: int = 1800) -> str:
    ende, status, d = time.time() + frist, "?", {}
    while time.time() < ende:
        d = anfrage("GET", f"/deployments/{dep}") or {}
        status = d.get("status", "?")
        if status in ENDE:
            break
        time.sleep(15)
    try:
        zeilen = [z for z in json.loads(d.get("logs") or "[]") if not z.get("hidden")]
        for z in zeilen[-25:]:
            print("  " + str(z.get("output", ""))[:300])
    except (TypeError, ValueError):
        pass
    print(f"Deploy {dep}: {status}")
    return status


def cmd_deploy(args):
    r = anfrage("GET", f"/deploy?uuid={urllib.parse.quote(args.uuid)}&force={'true' if args.force else 'false'}")
    deps = (r or {}).get("deployments") or []
    if not deps:
        sys.exit(f"Kein Deploy gestartet: {schwaerzen(r)}")
    status = warten(deps[0]["deployment_uuid"])
    sys.exit(0 if status == "finished" else 1)


def cmd_warten(args):
    sys.exit(0 if warten(args.deployment) == "finished" else 1)


def cmd_envs(args):
    for e in anfrage("GET", f"/applications/{args.uuid}/envs") or []:
        if e.get("is_preview"):
            continue
        art = "buildtime" if e.get("is_buildtime") else "runtime"
        print(f"{e.get('key')}  ({art})")


def cmd_env_setzen(args):
    daten = []
    for paar in args.paare:
        if "=" not in paar:
            sys.exit(f"Erwartet NAME=wert, bekommen: {paar.split('=')[0]}")
        name, spez = paar.split("=", 1)
        daten.append({"key": name, "value": wert_aufloesen(spez), "is_preview": False, "is_buildtime": False,
                      "is_runtime": True, "is_literal": False})
    anfrage("PATCH", f"/applications/{args.uuid}/envs/bulk", {"data": daten})
    print("gesetzt: " + ", ".join(d["key"] for d in daten) + "  (Werte nicht angezeigt; Redeploy nötig)")


def cmd_storages(args):
    r = anfrage("GET", f"/applications/{args.uuid}/storages")
    liste = r if isinstance(r, list) else (r or {}).get("persistent_storages", [])
    for s in liste:
        print(f"{s.get('name')}: {s.get('mount_path')}")


def cmd_api(args):
    daten = json.loads(Path(args.json).read_text()) if args.json else None
    print(json.dumps(schwaerzen(anfrage(args.methode.upper(), args.pfad, daten)), indent=2, ensure_ascii=False)[:20000])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.add_argument("uuid", nargs="*"); s.set_defaults(f=cmd_status)
    s = sub.add_parser("deploy"); s.add_argument("uuid"); s.add_argument("--force", action="store_true"); s.set_defaults(f=cmd_deploy)
    s = sub.add_parser("warten"); s.add_argument("deployment"); s.set_defaults(f=cmd_warten)
    s = sub.add_parser("envs"); s.add_argument("uuid"); s.set_defaults(f=cmd_envs)
    s = sub.add_parser("env-setzen"); s.add_argument("uuid"); s.add_argument("paare", nargs="+"); s.set_defaults(f=cmd_env_setzen)
    s = sub.add_parser("storages"); s.add_argument("uuid"); s.set_defaults(f=cmd_storages)
    s = sub.add_parser("api"); s.add_argument("methode"); s.add_argument("pfad"); s.add_argument("--json"); s.set_defaults(f=cmd_api)
    args = p.parse_args(argv)
    args.f(args)


if __name__ == "__main__":
    main()
