# Leap Journey marketing and legal site

Marketing site for [Leap Journey](https://apps.apple.com/app/id6770261130), with current privacy, terms, and support pages.

## Stack

Plain HTML + CSS. No framework, runtime JavaScript dependency, analytics, cookies, or remote font request.

## Structure

```
.
├── index.html         Marketing page (hero, features, pregnancy, premium, privacy strip)
├── privacy.html       Privacy policy linked from the app and App Store listing
├── terms.html         Product and one-time-purchase terms
├── support.html       Accurate support and deletion instructions
├── styles.css         Brand tokens + marketing-page layout
├── legal.css          Long-form typography for privacy/support pages
├── tools/             Regenerates localized redirects to current English pages
└── assets/
    ├── icon.png       App icon (used in nav + favicon)
    └── screenshots/   App Store iPhone screenshots (1242 × 2688)
```

## Local preview

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Any static file server works (`npx serve`, `live-server`, etc.). There is no build step.

## Deploy (GitHub Pages)

1. Push to `main`.
2. Repository → **Settings → Pages** → set source to "Deploy from a branch" + `main` + `/ (root)`.
3. The `CNAME` file points `nurtura.app` at this Pages site — once GitHub Pages is enabled, configure the apex A records / CNAME at your registrar:
   - A records: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - For `www`: CNAME to `<username>.github.io`
4. Enforce HTTPS in Pages settings once the DNS resolves.

## Updating screenshots

Replace files in `assets/screenshots/` with the latest from the app repo (`store/apple/screenshot/en-US/APP_IPHONE_65/`). Filenames are referenced from `index.html` — if you rename, update there too.

## Localized URLs

Existing locale URLs redirect to the current English pages. Do not restore the removed generated translations unless every translated legal and product claim is reviewed against the shipping release.
