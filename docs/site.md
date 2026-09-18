# Rea-Cli landing page (GitHub Pages `/docs` prototype)

Static HTML/CSS/JS with no build step. This is the in-repo landing-page
prototype; it is not the `reaperdoc-site.zip` produced by
`tools/build_release.py`.

## Structure

- `index.html` — Simplified Chinese (default)
- `en/index.html` — English
- `styles.css` / `main.js` — shared
- `assets/reacli-icon.png` — project icon

## Local preview

```bash
python3 -m http.server 8080 --directory docs
# http://localhost:8080 (Chinese) or http://localhost:8080/en/ (English)
```

## GitHub Pages

In repository Settings → Pages, select the `main` branch `/docs` directory.
`docs/index.html` is the default Chinese entry; `docs/en/` is English.

Product claims on the page follow `README.md`, `docs/api.md` and
`docs/environment.md`. Project-owned page content is [MIT licensed](../LICENSE);
upstream material keeps its own terms. See
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).
