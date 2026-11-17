# Hilfen für $WP_DIR/.env.local (von setup.sh eingebunden; erwartet ENV_LOCAL).
# Werte werden für die Shell gequotet (printf %q), damit `set -a; . .env.local; set +a` sie unverändert lädt –
# auch mit Leerzeichen wie in WP_TEST_WP_CLI.

# setenv NAME WERT – ersetzt eine vorhandene Zeile
setenv() {
  local tmp
  tmp="$(mktemp)"
  grep -v "^$1=" "$ENV_LOCAL" > "$tmp" || true
  printf '%s=%q\n' "$1" "$2" >> "$tmp"
  cat "$tmp" > "$ENV_LOCAL"
  rm -f "$tmp"
}

# getenv NAME – Wert so, wie die Shell ihn beim Laden sieht
getenv() {
  ( set -a; . "$ENV_LOCAL" >/dev/null 2>&1; set +a; printf '%s' "${!1:-}" )
}
