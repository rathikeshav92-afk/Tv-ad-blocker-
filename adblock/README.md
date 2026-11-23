# Block LG TV ads across every app

This blocks ads by filtering DNS, the "phone book" lookups the TV makes
before it contacts any server. Nothing is installed on the TV and no app
is modified, so **every app keeps working with your existing accounts**.
The allowlist (`sources/allow.txt`) guarantees the sign-in and video
servers for YouTube, Netflix, Prime Video, JioHotstar, SonyLIV, ZEE5,
Spotify and LG's own store are never blocked.

## What it blocks

| Blocked | Not blocked (DNS can't separate them from the video) |
|---|---|
| LG home-screen banners and "recommended" ads | YouTube ads (use `../youtube/` for those) |
| LG Live Plus / ACR viewing tracking | JioHotstar, Prime Video, Netflix ad tiers, SonyLIV, ZEE5 ads, which come from the same servers as the show |
| Ad and tracking networks inside apps and games | |
| Pre-roll ads in many free channel apps (aggressive tier) | |

## Pick a list

- `dist/*-standard.txt`: safe, start here.
- `dist/*-aggressive.txt`: also blocks video-ad servers used by free
  channel apps. A few free apps refuse to play without them. If one
  breaks, switch back to standard.

## Option 0: Always on, no device needed (easiest)

Uses the free public **AdGuard DNS** service, so ad blocking keeps
working when your PC is off. On the TV, set these as the DNS servers
(see "Point the TV at the blocker" below):

- Primary: `94.140.14.14`
- Secondary: `94.140.15.15`

It blocks 40 of the 52 domains in our standard list and none of the
app or login domains we protect, so apps and sign-ins keep working. It
doesn't block LG's home-screen ad server (`ngfts.lge.com`); turning off
**Home Promotion** in the TV's settings covers that. To block the full
list as well, use Option A on a Raspberry Pi that stays on.

## Option A: AdGuard Home (full list, needs an always-on device)

1. On a computer or Raspberry Pi that stays on, run
   `docker compose up -d` in this folder.
2. Open `http://<that-device-ip>:3000` and complete the setup.
3. **Filters → DNS blocklists → Add blocklist → Add a custom list.**
   Use the raw GitHub URL of `dist/adguard-standard.txt`, or paste its
   contents into **Filters → Custom filtering rules**.
4. Point the TV at it (see "Point the TV at the blocker" below).

## Option B: Pi-hole

**Adlists → Add** the raw URL of `dist/domains-standard.txt`, run
`pihole -g`, and add the domains from `sources/allow.txt` under
**Domains → Allow**.

## Option C: No extra device (NextDNS / router)

- **NextDNS** (free tier): create a profile, add the domains from
  `dist/domains-standard.txt` to the Denylist and `sources/allow.txt` to
  the Allowlist, then use its DNS IP addresses on the TV.
- **Router**: many routers accept a hosts file or domain list. Use
  `dist/hosts-standard.txt` or `dist/domains-standard.txt`.

## Point the TV at the blocker

On the TV: **Settings → General → Network → Wi-Fi (or Wired) →
Advanced Settings → Edit**. Untick "Set Automatically" for DNS and enter
the blocker's IP address (Pi-hole/AdGuard device, or NextDNS's IP). Save,
then restart the TV (unplug it for 30 seconds).

## Editing the lists

Edit files in `sources/`, then rebuild `dist/` with
`python3 adblock/build_lists.py`. If an app stops working, add its
domain to `sources/allow.txt`. AdGuard Home's Query Log shows exactly
which lookup was blocked.
