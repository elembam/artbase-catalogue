# Custom Domain Setup — arsaccordia.com

**GitHub Pages repo:** https://github.com/elembam/artbase-catalogue  
**Current GitHub Pages URL:** https://elembam.github.io/artbase-catalogue/  
**Target URL:** https://arsaccordia.com  

The `CNAME` file is already committed to the repo. Once you configure your DNS records below, the domain will go live automatically (propagation takes 10 minutes – 48 hours).

---

## Step 1 — DNS records at your registrar

Log into the control panel of wherever you bought `arsaccordia.com` and add these records:

### A records (for the apex domain `arsaccordia.com`)

Add all four — GitHub requires all four for redundancy:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | `@` | `185.199.108.153` | 3600 |
| A | `@` | `185.199.109.153` | 3600 |
| A | `@` | `185.199.110.153` | 3600 |
| A | `@` | `185.199.111.153` | 3600 |

### CNAME record (for `www.arsaccordia.com`)

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | `www` | `elembam.github.io` | 3600 |

> **Note:** `Name` is sometimes labelled "Host" or "Subdomain" at your registrar.  
> `@` means the apex/root domain (no prefix).

---

## Step 2 — Configure GitHub Pages

Once DNS is propagating, go to:

**https://github.com/elembam/artbase-catalogue/settings/pages**

1. Under **"Custom domain"**, enter: `arsaccordia.com`
2. Click **Save**
3. Wait for the **"DNS check in progress"** to complete
4. Once DNS resolves: check **"Enforce HTTPS"** ✅

> The `CNAME` file is already in the repo — GitHub may auto-populate this field.

---

## Step 3 — Verify

After DNS propagates (check progress at https://dnschecker.org/#A/arsaccordia.com):

```bash
# Check DNS is resolving to GitHub
dig arsaccordia.com +short
# Should return: 185.199.108.153 (and the other three IPs)

dig www.arsaccordia.com +short
# Should return: elembam.github.io
```

Then visit:
- https://arsaccordia.com — should load the catalogue index
- https://www.arsaccordia.com — should redirect to apex

---

## Step 4 — Update internal references

Once live, run this to update any internal URLs in the generated passports:

```bash
cd /Users/elemba/VSCode/Ars Accordia/Ars Accordia
python3 scripts/index_generator.py   # regenerate index with correct domain
python3 scripts/passport_generator.py  # regenerate passports if needed
```

Then push the updated files:

```bash
cd passports
git add -A
git commit -m "Update URLs to arsaccordia.com"
git push
```

---

## Troubleshooting

**Still showing elembam.github.io after 48 hours:**
- Confirm all 4 A records are saved at registrar
- Confirm `CNAME` file exists in repo root: https://github.com/elembam/artbase-catalogue/blob/main/CNAME
- Check GitHub Pages settings and re-enter the custom domain

**"Domain not verified" error in GitHub:**
- Add a DNS TXT record for domain verification:
  - Go to https://github.com/settings/pages and follow "Verify a domain"
  - Adds trust and prevents domain hijacking

**HTTPS certificate not issuing:**
- Wait 24 hours — Let's Encrypt certificate is auto-provisioned by GitHub
- Ensure "Enforce HTTPS" is checked in Pages settings
- Ensure no CAA DNS record is blocking Let's Encrypt

**www not redirecting:**
- Confirm the CNAME record for `www` points to `elembam.github.io` (not `arsaccordia.com`)

---

## What's already done ✅

- [x] `CNAME` file committed to `elembam/artbase-catalogue` repo
- [x] Contains: `arsaccordia.com`

## What you need to do ⏳

- [ ] Add 4 × A records at your registrar
- [ ] Add 1 × CNAME record (www) at your registrar
- [ ] Set custom domain in GitHub Pages settings
- [ ] Enable "Enforce HTTPS"
- [ ] Verify site loads at https://arsaccordia.com
