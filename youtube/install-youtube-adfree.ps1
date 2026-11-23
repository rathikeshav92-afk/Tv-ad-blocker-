# Install "YouTube AdFree" (open-source webosbrew/youtube-webos) on an LG TV
# from a Windows PC, and print the Developer Mode token used for automatic
# renewal (see .github/workflows/keep-devmode-on.yml).
#
# Needs Node.js (https://nodejs.org). Run in PowerShell, on the SAME Wi-Fi
# as the TV, with Developer Mode ON and Key Server ON:
#
#   powershell -ExecutionPolicy Bypass -File youtube\install-youtube-adfree.ps1 -TvIp 192.168.1.50
param([Parameter(Mandatory = $true)][string]$TvIp)
$ErrorActionPreference = "Stop"
$Device = "lgtv"

function Run($exe, [string[]]$argList) {
    & $exe @argList
    if ($LASTEXITCODE -ne 0) { throw "$exe failed (exit code $LASTEXITCODE)" }
}

if (-not (Get-Command ares-install -ErrorAction SilentlyContinue)) {
    Write-Host ">> Installing the LG webOS CLI..."
    Run "npm" @("install", "-g", "@webos-tools/cli")
}

Write-Host ">> Registering the TV ($TvIp) as '$Device'..."
cmd /c "ares-setup-device --remove $Device >nul 2>&1"
Run "ares-setup-device" @("--add", $Device, "--info", "{'host':'$TvIp','port':'9922','username':'prisoner'}")

Write-Host ">> Fetching the TV's developer key."
Write-Host "   When asked, type the PASSPHRASE shown in the Developer Mode app."
Run "ares-novacom" @("--device", $Device, "--getkey")

Write-Host ">> Finding the latest YouTube AdFree release..."
$release = Invoke-RestMethod "https://api.github.com/repos/webosbrew/youtube-webos/releases/latest"
$asset = $release.assets | Where-Object { $_.name -like "*.ipk" } | Select-Object -First 1
if (-not $asset) { throw "No .ipk found in the latest release." }
$ipk = Join-Path $env:TEMP $asset.name
Invoke-WebRequest $asset.browser_download_url -OutFile $ipk

Write-Host ">> Installing $($asset.name) on the TV..."
Run "ares-install" @("--device", $Device, $ipk)
Remove-Item $ipk

Write-Host ">> Reading the Developer Mode token for automatic renewal..."
$token = (& ares-novacom --device $Device --run "cat /var/luna/preferences/devmode_enabled" | Out-String).Trim()

Write-Host ""
Write-Host "Done. 'YouTube AdFree' is now in your TV's app list."
Write-Host "Sign in with your Google account (enter the TV's code at yt.be/activate)."
Write-Host ""
if ($token) {
    Write-Host "Developer Mode token (keep it private, like a password):"
    Write-Host "  $token"
    Write-Host "Add it to GitHub so Developer Mode renews itself every day:"
    Write-Host "  repo > Settings > Secrets and variables > Actions > New repository secret"
    Write-Host "  Name: LG_DEVMODE_TOKEN   Value: the token above"
} else {
    Write-Host "Could not read the Developer Mode token. Extend it by hand in the"
    Write-Host "Developer Mode app, or ask for help setting up automatic renewal."
}
Write-Host ""
Write-Host "Security: you can now turn Key Server OFF in the Developer Mode app."
