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
3. **YouTube without ads:**
   ```bash
   ./youtube/install-youtube-adfree.sh 192.168.1.50
   ```

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
