# Ferryman Hat Co. — deployment runbook

The site is static. GitHub Pages hosts it; every push to `main` deploys
automatically via `.github/workflows/deploy.yml`. The admin (`admin.html` +
`serve.py`) is **local-only** and is stripped from the deployed site by the
workflow — it never reaches the internet.

## Daily workflow (edit hats, publish)

```bash
python3 serve.py              # http://localhost:8080/admin.html
# add/edit hats, upload photos, Save all
git add -A && git commit -m "Update hats" && git push
```

Live on ferrymanhats.com ~1 minute later.

## One-time setup

### 1. GitHub Pages (Settings → Pages)
- Source: **GitHub Actions**
- Custom domain: `ferrymanhats.com` → Save
- After DNS resolves (step 2): tick **Enforce HTTPS**

### 2. Namecheap DNS (Domain List → ferrymanhats.com → Advanced DNS)

Delete any parking records, then add:

| Type  | Host | Value                          | TTL  |
|-------|------|--------------------------------|------|
| A     | @    | 185.199.108.153                | Auto |
| A     | @    | 185.199.109.153                | Auto |
| A     | @    | 185.199.110.153                | Auto |
| A     | @    | 185.199.111.153                | Auto |
| CNAME | www  | kulosaari-capital.github.io.   | Auto |

Propagation: usually minutes, occasionally a few hours.

### 3. Email forwarding (same Namecheap page → Mail Settings)
- Choose **Email Forwarding**
- Add: `hats` → your personal inbox
- Namecheap adds the needed MX records itself.
- Test by mailing hats@ferrymanhats.com before launch day.
- Note: this receives mail only. Replies go out from your personal
  address (fine at this scale; a proper mailbox is a later upgrade).

## Launch-day swaps
- New hat photos: upload via admin (resizes to 1600 px automatically), Save all, push.
- Social preview card: replace `assets/og-image.jpg` (1200×630 JPEG) and push.
  Facebook/LinkedIn cache aggressively — re-scrape at
  https://developers.facebook.com/tools/debug/ if the old card lingers.
- Mark the Founder card: edit in admin → tag "Commissioned · Founder №1" etc.

## Phase 2 (after launch, when needed)
- Stripe Payment Links: create a link per hat in the Stripe dashboard,
  add a `buy` field to products.json and a Buy button in script.js.
- Real mailbox (e.g. iCloud+/Google Workspace custom domain).
- Form backend (Formspree) instead of the mailto handoff.
