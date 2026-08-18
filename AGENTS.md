# Profile Repository Guide

## Architecture

- `README.md` is the published GitHub Profile.
- `PRODUCT.md` records the audience, content contract, and evidence rules.
- `DESIGN.md` records the visual system and responsive asset rules.
- `assets/` contains repository-owned screenshots and SVGs; mobile-specific SVGs use the `-mobile` suffix.
- `scripts/update-stats.mjs` generates anonymous rolling-year GitHub totals for desktop and mobile.
- `.github/workflows/update-stats.yml` runs the generator daily.

## Conventions

- Lead with products, then engineering work and capability evidence.
- Mark forks and private-source products explicitly.
- Use real screenshots where available. Feature diagrams must say they are not screenshots.
- Never expose private repository names or content in profile statistics.
- Keep AdventureX recruiting, school, and competition history outside this long-term Profile.
- CodeCarry is the independently maintained successor of the old oc-remote card; keep the upstream credit.
- FlyBuild may mention format codecs and NetEase login / server-entry adaptation. Do not write reverse-engineering claims on the Profile.

## Commands

```sh
PROFILE_STATS_TOKEN=<token> node scripts/update-stats.mjs
for f in assets/*.svg; do xmllint --noout "$f"; done
node --check scripts/update-stats.mjs
```
