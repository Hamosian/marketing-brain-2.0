# Stable artifact URL

The weekly report publishes to one URL, updated in place, so the SEO team's
bookmark survives every refresh.

```text
STATUS: live
URL:    https://claude.ai/artifact/2p64QrKaoy1usxqpUdngXn
        (was /code/artifact/0eac36a4-fac6-4d2c-a5b5-b3e86bde375d; the service
        moved to a shorter scheme on 2026-09-17 and returned the new form
        from a publish that passed the old one, same artifact, same version chain)
Title:  Weekly SEO Report
        (was "Organic Search Conversion Pull"; renamed 2026-09-17 when the
        skill became /weekly-seo-report. Same URL, same version chain)
Icon:   📈
Minted: 2026-09-03 (first edition, Aug 27 to Sep 2)
Shared: with the organization, so viewers see each update immediately
```

Pass that URL as the Artifact tool's `url` parameter on every run, keep the
title stable, and omit `favicon` so the icon does not change. Publishing without
`url` mints a **new** artifact and strands the shared link.

## Before publishing to it

The artifact service refuses a publish from a session that has not read the
live version. Read it first (`action: "read"` with the URL), which saves the
full source locally, then build the new edition from that file so nothing
already published is lost. It is a large page, so the read lands as a file
rather than inline.

## Editions so far

| Published | Funnel window | Search Console window |
|---|---|---|
| 2026-09-03 | Aug 27 to Sep 2 | Aug 25 to 31 |
| 2026-09-10 | Sep 3 to 9 | Sep 1 to 7, rebuilt from `date` + `device` rows |
| 2026-09-17 | Sep 9 to 15 (shifted: Snowflake at D-2) | Sep 8 to 14; tab rebuilt to the seven-section spec in `build-and-render.md` |
