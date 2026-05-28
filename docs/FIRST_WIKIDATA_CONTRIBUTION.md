# Making Your First Wikidata Contribution

**Quick start guide for contributing VIAF IDs to Wikidata using ArtBase data**

## Prerequisites

1. **Wikidata account created** at https://www.wikidata.org/
   - Username: ArtBaseLV (or similar)
   - User page created describing the ArtBase project
   
2. **QuickStatements access**
   - Go to https://quickstatements.toolforge.org/
   - Log in with your Wikidata account
   - Grant OAuth permission

## Step 1: Generate your first batch

Generate a single VIAF contribution for testing:

```bash
cd /Users/elemba/VSCode/ArtBank/ArtBase

# Dry-run first to see what would be generated
python3 scripts/wikidata_contribute.py \
  --artist ART-ABOLS-1922 \
  --property P214 \
  --max 1 \
  --dry-run

# If it looks good, generate the real batch
python3 scripts/wikidata_contribute.py \
  --artist ART-ABOLS-1922 \
  --property P214 \
  --max 1
```

This creates two files in `artbase_export/data/contributions/`:
- `queue_YYYYMMDD_HHMMSS.qs` — the QuickStatements batch
- `queue_YYYYMMDD_HHMMSS.review.md` — the review document

## Step 2: Review the files

**Open the .qs file:**

```bash
# It should look like this (one line, tab-separated):
Q3744638	P214	"45473840"	S854	"https://viaf.org/viaf/45473840/"	S813	+2026-05-28T00:00:00Z/11	S248	Q54919
```

**Check:**
- ✅ Tabs between fields (not spaces)
- ✅ VIAF ID in straight double quotes: `"45473840"`
- ✅ QID is bare (no quotes): `Q3744638`
- ✅ References present: S854 (URL), S813 (retrieved date), S248 (VIAF QID)

**Open the .review.md file:**

Read it carefully. It explains:
- What you're adding
- The source
- The risk level
- The submission checklist

## Step 3: Manual verification

Before submitting, manually verify the data:

1. **Check the Wikidata item:**
   - Go to https://www.wikidata.org/wiki/Q3744638
   - Confirm this is the correct artist (Ojārs Ābols)
   - Check if P214 (VIAF ID) already exists
   - **If it exists, STOP — choose a different artist**

2. **Check the VIAF page:**
   - Go to https://viaf.org/viaf/45473840/
   - Confirm the artist name matches
   - Confirm the dates match (if shown)

## Step 4: Submit via QuickStatements

1. Go to https://quickstatements.toolforge.org/
2. Click "Log in" and authorize with ArtBaseLV account
3. Click "New batch"
4. Select "Import V1 commands" tab
5. Open your `.qs` file in a text editor
6. **Copy the entire contents** (including the header comments)
7. **Paste** into the QuickStatements textarea
8. Click "Import"

QuickStatements will show you a preview of the batch.

## Step 5: Final checks before running

In the QuickStatements interface:

- ✅ Batch shows "Status: prepared" (not running yet)
- ✅ Statement count = 1
- ✅ Read the human-readable version carefully
- ✅ Artist name looks correct
- ✅ VIAF ID looks correct
- ✅ References are present

**If everything looks perfect:**

- Click "Run" or "Start"
- **Watch it complete** (takes ~5 seconds for 1 statement)
- Green row = success!

## Step 6: Verify on Wikidata

1. Go back to the Wikidata item (e.g., https://www.wikidata.org/wiki/Q3744638)
2. Refresh the page
3. Scroll to "Identifiers" section
4. Confirm VIAF ID now appears
5. Click "2 references" to see your S854/S813/S248 citations

## Step 7: Update your review document

Edit `queue_YYYYMMDD_HHMMSS.review.md` and add at the bottom:

```markdown
## ✅ Submitted

- **Batch ID:** [from QuickStatements URL]
- **Submitted at:** 2026-05-28T10:00:00Z
- **Success count:** 1
- **Failure count:** 0
- **Verified by:** [your name]
- **Wikidata diff:** https://www.wikidata.org/w/index.php?title=Q3744638&action=history
```

Commit this to git:

```bash
cd artbase_export
git add data/contributions/
git commit -m "First Wikidata contribution: VIAF ID for Ojārs Ābols

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
git push
```

## What to do next

**After your first successful contribution:**

1. **Wait 24 hours**
2. Check https://www.wikidata.org/wiki/User_talk:ArtBaseLV for any messages
3. Check if the edit was reverted (go back to the item page)
4. **If clean:** scale up to --max 5
5. Repeat the process

**Gradual scaling:**
- First batch: 1 statement
- Second batch: 5 statements (if first was clean)
- Third batch: 10 statements
- Fourth batch: 25 statements
- Never jump straight to 100+

## Troubleshooting

**"Property P214 already has a value"**
- The item already has a VIAF ID
- Choose a different artist
- Our script should catch this, but during testing it might not

**"Permission denied"**
- You're not logged in
- Log in to QuickStatements again

**"The given value is invalid"**
- Check the .qs file format
- Ensure tabs, not spaces
- Ensure proper quoting

**No statements generated**
- The script found no eligible contributions
- All artists already have VIAF IDs on Wikidata
- Try a different property or check different artists

## Safety reminders

⚠️ **NEVER:**
- Auto-submit batches via API
- Skip the manual review step
- Add data you haven't personally verified
- Overwrite existing Wikidata claims
- Submit batches larger than you can monitor

✅ **ALWAYS:**
- Read the review document
- Manually check source URLs
- Watch the batch run to completion
- Verify results on Wikidata
- Document everything in git

---

**See also:**
- `docs/quickstatements_runbook.md` — Full operational procedures
- `scripts/wikidata_contribute.py` — The contribution generator script
