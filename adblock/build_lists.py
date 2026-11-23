#!/usr/bin/env python3
"""Build ready-to-use blocklists from adblock/sources/.

Outputs in adblock/dist/:
  adguard-standard.txt / adguard-aggressive.txt  AdGuard Home (with allow rules)
  domains-standard.txt / domains-aggressive.txt  Pi-hole, NextDNS, routers
  hosts-standard.txt   / hosts-aggressive.txt    hosts-file format

Run:  python3 adblock/build_lists.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC, DIST = ROOT / "sources", ROOT / "dist"


def read(name):
    out = []
    for line in (SRC / name).read_text().splitlines():
        line = line.split("#", 1)[0].strip().lower()
        if line and line not in out:
            out.append(line)
    return out


def build(tier, block, allow):
    # Drop any blocked domain that is itself on the allowlist. A blocked
    # subdomain of an allowed parent (ngfts.lge.com under lge.com) stays
    # blocked: allowing lge.com must not unblock LG's ad host.
    safe = [d for d in block if d not in allow]
    header = f"# LG TV ad blocker - {tier} tier ({len(safe)} domains)\n"
    (DIST / f"domains-{tier}.txt").write_text(header + "\n".join(safe) + "\n")
    (DIST / f"hosts-{tier}.txt").write_text(
        header + "\n".join(f"0.0.0.0 {d}" for d in safe) + "\n")
    rules = [f"||{d}^$important" for d in safe]
    # Allow rules protect app/login domains from any OTHER list you add in
    # AdGuard Home. They are not $important, so the blocks above still win
    # for the specific ad hosts listed in this file.
    rules += [f"@@||{a}^" for a in allow]
    (DIST / f"adguard-{tier}.txt").write_text(
        "! Title: LG TV ad blocker (" + tier + ")\n" + "\n".join(rules) + "\n")
    return len(safe)


def main():
    DIST.mkdir(exist_ok=True)
    allow = read("allow.txt")
    std = read("block-standard.txt")
    agg = std + [d for d in read("block-aggressive.txt") if d not in std]
    for tier, block in (("standard", std), ("aggressive", agg)):
        print(f"{tier}: {build(tier, block, allow)} domains blocked")
    print(f"allowlist: {len(allow)} domains protected")


if __name__ == "__main__":
    main()
