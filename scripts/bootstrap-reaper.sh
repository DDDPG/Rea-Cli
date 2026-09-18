#!/usr/bin/env bash
# Standalone Linux preparation. REAPER is supplied by the user, not redistributed.
set -euo pipefail

REACLI_PREFIX="${REACLI_PREFIX:-$HOME/.local/opt/reacli}"
REACLI_PYTHON="${REACLI_PYTHON:-python3}"
REACLI_RESOURCE="${RAC_REAPER_RESOURCE:-${XDG_CACHE_HOME:-$HOME/.cache}/reacli/reaper}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

die() { printf '%s\n' "$*" >&2; exit 1; }
usage() {
  cat <<'HELP'
Usage: bash scripts/bootstrap-reaper.sh deps|install|env|verify|all
  deps     Install GTK3, ALSA, Xvfb, xauth and Lua (root/sudo required).
  install  Install the extracted official archive specified by REAPER_SRC.
  env      Initialize a dedicated Linux dummy-audio resource using reacli.
  verify   Execute generated Lua and verify a rendered 440 Hz WAV.
Variables: REAPER_SRC, REACLI_PREFIX, REACLI_PYTHON, RAC_REAPER_BIN,
           RAC_REAPER_RESOURCE. MP3/LAME is optional; install separately.
HELP
}

deps() {
  local elevate=() gtk=libgtk-3-0 alsa=libasound2
  if [ "$(id -u)" != 0 ]; then
    command -v sudo >/dev/null || die 'Installing OS packages requires root or sudo'
    elevate=(sudo)
  fi
  if command -v apt-get >/dev/null; then
    "${elevate[@]}" apt-get update
    if apt-cache show libgtk-3-0t64 >/dev/null 2>&1; then gtk=libgtk-3-0t64; fi
    if apt-cache show libasound2t64 >/dev/null 2>&1; then alsa=libasound2t64; fi
    "${elevate[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      "$gtk" "$alsa" xvfb xauth lua5.4
  elif command -v dnf >/dev/null; then
    "${elevate[@]}" dnf install -y --setopt=install_weak_deps=False \
      gtk3 alsa-lib xorg-x11-server-Xvfb xorg-x11-xauth lua
  elif command -v yum >/dev/null; then
    "${elevate[@]}" yum install -y gtk3 alsa-lib xorg-x11-server-Xvfb xorg-x11-xauth lua
  else
    die 'Unsupported package manager; see docs/environment.md for manual dependencies'
  fi
  if ! command -v xvfb-run >/dev/null; then
    command -v Xvfb >/dev/null || die 'Xvfb is still missing'
    command -v xauth >/dev/null || die 'xauth is still missing'
    mkdir -p "$REACLI_PREFIX/bin"
    cp -- "$SCRIPT_DIR/xvfb-run" "$REACLI_PREFIX/bin/xvfb-run"
    chmod +x "$REACLI_PREFIX/bin/xvfb-run"
    printf 'Add this directory to PATH: %s/bin\n' "$REACLI_PREFIX"
  fi
}

install_reaper() {
  [ -n "${REAPER_SRC:-}" ] || die 'Set REAPER_SRC to the extracted official Linux archive'
  [ -f "$REAPER_SRC/install-reaper.sh" ] || die 'Official install-reaper.sh missing under REAPER_SRC'
  [ -x "$REAPER_SRC/REAPER/reaper" ] || die 'REAPER/reaper missing or not executable'
  mkdir -p "$REACLI_PREFIX"
  sh "$REAPER_SRC/install-reaper.sh" --install "$REACLI_PREFIX" --quiet
  [ -x "$REACLI_PREFIX/REAPER/reaper" ] || die 'REAPER installation did not produce an executable'
  printf 'Set RAC_REAPER_BIN=%s/REAPER/reaper\n' "$REACLI_PREFIX"
}

init_env() {
  "$REACLI_PYTHON" -m rac init --resource "$REACLI_RESOURCE"
}

verify() {
  local binary="${RAC_REAPER_BIN:-$REACLI_PREFIX/REAPER/reaper}"
  PATH="$REACLI_PREFIX/bin:$PATH" "$REACLI_PYTHON" -m rac doctor \
    --reaper-bin "$binary" --resource "$REACLI_RESOURCE" --render --json
}

case "${1:---help}" in
  -h|--help|help) usage; exit 0 ;;
esac
[ "$(uname -s)" = Linux ] || die 'This bootstrap script supports Linux only'
case "$1" in
  deps) deps ;;
  install) install_reaper ;;
  env) init_env ;;
  verify) verify ;;
  all) deps; install_reaper; init_env; verify ;;
  *) usage; exit 2 ;;
esac
