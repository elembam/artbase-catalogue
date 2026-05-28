# QuickStatements Contribution Runbook

**Version:** 1.0  
**Last updated:** 2026-05-28  
**Owner:** ArtBase cataloguing team

This is the operational checklist for contributing ArtBase data to Wikidata via QuickStatements. Every step is mandatory. Read this document fully before each contribution session.

---

## 0. Before any session

**Account verification:**
- [ ] Verify you're logged into the correct Wikidata account (**ArtBaseLV**)
- [ ] Check your user page: https://www.wikidata.org/wiki/User:ArtBaseLV
- [ ] Confirm user page accurately describes the ArtBase project
- [ ] Check for any talk page messages: https://www.wikidata.org/wiki/User_talk:ArtBaseLV

**Transparency:**
- [ ] If first batch of the day, post a note on User talk:ArtBaseLV mentioning what you're about to do
  - Example: "Contributing VIAF IDs for 15 Latvian artists from verified sources. Batch prepared 2026-05-28."
- [ ] This aids community trust and makes it clear you're a human-operated account

**Environment:**
- [ ] Ensure stable internet connection (batches can take 5-10 minutes)
- [ ] Have enough time to monitor the entire batch run (don't start if you need to leave soon)
- [ ] Have the review.md file open in a text editor

---

## 1. Authentication

**Login to QuickStatements:**
- [ ] Go to https://quickstatements.toolforge.org/
- [ ] Click "Log in" (top right corner)
- [ ] Authorize via OAuth — this links QuickStatements to your Wikidata identity
- [ ] After redirect, confirm the username displayed top-right is **ArtBaseLV**
- [ ] **STOP** if logged in as a personal account — log out and retry

**Security check:**
- [ ] Verify the URL is exactly `quickstatements.toolforge.org` (not a phishing site)
- [ ] Check for HTTPS padlock in browser address bar

---

## 2. Loading a batch

**Import method:**
- [ ] Click "New batch" from top menu
- [ ] Select "Import V1 commands" tab
- [ ] **DO NOT** use file upload — always paste text so you see what you're submitting
- [ ] Open your `.qs` file in a text editor (VS Code, TextEdit, Notepad++)
- [ ] Select all (Cmd+A / Ctrl+A) and copy
- [ ] Paste into the large text area in QuickStatements
- [ ] Click "Import"

**What happens:**
- [ ] The batch enters "prepared" state (not running yet)
- [ ] You'll see a batch ID in the URL (e.g., #/batch/12345)
- [ ] Note this batch ID in your review.md file

---

## 3. Pre-flight checks

**Visual inspection:**
- [ ] Open the batch detail page (should appear automatically after import)
- [ ] Confirm "Status: prepared" at the top (NOT "running")
- [ ] Scroll through the human-readable statement list
- [ ] Read the **first 5 statements** carefully:
  - Is the artist correct?
  - Is the property correct (P7400, P214, etc.)?
  - Is the value correct?
  - Are references present (S854, S813, S248)?
- [ ] Read the **last 2 statements** (catches file truncation issues)

**Source verification:**
- [ ] Pick 1 random statement from the batch
- [ ] Copy the S854 reference URL
- [ ] Open it in a new browser tab
- [ ] Manually confirm the data on the source page matches the QuickStatements value
- [ ] Example: If adding VIAF 305086869, visit https://viaf.org/viaf/305086869/ and confirm the artist name matches

**Cross-check against review doc:**
- [ ] Open your `queue_YYYYMMDD_HHMMSS.review.md` file
- [ ] Verify the statement count matches
- [ ] Verify the artist names look correct
- [ ] Check for any flagged risks or warnings

---

## 4. Submission throttling

**Know your limits:**
- [ ] **Without bot flag:** QuickStatements throttles to ~30 edits/minute
  - A batch of 10 statements takes ~20 seconds
  - A batch of 50 statements takes ~2 minutes
  - A batch of 200 statements takes ~7 minutes
- [ ] **With bot flag:** Faster, but higher responsibility for clean edits

**Time management:**
- [ ] Do NOT start a batch late in your day
- [ ] Be present and monitoring while it runs
- [ ] If batch will take >5 minutes, set a timer and stay at your computer

---

## 5. Running the batch

**Start procedure:**
- [ ] Double-check you've completed all pre-flight checks above
- [ ] Click "Start" button (or "Run" depending on interface version)
- [ ] **Stay on the page** — do not navigate away
- [ ] Watch the progress counter increment

**Monitoring:**
- [ ] Green rows = successful
- [ ] Red rows = failed — **if ANY appear, read section 6 immediately**
- [ ] Watch for console warnings (F12 developer tools if you're technical)

**If a failure appears:**
- [ ] **STOP** — do not click "retry" immediately
- [ ] Click on the failed row to see details
- [ ] Screenshot or copy the error message
- [ ] Identify the issue (see Common Errors section below)
- [ ] Fix the source `.qs` file
- [ ] Generate a new batch — do NOT retry the failed batch

---

## 6. Common errors and what they mean

**"The given value is invalid"**
- **Cause:** Time format probably wrong (missing `+` or `/N` precision suffix)
- **Fix:** Check ISO format: `+1913-07-30T00:00:00Z/11`
- **Action:** Regenerate batch with corrected time formatting

**"Property expects type X, got Y"**
- **Cause:** String where Wikidata expects item (QID), or vice versa
- **Example:** P214 (VIAF) expects string, but you sent Q54919 without quotes
- **Fix:** Check property datatype on Wikidata
- **Action:** Correct value format in script, regenerate

**"Constraint violation: single-value constraint"**
- **Cause:** Property only allows one value per item, Wikidata already has one
- **Example:** P18 (image) — only one main image allowed
- **Fix:** Our eligibility check should have caught this
- **Action:** Investigate why check failed, add to `do_not_contribute` list

**"Permission denied"**
- **Cause:** Not logged in, account rate-limited, or item/property protected
- **Fix:** Check login status, wait 1 hour if rate-limited
- **Action:** If item is protected, skip it — do not force

**"The save has failed due to a conflict"**
- **Cause:** Someone else edited the item while batch was queued
- **Fix:** Refresh Wikidata cache
- **Action:** Run `wikidata_contribute.py --refresh-wikidata` and regenerate batch

---

## 7. Post-run audit

**Immediate checks:**
- [ ] Note final stats: N succeeded, N failed
- [ ] If ANY failures: investigate before doing anything else
- [ ] If success rate < 95%: PAUSE and review methodology

**Manual verification:**
- [ ] Pick 3 random successful statements
- [ ] Open target Wikidata items directly (e.g., https://www.wikidata.org/wiki/Q16353281)
- [ ] Confirm new statement appears
- [ ] Confirm references are present (S854, S813, S248)
- [ ] Confirm value is correct

**Update review doc:**
- [ ] Open your `queue_YYYYMMDD_HHMMSS.review.md`
- [ ] Add to bottom:
  ```markdown
  ## ✅ Submitted
  - **Batch ID:** 12345
  - **Submitted at:** 2026-05-28T09:30:00Z
  - **Success count:** 47
  - **Failure count:** 0
  - **Verified by:** [your name]
  ```
- [ ] Commit the updated review.md to git

---

## 8. Watching for community response

**48-hour monitoring period:**

For 48 hours after submission, check daily:

- [ ] **User talk:ArtBaseLV** — any messages from community?
  - https://www.wikidata.org/wiki/User_talk:ArtBaseLV
  
- [ ] **Watchlist** — any reverts on items you edited?
  - https://www.wikidata.org/wiki/Special:Watchlist
  - Add contributed items to your watchlist
  
- [ ] **WikiProject Latvia** talk page — any discussion mentioning ArtBase?
  - https://www.wikidata.org/wiki/Wikidata:WikiProject_Latvia

**Response protocol:**

- [ ] If 1 statement reverted by a human editor:
  - Read their edit summary
  - Respond on their talk page politely
  - **Do NOT re-add** the statement
  - Adjust methodology if needed
  
- [ ] If 2-5 reverts in 24 hours:
  - Post on User talk:ArtBaseLV explaining your methodology
  - Wait for community response
  - Adjust before next batch
  
- [ ] If >5 reverts in 24 hours:
  - **PAUSE all contributions immediately**
  - Post on Wikidata:Project chat explaining the issue
  - Wait for admin/community guidance

---

## 9. Rollback procedure

**If you need to undo a batch:**

**Option A: Recent batch (< 7 days old)**
- [ ] Go to your batch detail page on QuickStatements
- [ ] Click "Undo" link (if available)
- [ ] This reverses all statements from that batch
- [ ] Monitor the undo process (it's also a batch)

**Option B: Older batch or complex undo**
- [ ] Do NOT try to manually revert hundreds of edits yourself
- [ ] Go to https://www.wikidata.org/wiki/Wikidata:Administrators%27_noticeboard
- [ ] Create a new section explaining:
  - Batch ID
  - Number of statements
  - Reason for rollback
  - Your ArtBase account name
- [ ] Admins have tools for mass rollback
- [ ] Wait for admin action (usually within 24 hours)

**After rollback:**
- [ ] Document what went wrong
- [ ] Fix the issue in your script
- [ ] Test with --dry-run and --max 1
- [ ] Wait 72 hours before attempting similar contribution again

---

## 10. Escalation triggers

**STOP all contributions immediately if ANY of these occur:**

- [ ] A single batch has >5% failure rate
- [ ] An admin or experienced editor (>1000 edits) posts on User talk:ArtBaseLV
- [ ] Reverts exceed 10 in any 24-hour window
- [ ] Any block or temporary restriction is applied to the ArtBaseLV account
- [ ] A property you depend on (P7400, P214, etc.) is deprecated or restricted
- [ ] You receive an email from Wikidata or Wikimedia Foundation
- [ ] QuickStatements returns "bot flag required" error

**Escalation procedure:**
1. STOP all batches
2. Post on User talk:ArtBaseLV acknowledging the issue
3. Contact an admin or post on Wikidata:Project chat
4. Do NOT resume until issue is resolved

---

## 11. Phase escalation checklist

**Before enabling Phase 2 (biographical data):**
- [ ] Successfully completed at least 500 Phase 1 statements
- [ ] Zero reverts in last 30 days
- [ ] Positive or neutral feedback from community
- [ ] User page updated to describe Phase 2 intentions
- [ ] Post on WikiProject Latvia announcing Phase 2 plans
- [ ] Wait 7 days for feedback
- [ ] Start Phase 2 with --max 10, increase gradually

**Before enabling Phase 3 (interpretive data):**
- [ ] Successfully completed at least 2000 combined Phase 1+2 statements
- [ ] Applied for and received bot flag (https://www.wikidata.org/wiki/Wikidata:Requests_for_permissions/Bot)
- [ ] Discussed methodology on relevant WikiProjects
- [ ] Created and documented clear sourcing rules
- [ ] Start with --max 5, monitor very carefully

---

## 12. Contact information

**ArtBase project:**
- GitHub: https://github.com/elembam/artbase-catalogue
- Documentation: See repo `/docs` folder

**Wikidata resources:**
- QuickStatements: https://quickstatements.toolforge.org/
- Help: https://www.wikidata.org/wiki/Help:QuickStatements
- Project chat: https://www.wikidata.org/wiki/Wikidata:Project_chat
- WikiProject Latvia: https://www.wikidata.org/wiki/Wikidata:WikiProject_Latvia

**In case of emergency:**
- Wikidata admin noticeboard: https://www.wikidata.org/wiki/Wikidata:Administrators%27_noticeboard
- Email stewards: stewards@wikimedia.org (only for serious issues)

---

## Appendix A: First contribution checklist

**For your very first batch ever:**

- [ ] Read this entire runbook
- [ ] Verify ArtBaseLV user page exists and is descriptive
- [ ] Generate batch with `--max 1 --property P214 --artist ART-AIDE-1913`
- [ ] Review the single statement 10+ times
- [ ] Manually verify source URL
- [ ] Submit via QuickStatements
- [ ] Monitor for 72 hours
- [ ] If clean: increase to --max 5
- [ ] If clean after 5: increase to --max 10
- [ ] Never jump directly to large batches

**Your first 10 batches should be tiny. Build trust gradually.**

---

**Document control:**
- Created: 2026-05-28
- Last review: 2026-05-28
- Next review: After first 100 successful contributions
- Owner: ArtBase team
