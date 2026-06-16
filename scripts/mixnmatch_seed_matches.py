#!/usr/bin/env python3
"""
Seed confirmed ART-* → Q-number matches into Mix'n'match catalog 8050
using the public API. Run this once after catalog import.

Requires: pip install requests
You must be logged in via OAuth or use a bot password.
See: https://www.mediawiki.org/wiki/Manual:Bot_passwords
"""

import json
import time
import glob
from pathlib import Path

try:
    import requests
except ImportError:
    print("pip install requests")
    raise

CATALOG_ID = "8050"
API_URL    = "https://mix-n-match.toolforge.org/api.php"

REPO_ROOT   = Path(__file__).resolve().parent.parent
ARTISTS_DIR = REPO_ROOT / "artbase_export" / "data" / "artists"

# ── Collect confirmed pairs ────────────────────────────────────────────────
pairs = []
for path in sorted(ARTISTS_DIR.glob("*.json")):
    artist = json.loads(path.read_text())
    aid    = artist.get("artbase_id", "")
    al     = (artist.get("authority_links") or {}).get("wikidata") or {}
    if al.get("status") == "confirmed" and al.get("id"):
        pairs.append((aid, al["id"]))

print(f"Confirmed pairs to seed: {len(pairs)}")

# ── Submit via API ─────────────────────────────────────────────────────────
# Mix'n'match API: action=add_match, catalog=N, ext_id=..., wikidata=Q...
# Rate-limit to 5 requests/sec to be polite.

session = requests.Session()
session.headers.update({"User-Agent": "ArsAccordia-seed/1.0 (arsaccordia.com)"})

ok = 0
fail = 0

for ext_id, qid in pairs:
    resp = session.get(API_URL, params={
        "action":   "add_match",
        "catalog":  CATALOG_ID,
        "ext_id":   ext_id,
        "wikidata": qid,
        "user":     "ArsAccordia",
    }, timeout=15)

    try:
        data = resp.json()
        if data.get("status") == "OK":
            ok += 1
            print(f"  ✓ {ext_id} → {qid}")
        else:
            fail += 1
            print(f"  ✗ {ext_id} → {qid}  ({data})")
    except Exception as e:
        fail += 1
        print(f"  ✗ {ext_id}: {e}")

    time.sleep(0.2)  # 5 req/sec max

print(f"\nDone. {ok} seeded, {fail} failed.")
print("Check catalog: https://mix-n-match.toolforge.org/#/catalog/8050")
