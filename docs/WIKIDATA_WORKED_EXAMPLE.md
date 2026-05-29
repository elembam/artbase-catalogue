# Wikidata: A Worked Example

*Step-by-step walkthrough of improving an existing entry — using the real entry for Herberts Siliņš (Q23054868) as the example.*

Version 0.1

---

## Why this example is useful

Q23054868 is the entry for **Herberts Siliņš** (1926–2001), a Latvian painter. It's a *partially populated* entry — created by someone, then mostly left alone. This is the most common situation you'll find in real work: the artist exists on Wikidata, but the entry is sparse, has unsourced claims, and may even have data-quality issues.

Creating an entry from scratch is the rarer task. Improving an existing one is the workhorse activity, and it's where most of the value gets added.

---

## Step 1 — Audit the entry (10 minutes)

Open the entry in your browser: <https://www.wikidata.org/wiki/Q23054868>

Read every statement, top to bottom. For each one, ask three questions:

1. **Is it correct?** Does it match what you find in other sources?
2. **Is it sourced?** Look at the small "▸ 1 reference" or "▸ 0 references" indicator under each statement.
3. **Is it complete?** Are there obvious related statements that *should* be there?

Make a list in your scratchpad as you go. The audit for Q23054868 produces roughly this:

**Currently present (correct, with references):**
- Label: Herberts Siliņš
- Description: "Latvian painter (1926-2001)"
- Alias: Herberts Ernests Silins
- `country of citizenship`: Latvia (1 reference — *Visuotinė lietuvių enciklopedija*)
- `date of birth`: 25 August 1926 (2 references — *Visuotinė lietuvių enciklopedija*, DACS)
- Sitelink to Latvian Wikipedia article

**Present but unsourced (need to add references):**
- `instance of`: human (0 references)
- `sex or gender`: male (0 references)
- `given name`: Herberts (0 references)
- `family name`: Siliņš (0 references)

**Missing entirely (need to add):**
- `occupation`: painter (Q1028181) — this is a glaring omission for a painter!
- `date of death`: 2001 (March, per Latvian Wikipedia)
- `place of birth`: (Kurzeme region likely; verify)
- `place of death`: Mērsrags, Latvia
- `educated at`: Latvian School of Art in Esslingen (1946–48)
- `member of`: Latvian Artists' Union (since 1960)
- `award received`: lifelong stipendiate of the Latvian Culture Capital Foundation (1999)
- `field of work`: painting, watercolour
- `genre`: landscape, still life, seascape
- `movement`: post-impressionism (Latvian Wikipedia says influences of this and abstract expressionism)
- `notable work`: well-known paintings if Wikidata items exist for them
- `child`: Kārlis Siliņš (also an artist), Liene Sondore
- `spouse`: Ausma Siliņa
- External IDs: Getty ULAN (check if exists), VIAF (check), Latvian National Encyclopaedia, ISNI

**Probable data quality issue:**
- `Elite Prospects player ID`: 140149 — this is a **hockey-player database**. Almost certainly a different person with a similar name was conflated into this entry. This is the kind of error you find on real Wikidata pages and you need to handle carefully (see Step 6).

---

## Step 2 — Decide what to fix in this session

Don't try to fix everything at once. A 90-minute session can comfortably:

- Add 3–5 new sourced statements
- Add references to 2–3 existing unsourced statements
- Flag or correct 1 quality issue
- Add a couple of external identifiers

Aim for **high-value, well-sourced** improvements rather than completeness. A single statement with a good reference is worth more than five unsourced ones.

For Q23054868, this session's priority list:

1. Add `occupation: painter` (the most embarrassing gap)
2. Add `date of death: March 2001` with reference
3. Add `place of death: Mērsrags` with reference
4. Add `educated at: Latvian Academy of Art / Esslingen school` with reference
5. Add `member of: Artists' Union of Latvia` with reference
6. Address the suspected hockey-player ID conflation
7. Add references to existing unsourced claims (`instance of`, `sex`, `given name`, `family name`)
8. Search for and link Getty ULAN ID if it exists

That's enough for one session.

---

## Step 3 — Sign in and prepare

You need a Wikidata account. If you're operating on behalf of Ars Accordia, the account is **`Ars Accordia`** (or whatever name was chosen during architecture setup). Use this account, not a personal one, for all business contributions.

1. Go to <https://www.wikidata.org>
2. Click **Log in** (top right). Enter Ars Accordia credentials.
3. Confirm the account appears at top right — `Ars Accordia`.
4. Navigate back to Q23054868.
5. Keep your audit notes open in another window.

Open the relevant **source documents** in additional tabs so you can cite them as you go:

- Latvian Wikipedia: <https://lv.wikipedia.org/wiki/Herberts_Siliņš>
- Visuotinė lietuvių enciklopedija (already cited by existing claims)
- Gallery Romas Dārzs (Liepāja gallery representing him): <https://galerijaromasdarzs.lv/en/artist/herberts-silins/>
- Any auction-house records (1stDibs has documented biographical text)

---

## Step 4 — Add a new statement with a source

Let's add `occupation: painter`. This is the canonical example of a single statement.

**4.1 — Open the editor**
On the entry page, scroll to the **Statements** section. Find the *+ add statement* link at the bottom of the list (you can also use the small edit pencils next to existing statements).

**4.2 — Choose the property**
A property selector opens. Type `occupation`. Wikidata autocompletes — pick **occupation** (P106). The property label says "occupation" with a small description "occupation of a person".

**4.3 — Add the value**
A value field opens. Type `painter`. Multiple options will appear:

- *painter* (Q1028181) — "artist who creates two-dimensional artworks"
- *house painter* — different meaning
- Various others

Choose **Q1028181** — the artist-painter sense. The description disambiguates from house painters and other meanings.

**4.4 — Save**
Click **publish**. The statement now appears with "0 references" — you've added the claim, but not the source. Don't leave it like this.

**4.5 — Add a reference**
Click the small **+ add reference** link directly under the statement you just added.

A reference editor opens. The most common reference structure uses two properties:

- `stated in` (P248): which work this is sourced from
- `retrieved` (P813): the date you consulted it

For our case:
- `stated in`: search for "Visuotinė lietuvių enciklopedija" — it already has a Wikidata item (Q3576728). Select it.
- `retrieved`: enter today's date in `+1 year +month +day` format. Wikidata's date editor handles this; just type the date.
- Optionally add `reference URL` (P854) for the exact page you used.

Click **publish**. The reference appears under the statement, showing "1 reference" next to the statement now.

You've added one fully-sourced statement. Repeat the pattern for each new statement.

---

## Step 5 — Add a date statement (a slightly more complex case)

Adding a date is similar but the value editor is different.

For `date of death`:

1. *+ add statement* → property `date of death` (P570)
2. The value editor opens with a calendar. Enter `2001-03-XX` if the exact date isn't known, or use the **precision** setting to choose "month" instead of "day". This is a Wikidata convention for when you have partial information.
3. Publish.
4. Add reference — `stated in` → Latvian Wikipedia article (or directly cite the source the Latvian article uses, which is more authoritative).

**A nuance worth knowing**: Wikidata supports multiple values per statement, each ranked. If you find conflicting sources (one says March 2001, another says exactly 2 March 2001), add both and use the "rank" feature: mark the more precise one as **preferred**.

---

## Step 6 — The hockey-player problem (handling errors)

The entry has `Elite Prospects player ID = 140149`. Elite Prospects is a hockey database. Something is wrong here.

**Don't immediately delete it.** Maybe Herberts Siliņš was also a competitive sailor and Elite Prospects covers other sports? Investigate first:

1. Open `https://www.eliteprospects.com/player/140149` and see whose record it is. If it's someone else entirely (likely a different "Herberts Siliņš"), you've confirmed the error.
2. Look at the **edit history** of the Wikidata statement. Who added this and when? Sometimes there's a comment explaining a reasoning that turns out to be wrong.

When confirmed an error:

- **Click the edit pencil** next to the statement
- Select **Remove** (or its localised equivalent)
- Click **Publish**
- In the edit summary field at the bottom, write a brief explanation: *"Removed: Elite Prospects ID refers to a different person (hockey player); does not match this painter."*

The removal is logged in the entry's history. If you're wrong, another editor can revert with discussion.

If you're **uncertain**, a better path: mark the statement as **deprecated rank** instead of removing it. Deprecated rank means "this value is preserved in the record but should not be used." Click the rank indicator (a small triangle on the left of the statement), choose *deprecated*, and add a note explaining the suspicion. Other editors will see your concern and can confirm or correct.

This is genuinely how Wikidata's data quality improves — through cautious, well-explained edits, not silent deletions.

---

## Step 7 — Add references to existing unsourced claims

For each statement currently showing "0 references":

1. Click the **+ add reference** link directly under the statement
2. Add `stated in` pointing to a source
3. Add `retrieved` with today's date
4. Publish

This is unglamorous but valuable work. Each reference added increases the entry's trustworthiness.

For Q23054868, you can add the Latvian Wikipedia article as a reference for:
- `instance of: human`
- `sex or gender: male`
- `given name: Herberts`
- `family name: Siliņš`

Wikipedia articles aren't the strongest references (Wikidata prefers original sources), but they're acceptable for basic biographical claims and they're vastly better than nothing.

---

## Step 8 — Search for external authority IDs

A core Ars Accordia contribution is **linking Wikidata to other authority systems**. Each external ID is its own Wikidata property.

For Herberts Siliņš, check whether the artist has records in:

| Authority | Wikidata property | Where to search |
|---|---|---|
| Getty ULAN | P245 | `vocab.getty.edu/ulan` |
| VIAF | P214 | `viaf.org` |
| ISNI | P213 | `isni.org` |
| Latvian National Encyclopaedia | P12326 | `enciklopedija.lv` |
| RKDartists | P650 | `rkd.nl` |
| Library of Congress (NACO) | P244 | `id.loc.gov` |

For each found ID, add it as a statement on the Wikidata entry. For example: `Getty ULAN ID` (P245) = `500XXXXXX`.

The hidden value: once you add a Getty ULAN ID to Wikidata, the next person looking up the artist on Getty can follow the link back to Wikidata. The graph grows denser; everyone benefits.

---

## Step 9 — Add the Ars Accordia ID (when our property is approved)

In the architecture document we noted that Ars Accordia will eventually propose its own Wikidata property: `P-Ars Accordia-ID`. Once that property exists, every artist in our system that has a Wikidata entry should have the Ars Accordia ID added.

Property proposals on Wikidata go through a community review process (1–4 weeks). Submit one early so the property is ready when we need it.

---

## Step 10 — Save your work and document it

After your session:

1. Verify each change appears on the entry. Reload the page; everything should be there.
2. Record the session in the **contribution log** (per the AUTHORITY_CONTRIBUTION_STRATEGY): which artist, which Q-number, what changed, what was added, when, by whom.
3. If you removed or deprecated a problematic statement, also note it in the log — these are quality contributions even when they don't add data.

A typical log entry for this session:

```yaml
session: 2026-05-27
contributor: K. Andersson (Ars Accordia account)
target: Q23054868 - Herberts Siliņš

statements_added:
  - P106 (occupation): Q1028181 (painter)
  - P570 (date of death): 2001-03
  - P20 (place of death): Mērsrags
  - P69 (educated at): Latvian Academy of Art
  - P463 (member of): Artists' Union of Latvia

references_added:
  - P31 (instance of): added Latvian Wikipedia reference
  - P21 (sex or gender): added Latvian Wikipedia reference
  - P735 (given name): added reference
  - P734 (family name): added reference

external_ids_added:
  - (pending: search for ULAN, VIAF, ISNI)

corrections:
  - Removed Elite Prospects player ID (referred to a different person)

time_spent: 75 minutes
notes: Entry was sparse but accurate; major gap was missing occupation.
       One data-quality issue found and corrected. ULAN ID search not
       yet completed - queued for next session.
```

---

## Common pitfalls

**Editing the label or description casually.** Don't rename the entry unless you have a clear reason and a strong source. Labels are visible everywhere; changes propagate widely.

**Adding statements without references.** A statement with no reference is a claim made on your own authority. Wikidata's value comes from claims being traceable. Always add a reference, even if it's just "Latvian Wikipedia article."

**Treating Wikidata as a sandbox.** It isn't. Every edit is public, attributed, and permanent in the history. Edit as if your name is being read out at a museum conference, because in five years it might be.

**Deleting things you're unsure about.** Use *deprecated rank* instead. The information stays in the record but is marked as not-to-be-used. This is how data quality improves over time.

**Forgetting the contribution log.** Wikidata is the public record; the contribution log is your private record. The two together are what build the credibility metric we track in the AUTHORITY_CONTRIBUTION_STRATEGY.

---

## A realistic session outcome for Q23054868

After 75 minutes of careful work:

- Entry goes from ~7 statements (most unsourced) to ~18 statements (most sourced)
- One data-quality issue caught and handled
- 3–4 external authority IDs added
- One reference added to the contribution log
- The entry is now a *useful, citable* record rather than a stub

A year from now, a researcher looking up Latvian post-war painters will find this entry and be able to use it. That's the contribution.

---

## When to escalate

Two situations warrant pausing rather than editing:

1. **The entry has many contradictory statements with multiple references.** Sometimes two sources disagree (e.g., birth year differs by one year). Don't try to resolve this on your own — leave both, use the rank system (preferred / normal / deprecated), and note the discrepancy in the contribution log.

2. **The artist's Wikidata entry duplicates another entry.** Two Q-numbers for the same person is a real issue. Wikidata has a merge process, but it's irreversible and should be handled carefully. Document the suspected duplication and discuss with another cataloguer before merging.

---

*This document is part of the Ars Accordia operations library. Reference it during onboarding and whenever a cataloguer encounters their first Wikidata improvement task.*
