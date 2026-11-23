# LG TV Ad Blocker & Customiser

Block ads on an LG webOS TV and set it up the way you like, **without
breaking any app or signing out of your existing accounts**.

| Folder | What it does | Runs on |
|---|---|---|
| [`docs/`](docs/turn-off-lg-ads-in-settings.md) | Turn off LG's own ads and tracking in Settings | The TV remote |
| [`adblock/`](adblock/README.md) | Blocks ad and tracking servers for every app, using AdGuard Home, Pi-hole, NextDNS or your router | A device on your Wi-Fi |
| [`youtube/`](youtube/install-youtube-adfree.sh) | Installs YouTube AdFree, an ad-free YouTube app you sign into with your existing Google account | A computer, once |
| [`customize/`](customize/tv_customize.py) | Applies your picture, sound, input names and start-up app from one profile file | A computer on your Wi-Fi |
| [`customize/home/`](customize/home/) | **Clean Home**: an app showing only your installed apps on a solid background, no ads or rows | Installed on the TV |

## Quick start

1. **Settings:** follow [docs/turn-off-lg-ads-in-settings.md](docs/turn-off-lg-ads-in-settings.md).
2. **Ad blocking:** follow [adblock/README.md](adblock/README.md), then set the TV's DNS to the blocker.
3. **YouTube without ads:**
   ```bash
   ./youtube/install-youtube-adfree.sh 192.168.1.50
   ```
4. **Customise:** edit `customize/config.toml`, then:
   ```bash
   cd customize && pip install -r requirements.txt
   python3 tv_customize.py pair     # accept the prompt on the TV once
   python3 tv_customize.py apply
   python3 tv_customize.py home     # build + install Clean Home (needs Developer Mode)
   ```

## Clean Home

`python3 tv_customize.py home` reads the app list from your TV, keeps
only the apps you installed (plus anything in `always_show`, such as
HDMI 1 and Settings) and installs a home app with your colours from the
`[home]` section of `config.toml`. Use the arrows and OK to open an app;
it also works with the Magic Remote pointer. Run the command again after
you install or remove apps.

LG doesn't allow any app to replace the built-in home screen, so the
**Home button still opens LG's launcher**. Pin Clean Home to the first
spot in LG's app bar (press and hold it, then move it) so it's one click
away, and turn off LG's promotions with the settings guide.

## Why these files don't run *on* the TV

LG's webOS only runs apps installed from the LG store or through
Developer Mode. Ordinary scripts can't run on it, and there is no setting
that blocks ads inside other apps. So the blocking happens on your
network (DNS), and the settings are changed remotely through LG's own
control interface, the same one the LG ThinQ phone app uses.

## Honest limits

- **Ads served from the same servers as the video can't be blocked by
  DNS.** That includes YouTube, JioHotstar, Prime Video, Netflix's ad
  plan, SonyLIV and ZEE5. Blocking those servers would stop the shows
  too. YouTube is solved by YouTube AdFree; for the others, only an
  ad-free subscription removes the ads.
- Some picture/sound settings in `config.toml` aren't supported on every
  model. The script reports `skip` for those and carries on.
