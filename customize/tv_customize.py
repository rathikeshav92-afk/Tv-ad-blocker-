#!/usr/bin/env python3
"""Customise an LG webOS TV from a computer on the same Wi-Fi.

Commands:
  pair                    First-time pairing (accept the prompt on the TV)
  apply                   Apply everything in config.toml
  info                    Show model, webOS version and current picture settings
  apps                    List installed apps and their IDs
  inputs                  List HDMI/AV inputs
  launch <app_id>         Open an app
  screen-off / screen-on  Turn only the screen off/on (sound keeps playing)
  message "<text>"        Show a pop-up message on the TV
  home                    Build and install the Clean Home app ([home] in config.toml)

Options:
  --build-only            With "home": build the .ipk but don't install it
  --config PATH           Use another profile (default: config.toml next to this file)
  --ip ADDRESS            Override the TV IP in the config

Needs Python 3.11+ and:  pip install -r requirements.txt
On the TV: Settings > General > Devices > External Devices (or "Mobile TV On")
           > turn ON "Turn on via Wi-Fi" / LG Connect Apps.
"""
import argparse
import asyncio
import sys
import json
import shutil
import struct
import subprocess
import tempfile
import tomllib
import urllib.request
import zlib
from pathlib import Path

try:
    from bscpylgtv import WebOsClient
except ImportError:
    sys.exit("Missing library. Run:  pip install -r requirements.txt")

HERE = Path(__file__).resolve().parent
KEY_FILE = HERE / ".lgtv-pairing-key.sqlite"   # remembers the TV pairing


async def connect(ip):
    client = await WebOsClient.create(
        ip, key_file_path=str(KEY_FILE), ping_interval=None, states=[])
    await client.connect()
    return client


async def step(name, coro):
    """Run one setting; report but don't stop on failure (models differ)."""
    try:
        await coro
        print(f"  ok   {name}")
    except Exception as exc:  # noqa: BLE001 - keep going on any TV error
        print(f"  skip {name}: {exc}")


async def apply(client, cfg):
    pic = dict(cfg.get("picture", {}))
    if pic:
        print("Picture:")
        mode = pic.pop("pictureMode", None)
        if mode:
            # Mode first: other picture values are saved per mode.
            await step(f"pictureMode = {mode}", client.set_current_picture_mode(mode))
        for key, value in pic.items():
            await step(f"{key} = {value}", client.set_settings("picture", {key: value}))

    sound = cfg.get("sound", {})
    if sound:
        print("Sound:")
        if "output" in sound:
            await step(f"output = {sound['output']}",
                       client.change_sound_output(sound["output"]))
        if "volume" in sound:
            await step(f"volume = {sound['volume']}", client.set_volume(int(sound["volume"])))

    inputs = cfg.get("inputs", [])
    if inputs:
        print("Inputs:")
        for item in inputs:
            await step(f"{item['id']} -> {item['label']}",
                       client.set_device_info_luna(item["id"], item["icon"], item["label"]))

    start = cfg.get("startup", {})
    if start.get("launch_app"):
        await step(f"launch {start['launch_app']}", client.launch_app(start["launch_app"]))
    if start.get("message"):
        await step("message", client.send_message(start["message"]))


HOME_APP_ID = "com.tvcustomize.cleanhome"
DEVICE = "lgtv"   # device name registered by ../youtube/install-youtube-adfree.sh


def solid_png(path, size, hex_color):
    """Write a plain square PNG (app icon) without needing an image library."""
    rgb = bytes.fromhex(hex_color.lstrip("#")[:6])
    raw = b"".join(b"\x00" + rgb * size for _ in range(size))

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))

    path.write_bytes(b"\x89PNG\r\n\x1a\n"
                     + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def pick_apps(apps, home):
    """Installed apps only (plus always_show), minus hide, with order first."""
    keep_sys = home.get("include_system_apps", False)
    always = set(home.get("always_show", []))
    hide = set(home.get("hide", [])) | {HOME_APP_ID}
    chosen = [a for a in apps
              if a.get("id") not in hide
              and (keep_sys or a.get("id") in always
                   or (a.get("removable") and not a.get("systemApp")))]
    order = {app_id: i for i, app_id in enumerate(home.get("order", []))}
    return sorted(chosen, key=lambda a: (order.get(a.get("id"), len(order)),
                                         a.get("title", "").lower()))


def fetch_icon(app, out_dir):
    """Copy the app's icon into the package. Returns a relative path or ''."""
    url = app.get("largeIcon") or app.get("icon") or ""
    if url.startswith(("http://", "https://")):
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = resp.read()
            name = f"icons/{len(list(out_dir.glob('icons/*')))}.png"
            (out_dir / name).write_bytes(data)
            return name
        except OSError:
            return ""
    # A path on the TV itself; the app tries it and falls back to a letter.
    return f"file://{url}" if url.startswith("/") else ""


async def build_home(client, cfg, build_only):
    home = cfg.get("home", {})
    apps = pick_apps(await client.get_apps(), home)
    print(f"Clean Home will show {len(apps)} apps:")
    for a in apps:
        print(f"  {a.get('title', ''):35} {a.get('id')}")

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "cleanhome"
        shutil.copytree(HERE / "home", src)
        (src / "icons").mkdir()
        entries = [{"id": a["id"], "title": a.get("title", a["id"]),
                    "icon": fetch_icon(a, src)} for a in apps]
        theme = {k: home[k] for k in ("title", "background", "text_color", "accent",
                                       "columns", "show_clock") if k in home}
        (src / "apps.js").write_text(
            "window.HOME_CONFIG = " + json.dumps({"apps": entries, "theme": theme},
                                                 indent=1) + ";\n")
        color = home.get("accent", "#4f8cff")
        solid_png(src / "icon.png", 80, color)
        solid_png(src / "largeIcon.png", 130, color)

        if not shutil.which("ares-package"):
            sys.exit("LG webOS CLI not found. Install Node.js, then run:\n"
                     "  npm install -g @webos-tools/cli")
        subprocess.run(["ares-package", str(src), "-o", str(HERE)], check=True)
        ipk = max(HERE.glob(f"{HOME_APP_ID}_*.ipk"), key=lambda p: p.stat().st_mtime)
        print(f"Built {ipk.name}")
        if build_only:
            return
        subprocess.run(["ares-install", "--device", DEVICE, str(ipk)], check=True)
        await client.launch_app(HOME_APP_ID)
        print("Installed and opened Clean Home. Run this command again after "
              "installing or removing apps to refresh it.")


async def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["pair", "apply", "info", "apps", "inputs",
                                        "launch", "screen-off", "screen-on", "message", "home"])
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--config", default=str(HERE / "config.toml"))
    ap.add_argument("--ip")
    ap.add_argument("--build-only", action="store_true")
    args = ap.parse_args()

    cfg = tomllib.loads(Path(args.config).read_text())
    ip = args.ip or cfg.get("tv", {}).get("ip")
    if not ip:
        sys.exit("Set [tv] ip in config.toml or pass --ip")

    if args.command == "pair":
        print(f"Connecting to {ip}... press ACCEPT on the TV when asked.")
    client = await connect(ip)
    try:
        cmd = args.command
        if cmd == "pair":
            print("Paired. The key is saved, so you won't be asked again.")
        elif cmd == "apply":
            await apply(client, cfg)
            print("Done.")
        elif cmd == "info":
            sysinfo = await client.get_system_info()
            sw = await client.get_software_info()
            print(f"Model:  {sysinfo.get('modelName')}")
            print(f"webOS:  {sw.get('product_name')} {sw.get('major_ver')}.{sw.get('minor_ver')}")
            pic = await client.get_picture_settings(
                keys=["pictureMode", "backlight", "contrast", "brightness",
                      "color", "sharpness", "energySaving"])
            for k, v in pic.items():
                print(f"  {k}: {v}")
        elif cmd == "apps":
            for app in sorted(await client.get_apps(), key=lambda a: a.get("title", "")):
                print(f"{app.get('title', ''):35} {app.get('id')}")
        elif cmd == "inputs":
            for dev in await client.get_inputs():
                print(f"{dev.get('id'):12} {dev.get('label', '')}  connected={dev.get('connected')}")
        elif cmd == "launch":
            if not args.arg:
                sys.exit("Usage: launch <app_id>   (see the 'apps' command)")
            await client.launch_app(args.arg)
        elif cmd == "screen-off":
            await client.turn_screen_off()
        elif cmd == "screen-on":
            await client.turn_screen_on()
        elif cmd == "home":
            await build_home(client, cfg, args.build_only)
        elif cmd == "message":
            await client.send_message(args.arg or "Hello from tv_customize")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (OSError, asyncio.TimeoutError) as exc:
        sys.exit(f"Could not reach the TV: {exc}\n"
                 "Check the IP, that the TV is on, and that this computer is on the same Wi-Fi.")
