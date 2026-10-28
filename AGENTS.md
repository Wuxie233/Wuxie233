# Profile Repository Guide

## Architecture

- `README.md` is the published GitHub Profile.
- `PRODUCT.md` records the audience, content contract, and evidence rules.
- `DESIGN.md` records the visual system and responsive asset rules.
- `assets/` contains repository-owned screenshots and SVGs; mobile-specific SVGs use the `-mobile` suffix.
- `scripts/art/build.py` generates the hero and work illustrations into `assets/` and the Chinese label outlines in `scripts/art/glyphs.json`. Edit the generator, not the generated SVGs.
- `scripts/update-stats.mjs` draws the rolling-year contribution skyline for desktop and mobile from anonymous daily counts; it reads `scripts/art/pixel-font.json` and `glyphs.json` and needs no dependencies.
- `.github/workflows/update-stats.yml` runs the stats generator daily.

## Conventions

- Open with the hero line and one identity line, then works (Minecraft command systems first), then how I work with AI. No personal story; follow `PRODUCT.md` for order and voice.
- Mark forks and private-source products explicitly.
- Use real screenshots where available; illustrations must not imitate product UI.
- Never expose private repository names or content in profile statistics.
- Keep AdventureX recruiting, school, major, grade, income figures, and competition history outside this long-term Profile.
- FlyBuild has ended operation: no live link, and say so.
- CodeCarry is the independently maintained successor of the old oc-remote card; keep the upstream credit.
- FlyBuild may mention format codecs and NetEase login / server-entry adaptation. Do not write reverse-engineering claims on the Profile.

## Commands

```sh
uv run --with fonttools python scripts/art/build.py   # needs Noto Serif CJK and DejaVu Sans Mono installed
PROFILE_STATS_TOKEN=<token> node scripts/update-stats.mjs
for f in assets/*.svg; do python3 -c "import sys,xml.etree.ElementTree as E;E.parse(sys.argv[1])" "$f"; done
node --check scripts/update-stats.mjs
```
