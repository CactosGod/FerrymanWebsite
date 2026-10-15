# ferrymanhats.com

Ferryman Hat Co. — bespoke hats made in Kulosaari, Helsinki.
Static site + local admin. See **DEPLOY.md** for hosting, DNS and the
publishing workflow.

- `index.html`, `styles.css`, `script.js` — the site; gallery renders from `products.json`
- `admin.html` + `serve.py` — local admin (`python3 serve.py`, then /admin.html).
  Local only, no auth; the deploy workflow strips both from the public site.
- `assets/` — images, logos, og-image, favicons; admin photo uploads land in `assets/uploads/`

A Kulosaari Capital Oy brand.
