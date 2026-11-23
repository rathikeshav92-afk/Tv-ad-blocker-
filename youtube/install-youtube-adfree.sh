#!/usr/bin/env bash
# Install "YouTube AdFree" (open-source webosbrew/youtube-webos) on an LG TV.
# It is a separate YouTube app with ads, sponsor segments and the
# "Shorts" shelf removed. Your normal YouTube app is left untouched.
#
# Run this on a computer (Mac/Linux, or Windows with WSL/Git Bash) on the
# SAME Wi-Fi as the TV. Needs: Node.js (for the LG webOS CLI), curl, python3.
#
# Before running, on the TV:
#   1. Create a free account at https://webostv.developer.lge.com
#   2. Install the "Developer Mode" app from the LG Content Store,
#      sign in, turn on "Dev Mode Status" and "Key Server", reboot the TV.
#   3. Open Developer Mode again and note the IP and PASSPHRASE it shows.
#
# Usage:  ./install-youtube-adfree.sh <TV_IP>
set -euo pipefail

TV_IP="${1:?Usage: $0 <TV_IP>}"
DEVICE=lgtv
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

if ! command -v ares-install >/dev/null; then
  echo ">> Installing the LG webOS CLI (npm @webos-tools/cli)..."
  npm install -g @webos-tools/cli
fi

echo ">> Registering the TV ($TV_IP) as device '$DEVICE'..."
ares-setup-device --remove "$DEVICE" >/dev/null 2>&1 || true
ares-setup-device --add "$DEVICE" \
  --info "{'host':'$TV_IP','port':'9922','username':'prisoner'}"

echo ">> Fetching the TV's developer key (Key Server must be ON)."
echo "   When asked, type the PASSPHRASE shown in the Developer Mode app."
ares-novacom --device "$DEVICE" --getkey

echo ">> Finding the latest YouTube AdFree release..."
URL="$(curl -fsSL https://api.github.com/repos/webosbrew/youtube-webos/releases/latest |
  python3 -c 'import json,sys
assets=json.load(sys.stdin).get("assets",[])
ipk=[a["browser_download_url"] for a in assets if a["name"].endswith(".ipk")]
print(ipk[0] if ipk else "")')"
[ -n "$URL" ] || { echo "No .ipk found in the latest release." >&2; exit 1; }

echo ">> Downloading $URL"
curl -fL -o "$WORK/youtube-adfree.ipk" "$URL"

echo ">> Installing on the TV..."
ares-install --device "$DEVICE" "$WORK/youtube-adfree.ipk"

cat <<'DONE'

Done. "YouTube AdFree" is now in your TV's app list.
 - Sign in once with your existing Google account (TV shows a code,
   enter it at yt.be/activate on your phone). Your subscriptions,
   history and playlists all carry over.
 - Press the GREEN button inside the app for its settings
   (ad blocking, SponsorBlock, hide Shorts).

IMPORTANT: Developer Mode has a countdown timer (shown in the app). When it
runs out, dev apps are removed. Open Developer Mode and press "Extend" before
it runs out (or install the Homebrew Channel, which can keep it alive).
DONE
