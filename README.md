# LG TV Ad Blocker

Block ads on an LG webOS TV **without breaking any app or signing out of
your existing accounts**.

| Folder | What it does | Runs on |
|---|---|---|
| [`docs/`](docs/turn-off-lg-ads-in-settings.md) | Turn off LG's own ads and tracking in Settings | The TV remote |
| [`adblock/`](adblock/README.md) | Blocks ad and tracking servers for every app, using AdGuard Home, Pi-hole, NextDNS or your router | A device on your Wi-Fi |
| [`youtube/`](youtube/install-youtube-adfree.sh) | Installs YouTube AdFree, an ad-free YouTube app you sign into with your existing Google account | A computer, once |

## Quick start

1. **Settings:** follow [docs/turn-off-lg-ads-in-settings.md](docs/turn-off-lg-ads-in-settings.md).
2. **Ad blocking:** follow [adblock/README.md](adblock/README.md), then set the TV's DNS to the blocker.
3. **YouTube without ads.** Windows (PowerShell):
   ```powershell
   powershell -ExecutionPolicy Bypass -File youtube\install-youtube-adfree.ps1 -TvIp 192.168.1.50
   ```
   Mac/Linux: `./youtube/install-youtube-adfree.sh 192.168.1.50`
4. **Keep it running by itself.** Add the token the installer prints as
   the GitHub secret `LG_DEVMODE_TOKEN` (repo → Settings → Secrets and
   variables → Actions). GitHub then renews Developer Mode every day, so
   YouTube AdFree is never removed.

## Works with your PC and TV switched off

| Part | Where it runs |
|---|---|
| Settings changes | Saved in the TV |
| Ad blocking (Option 0) | AdGuard DNS's servers |
| YouTube AdFree | Installed on the TV |
| Developer Mode renewal | GitHub's servers, daily ([workflow](.github/workflows/keep-devmode-on.yml)) |

Your PC is only needed once, to install YouTube AdFree. GitHub pauses
scheduled workflows after 60 days with no changes to the repo; it emails
you, and one click on **Enable workflow** turns it back on.

## Why these files don't run *on* the TV

LG's webOS only runs apps installed from the LG store or through
Developer Mode. Ordinary scripts can't run on it, and there is no setting
that blocks ads inside other apps. So the blocking happens on your
network (DNS), and YouTube AdFree is installed through LG's official
Developer Mode.

## Honest limits

- **Ads served from the same servers as the video can't be blocked by
  DNS.** That includes YouTube, JioHotstar, Prime Video, Netflix's ad
  plan, SonyLIV and ZEE5. Blocking those servers would stop the shows
  too. YouTube is solved by YouTube AdFree; for the others, only an
  ad-free subscription removes the ads.
