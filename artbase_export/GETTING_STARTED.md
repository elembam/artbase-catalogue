# Getting Started

*From zero to your first export in VS Code.*

---

## What you need before starting

- **Python 3.11 or later** — check with `python3 --version` in terminal. If not installed: `brew install python` on Mac.
- **VS Code** with the **Python extension** (ms-python.python) installed.
- **Git** — check with `git --version`. Usually pre-installed on Mac.
- **An Airtable account** with the starter kit imported (see Section 2).

---

## Section 1 — Get the code onto your machine

Download the `artbase_export/` folder from wherever it was delivered, then open it in VS Code:

```
File → Open Folder → select the artbase_export folder
```

You should see this structure in the VS Code Explorer:

```
artbase_export/
├── .gitignore
├── .vscode/
│   └── launch.json          ← run configurations
├── config.yaml.example
├── pyproject.toml
├── data/
│   └── artists/             ← canonical JSON files go here
└── src/
    └── artbase_export/
        ├── cli.py
        ├── config.py
        ├── airtable/
        ├── canonical/
        ├── transform/
        └── writers/
```

---

## Section 2 — Set up Airtable

**Import the starter kit CSV files into Airtable:**

1. Go to [airtable.com](https://airtable.com) and create a new base (name it "Ars Accordia" or similar).
2. In the base, create tables by importing the CSV files from `csv_tables/` **in this order**:
   - Collections.csv
   - Artists_Makers.csv
   - Imports.csv
   - Artworks.csv
   - Authority_Links.csv
   - Object_ID_Checklist.csv
   - Photography_Media.csv
   - Provenance_Events.csv
   - Condition_Conservation.csv
   - Source_Documents.csv
   - Passport_Issues.csv
   - Export_Jobs.csv
3. Note your **base ID** — it's in the browser URL: `airtable.com/appXXXXXXXXXXXXXX/...`

**Create a Personal Access Token:**

1. Go to [airtable.com/account](https://airtable.com/account) → Developers → Personal access tokens
2. Click "Create new token"
3. Name: `artbase-export`
4. Scopes: select `data.records:read` and `schema.bases:read`
5. Access: select your Ars Accordia base
6. Copy the token — you'll only see it once

---

## Section 3 — Create your config file

In VS Code, open a terminal (**Terminal → New Terminal** or `` Ctrl+` ``).

You should be in the `artbase_export/` folder. Run:

```bash
cp config.yaml.example config.yaml
```

Open `config.yaml` (click it in the Explorer). Fill in your credentials:

```yaml
airtable:
  token: "patXXXX.XXXXXXXX"      # ← paste your Personal Access Token
  base_id: "appXXXXXXXXXXXXXX"   # ← paste your base ID

export:
  output_dir: "./data"
  auto_commit: false              # ← keep false until first run works
```

Save the file. It's in `.gitignore` — credentials will never be committed.

---

## Section 4 — Set up Python

**Tell VS Code which Python to use:**

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type `Python: Select Interpreter`
3. Choose Python 3.11 or 3.12

**Install the project and its dependencies:**

In the terminal:

```bash
pip install -e ".[dev]"
```

This installs the `artbase-export` command and all dependencies. It should take 30–60 seconds.

**Verify the install worked:**

```bash
artbase-export --help
```

You should see:

```
Usage: artbase-export [OPTIONS] COMMAND [ARGS]...

  Ars Accordia export pipeline — Airtable → canonical JSON

Commands:
  run       Export Airtable records to canonical JSON files
  status    Show a status table of all canonical records
  validate  Validate existing canonical JSON files
```

If you see an error instead, check that `pip install -e .` completed without errors and that the selected Python interpreter matches what pip used.

---

## Section 5 — First run

**Always start with a dry run.** It connects to Airtable, fetches records, transforms them, and prints what would change — without writing anything.

```bash
artbase-export run --dry-run --verbose
```

Expected output:

```
Fetched 3 artist(s) from Airtable
  (dry-run) would write ART-0001.json
  (dry-run) would write ART-NEW-001.json
  ...
(dry-run) +3 created  ~0 updated  =0 unchanged
```

If you see "No module named..." or authentication errors, see Troubleshooting below.

**When the dry run looks right, run for real:**

```bash
artbase-export run --verbose
```

Check the output in `data/artists/` — you should see JSON files, one per artist.

```bash
artbase-export status
```

This prints a table of all exported records showing their Object ID score, authority link count, and any conflicts.

---

## Section 6 — Running from VS Code with F5

The `.vscode/launch.json` file includes five pre-configured run profiles.

1. Click the **Run and Debug** icon in the left sidebar (or press `Ctrl+Shift+D`)
2. Select a profile from the dropdown at the top:
   - **Export — dry run (all)** — safe first test
   - **Export — single artist** — export just `ART-0001`
   - **Export — full run** — the real thing
   - **Status** — see the current state
   - **Validate** — check existing files
3. Press **F5** (or the green play button)

F5 runs the same code as the terminal commands but with the VS Code debugger attached. This means you can:
- Set breakpoints (click left of a line number) and pause execution
- Inspect variables in the Variables panel
- Step through the transform logic line by line

This is especially useful when a particular artist or artwork fails to transform and you want to see exactly which field is causing the problem.

---

## Section 7 — Daily workflow

Once everything is set up, the daily workflow is:

```bash
# 1. Update records in Airtable (add artists, fill in fields, etc.)

# 2. Export to canonical JSON
artbase-export run

# 3. Check what changed
artbase-export status

# 4. Review changed files in VS Code's Source Control panel
#    (the Git diff shows exactly what data changed)

# 5. When satisfied, push to Git remote
git push
```

The canonical `data/` folder is version-controlled — every export run that changes anything creates a Git commit. VS Code's built-in Source Control panel (the branch icon in the left sidebar) shows the diff of what changed between runs.

---

## Troubleshooting

**`artbase-export: command not found`**
→ The install didn't complete or you're using a different Python. Try:
```bash
python3 -m artbase_export.cli --help
```
If that works, use `python3 -m artbase_export.cli run` instead of `artbase-export run`.

**`Config file not found`**
→ Run from inside the `artbase_export/` folder, and make sure you created `config.yaml`:
```bash
cp config.yaml.example config.yaml
# then edit config.yaml
```

**`401 Unauthorized` from Airtable**
→ Your token is wrong or expired. Create a new one at airtable.com/account.

**`Could not find table 'Artists_Makers'`**
→ Your table name in Airtable doesn't match. Check the exact table name in Airtable and update `config.yaml` under `airtable.tables.artists`.

**`pydantic_core.ValidationError`**
→ An Airtable record has a field value the model doesn't expect (e.g. an empty required field). Run with `--verbose` and look for the artist or artwork ID in the error message, then check that record in Airtable.

**`Invalid git repository`**
→ The `data/` folder isn't in a Git repo yet. Fix:
```bash
git init
git add .
git commit -m "initial commit"
```
Or set `auto_commit: false` in config.yaml to skip Git entirely for now.

**Something else**
→ Run with `--verbose` for full debug output. Paste the error into a Claude conversation — the error message plus the name of the failing record is usually enough to diagnose.

---

## Project layout reference

```
artbase_export/
├── config.yaml.example     copy → config.yaml (gitignored)
├── pyproject.toml          pip install -e . reads this
├── .gitignore
├── .vscode/
│   └── launch.json         F5 run profiles for VS Code
│
├── data/                   ← the canonical store (committed to Git)
│   ├── artists/
│   │   └── ART-0001.json
│   └── artworks/
│
└── src/artbase_export/
    ├── cli.py              artbase-export run / status / validate
    ├── config.py           loads config.yaml
    ├── airtable/
    │   ├── client.py       fetches records from Airtable API
    │   └── schema.py       all field names in one place ← edit this when Airtable changes
    ├── canonical/
    │   └── models.py       Pydantic data models for the JSON output
    ├── transform/
    │   ├── artist.py       Airtable artist row → CanonicalArtist
    │   └── artwork.py      Airtable artwork row → CanonicalArtwork
    └── writers/
        ├── json_writer.py  writes JSON files to data/
        └── git_handler.py  commits changed files to Git
```

The file to edit most often is **`airtable/schema.py`** — whenever a field name changes in Airtable, update it here. The field name change propagates to the transform layer automatically because both use the same constants.
