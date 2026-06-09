# Nurtura — marketing site

One-page marketing site for [Nurtura Baby Insights](https://apps.apple.com/app/id6770261130) plus the two legal pages Apple requires (`privacy.html` and `support.html`).

## Stack

Plain HTML + CSS. No framework, no build step, no JavaScript dependencies. The whole site is three HTML files, two stylesheets, and the App Store screenshots.

## Structure

```
.
├── index.html         Marketing page (hero, features, pregnancy, premium, privacy strip)
├── privacy.html       Privacy policy — linked from Apple's App Store listing
├── support.html       Support FAQ — linked from Apple's App Store listing
├── styles.css         Brand tokens + marketing-page layout
├── legal.css          Long-form typography for privacy/support pages
├── CNAME              GitHub Pages custom domain config (nurtura.app)
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

## Brand

Sage palette + Inter type. All colour tokens are CSS custom properties at the top of `styles.css`; change them once and the whole site shifts.
