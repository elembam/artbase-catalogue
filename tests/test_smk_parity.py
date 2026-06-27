"""
test_smk_parity.py — Drift guard for Spec 17 (acceptance test 6).

Fetches KMS4185 live from api.smk.dk, runs both the Python SMKAdapter and
the JS smk-preview.js mapRecord() on the same raw JSON, then compares the
fields listed in data/mappings/smk-field-map.json:parity_test_fields.

Fails if any field disagrees between the two implementations.

Run: python3 tests/test_smk_parity.py
Exit 0 = parity OK. Exit 1 = mismatch or error.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import urllib.request
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parent.parent
FIELD_MAP   = REPO_ROOT / "data" / "mappings" / "smk-field-map.json"
PREVIEW_JS  = REPO_ROOT / "site" / "sources" / "smk" / "smk-preview.js"

sys.path.insert(0, str(REPO_ROOT / "artbase_export" / "src"))

TEST_OBJECT = "KMS4185"

# ── Helpers ────────────────────────────────────────────────────────────────────

def _get(obj: dict, dotpath: str):
    """Resolve 'a.b.c' into obj['a']['b']['c']; return None if absent."""
    parts = dotpath.split(".")
    cur   = obj
    for p in parts:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def fetch_raw(object_number: str) -> dict:
    url = f"https://api.smk.dk/api/v1/art/?object_number={object_number}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
    items = data.get("items") or []
    if not items:
        raise ValueError(f"Not found from SMK API: {object_number}")
    return items[0]


def python_mapped(raw: dict) -> dict:
    from artbase_export.adapters.smk import SMKAdapter
    adapter = SMKAdapter()
    return adapter.normalize_to_object_record(raw)


def js_mapped(raw: dict) -> dict:
    """Run smk-preview.js mapRecord() via Node.js subprocess on the same raw JSON."""
    raw_json = json.dumps(raw, ensure_ascii=False)

    # Inline Node script: loads smk-preview.js (which exports mapRecord when
    # run under Node via the `if (typeof module !== 'undefined')` guard),
    # calls mapRecord on the supplied raw, prints the result.
    node_script = textwrap.dedent(f"""\
        const path   = require('path');
        const fs     = require('fs');
        // smk-preview.js uses CommonJS module.exports when run in Node
        const widget = require({json.dumps(str(PREVIEW_JS))});
        const raw    = {raw_json};
        const result = widget.mapRecord(raw);
        process.stdout.write(JSON.stringify(result));
    """)

    result = subprocess.run(
        ["node", "--input-type=module"],
        input=textwrap.dedent(f"""\
            import {{ createRequire }} from 'module';
            import {{ fileURLToPath }} from 'url';
            import {{ dirname }} from 'path';
            import {{ readFileSync }} from 'fs';
            import {{ pathToFileURL }} from 'url';
            // smk-preview.js uses 'use strict' + module.exports guard;
            // we evaluate it in CommonJS context via Node's createRequire trick
            const require = createRequire(import.meta.url);
            const widget  = require({json.dumps(str(PREVIEW_JS))});
            const raw     = {raw_json};
            const result  = widget.mapRecord(raw);
            process.stdout.write(JSON.stringify(result));
        """).encode(),
        capture_output=True,
        timeout=30,
    )

    if result.returncode != 0:
        stderr = result.stderr.decode(errors="replace")
        # ESM approach failed — fall back to CJS subprocess
        result2 = subprocess.run(
            ["node", "-e", node_script],
            capture_output=True,
            timeout=30,
        )
        if result2.returncode != 0:
            raise RuntimeError(
                f"Node.js failed (ESM): {stderr}\n"
                f"Node.js failed (CJS): {result2.stderr.decode(errors='replace')}"
            )
        return json.loads(result2.stdout.decode())

    return json.loads(result.stdout.decode())


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    field_map = json.loads(FIELD_MAP.read_text())
    parity_fields = field_map["parity_test_fields"]

    print(f"Fetching {TEST_OBJECT} from api.smk.dk …", flush=True)
    try:
        raw = fetch_raw(TEST_OBJECT)
    except Exception as exc:
        print(f"ERROR: Could not fetch from SMK API: {exc}")
        sys.exit(1)

    print("Running Python adapter …", flush=True)
    try:
        py_out = python_mapped(raw)
    except Exception as exc:
        print(f"ERROR: Python adapter failed: {exc}")
        sys.exit(1)

    print("Running JS widget (Node.js) …", flush=True)
    try:
        js_out = js_mapped(raw)
    except Exception as exc:
        print(f"ERROR: JS mapRecord failed: {exc}")
        sys.exit(1)

    # Compare parity fields
    mismatches = []
    for field in parity_fields:
        py_val = _get(py_out, field)
        js_val = _get(js_out, field)
        match  = py_val == js_val
        status = "OK  " if match else "FAIL"
        print(f"  [{status}] {field}")
        print(f"          py: {py_val!r}")
        if not match:
            print(f"          js: {js_val!r}")
            mismatches.append(field)

    print()
    if mismatches:
        print(f"PARITY FAIL — {len(mismatches)} field(s) disagree: {mismatches}")
        sys.exit(1)
    else:
        print(f"Parity OK — {len(parity_fields)} field(s) match between Python adapter and JS widget.")
        sys.exit(0)


if __name__ == "__main__":
    main()
