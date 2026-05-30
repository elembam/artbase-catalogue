# Instruction 9 — Contributors, User Submissions, Moderation & Privacy

*Hand to Copilot as a single component. It generalizes Instructions 7–8 (sources, attestations, the gallery origin, the source ledger) to **all** data contributors, and adds the process and protections required once private users can submit data. Where it conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## Purpose

Private users will eventually add artists and artworks. A user is structurally the same as Galerija Jēkabs — a non-authoritative **origin** source — so the data model already started (the unified `Contributor` with trust flags) is correct. This instruction formalizes that model and adds the three things opening to the public requires and that trust flags alone do not provide:

1. a **moderation gate** (submissions are reviewed before they enter the canonical/published dataset),
2. **owner-claim handling** (self-interested submissions are labelled and corroborated, not trusted), and
3. a **privacy/GDPR design** (the registry holds personal data about living people — contributors, artists, and third parties).

This builds on, and does not replace, the `Contributors` / `Source_Documents` / attestation / source-ledger structure already in place.

---

## The conceptual core: four orthogonal dimensions, never collapsed

The earlier model carried two ideas (origin ≠ authority; per-source trust flags). User submissions add more. Keep these **separate** — each answers a different question:

| Dimension | Question it answers | Field(s) |
|---|---|---|
| **Role** | *What kind of claim is this?* origin / authority / owner-asserted / provenance | attestation `role` |
| **Trust type** | *How authoritative is this source for a fact?* (citable? can confirm?) | `wikidata_citable`, `can_confirm` |
| **Verification level** | *Is the contributor who they claim, acting in good faith?* | `verification_level` |
| **Moderation status** | *Has this specific submission been reviewed?* | `status` (pending_review → accepted/rejected) |

The crucial new insight: **trust-*type* is not trust*worthiness*.** A `private_collector` with `can_confirm: false` is correctly scoped *for facts* — but that flag says nothing about whether the submission is genuine, accurate, or made in good faith. The gallery was **one known entity**; users are **many unknown ones**. Verification level and moderation status are the dimensions that handle that, and they are independent of the trust-type flags.

---

## Part A — The unified Contributor model (formalized)

Every data contributor is a `Contributor`. Defaults by type:

| `contributor_type` | `wikidata_citable` | `can_confirm` | Example |
|---|---|---|---|
| `authority_file` | true | true | Wikidata, VIAF, ULAN |
| `institutional` | true *(if from an authoritative document — see Part B)* | true | National museum catalogue |
| `platform_staff` | false | true *(must cite a basis — see Part G)* | Ars Accordia cataloguer |
| `commercial_gallery` | false | false | Galerija Jēkabs |
| `private_collector` | false | false | A user submitting their own works |
| `data_partner` | false | false | A gallery feeding data under agreement |

Add the **orthogonal verification axis**:

| `verification_level` | Meaning |
|---|---|
| `unverified` | Account exists, identity unconfirmed |
| `email_verified` | Email confirmed only |
| `identity_verified` | Identity established (KYC-style, for higher-trust submissions) |
| `known_institution` | A vetted institutional/partner relationship |

`verification_level` does **not** change `wikidata_citable`/`can_confirm` — a verified collector is still `can_confirm: false`. It governs how much scrutiny a submission gets and whether it can be fast-tracked through review.

The three layers stay clean:
- **Contributor** = the *who* (gallery, user, institution, staff).
- **Source_Document** = the *what* (paintings.lv; a published catalogue; a single user submission).
- **Attestation** = the link (entity ↔ source-document) with a `role`.

---

## Part B — Trust flags: contributor default, source-document override

The "institutional → true *if auth*" conditional is the tell that trust can't live only on the contributor. A national museum's **official catalogue** is citable; its **blog or press release** is not — same contributor, different document.

So:
- The **contributor** sets the *default* `wikidata_citable` / `can_confirm`.
- The **Source_Document** may **override** it (`inherit` / `true` / `false`).

Every code path that emits a Wikidata reference or sets `confirmed` resolves trust as: *source-document override if set, else contributor default.* This future-proofs institutional and data-partner sources and prevents a museum's non-authoritative output from being cited as if it were its catalogue.

---

## Part C — User submissions: the data flow

A user submission is parallel to the gallery (Contributor → Source_Document → attestation), with moderation state attached:

```
Contributor   CON-USER-00042   (private_collector, verification_level=email_verified)
   │
   ▼
Source_Document  SRC-USER-00042-0007   (source_type: user_submission, status: pending_review)
   │
   ▼
Attestation   artwork ⟷ SRC-USER-00042-0007   (role: owner_asserted, authoritative: false,
                                               status: pending_review)
```

A submission may also create **new entity records** (a new artwork, possibly a new artist). Those new records carry `publication_status: pending_review` and are **excluded from the canonical export, the public site, and any Wikidata contribution until accepted** (Part D).

User-submission Source_Document schema:

```json
// data/sources/SRC-USER-00042-0007.json
{
  "source_id": "SRC-USER-00042-0007",
  "source_type": "user_submission",
  "contributor_id": "CON-USER-00042",
  "wikidata_citable": false,
  "can_confirm": false,
  "submitted_at": "2026-05-DD",
  "status": "pending_review",
  "reviewed_by": null,
  "reviewed_at": null,
  "submission_payload_ref": "submissions/SUB-00042-0007.json",
  "gdpr": { "contains_personal_data": true, "third_parties_named": false }
}
```

---

## Part D — The moderation gate (the critical process)

User-generated content must be **quarantined and reviewed before it enters the trusted dataset.** This is not optional: the registry's value is its integrity, and one unmoderated path lets anyone inject anything into the dataset that *is* the moat. The model is Wikipedia-style patrolling.

**States** (on the submission Source_Document and on any entity/attestation it creates):

```
pending_review ──► accepted        (a platform_staff contributor approves)
               ├──► needs_more_info (returned to submitter)
               └──► rejected        (spam / fraud / unverifiable / out of scope)
```

**Quarantine rules while `pending_review`:**
- Not written to the canonical export.
- Not rendered on the public site (or rendered only in the submitter's private workspace).
- **Never** eligible for Wikidata contribution.
- Excluded from `confirmed` status — a pending submission cannot be confirmed.

**What review checks** (the cataloguer's job):
- Is the contributor's identity/good-faith adequate for what's being claimed?
- Does the artwork/artist plausibly exist; are there obvious duplicates to merge?
- Are owner-asserted attribution and provenance flagged as claims (Part E)?
- Are there personal-data / third-party concerns (Part F)?

Only on `accepted` does the entity become publishable and its attestations active. Acceptance does **not** make the user a citable authority — it makes the submission *visible and trusted-as-an-owner-claim*; facts within it still follow the trust flags and need authority corroboration to become `confirmed`.

---

## Part E — Owner-asserted claims

A collector submitting their *own* work has a direct financial incentive to inflate attribution, provenance, and value — sharper than the gallery. So:

- Owner-originated attribution/provenance use **`role: owner_asserted`** (distinct from `data_origin`), so the source ledger shows them *as claims*.
- Owner-asserted attribution and provenance are **never** treated as fact without **independent corroboration** (an authority, a published catalogue, expert verification), and are **visibly labelled** as owner-asserted in the public record.
- "Owner says it is a Rozentāls" is data about a *claim*, not about the *work*. The passport must not present an owner-asserted attribution with the same authority as an authority-confirmed one.

The source ledger surfaces this automatically: an `owner_asserted` attestation sits under `origin` (not `authority`), `citable: false`, and any fact it alone supports shows `has_citable_source: false`.

---

## Part F — Privacy & GDPR

Ars Accordia is Sweden-based, the mission is *art held by private people*, and users will submit data. That makes it a **data controller of personal data**. A single `gdpr_sensitive` flag cannot carry this; the design must support the following. *(This is architecture informed by GDPR principles, not legal advice — confirm specifics with a qualified Swedish/EU data-protection professional before user submissions launch.)*

**Three distinct data subjects — do not conflate:**
1. **The contributor** (the user) — you hold their account/identity data.
2. **The artist** — if **living**, their biographical data is personal data.
3. **Third parties named in a submission** — previous owners, the current collector — who **did not consent**. This third-party exposure is the most-overlooked risk in art databases.

**Design requirements:**
- **`living_person` flag** on person records (artists, owners) drives sensitivity — *not* one coarse boolean. Most historical Latvian painters are deceased and outside GDPR; the concern concentrates on living artists and owners.
- **Ownership data is sensitive.** Knowing a named individual owns valuable works is a theft/wealth-disclosure risk. **Owner identity defaults to `visibility: private`** for living owners; promotion to `restricted`/`public` requires explicit, recorded consent.
- **Lawful basis per data category** — record the basis under which each category (contributor account data, living-artist biography, ownership records) is processed.
- **Data minimization** — collect only what the catalogue function needs; don't store extraneous personal detail because a submission happened to include it.
- **Erasure vs. permanence — resolve the collision explicitly.** The project promises permanent IDs (DOI/ISIN-style); GDPR Art. 17 grants living people erasure rights. Policy:
  - The **object record and its permanent ID persist** — an artwork is not personal data; the ID can survive as a tombstone.
  - **Personal fields are redactable/anonymizable** (owner identity, a living artist's private details) on a valid request, without destroying the object record.
  - Data already **published or contributed to Wikidata cannot be unilaterally retracted** — so scope what personal data is ever published/contributed *before* it goes out, not after.
- **A data-subject-request log** (erasure / rectification / access) with the redaction action recorded in the audit trail.

The architecture must be **redaction-compatible from day one**: separate personal fields (erasable) from object/identity fields (permanent), so a future erasure request is a field-level redaction, not an impossible deletion of a permanent record.

---

## Part G — Staff confirmation must cite a basis

`platform_staff` has `can_confirm: true`, but staff are **not** themselves an authority. Staff *verify against* sources; they are not the basis. So:
- Setting a record to `confirmed` via staff action **must record what justified it** — the authority/source consulted — into the ledger's `verification.basis` / `confirmed_by`.
- A `confirmed` record with no justifying source behind the staff action is invalid. Staff confirmation is not a backdoor to unsourced `confirmed` data.

---

## Part H — Origin completeness (the 274 vs 288 gap)

Instruction 8's ingestion linked 274 of the 288 existing artists to the gallery. The remaining **14 have no documented origin** — which defeats the purpose. Resolve each:
- If name-normalization missed them → fix the match and attach the `data_origin` attestation.
- If they genuinely came from elsewhere → record *that* origin (another source, or `platform_staff` if hand-entered).

**Invariant going forward:** every entity record has at least one origin attestation. Add a check (e.g. in `audit_provenance.py`) that flags any artist/artwork with no origin source at all.

---

## Airtable schema additions

**`Contributors`** (extend the table already created):
- `Contributor ID` (primary), `Display Name`
- `contributor_type` (single select — the six types)
- `verification_level` (single select — unverified / email_verified / identity_verified / known_institution)
- `wikidata_citable` (checkbox), `can_confirm` (checkbox) — defaults by type
- `living_person` (checkbox), `gdpr_role` (single select — data_subject / not_applicable)
- `contact`, `account_ref`, `created_at`, `notes`

**`Source_Documents`** (extend):
- `wikidata_citable_override`, `can_confirm_override` (single select — inherit / true / false)
- `status` (single select — active / pending_review / accepted / needs_more_info / rejected)
- `reviewed_by` (link → Contributors), `reviewed_at`
- `contains_personal_data` (checkbox), `third_parties_named` (checkbox)

**`Attestations`** (extend):
- `role` values now include `owner_asserted` and `user_submission`
- `status` (inherits the submission's review state)

**Entity tables (`Artists_Makers`, `Artworks`)** (extend):
- `publication_status` (single select — pending_review / published / rejected)
- `living_person` (checkbox, person records)
- `owner_visibility` (single select — private / restricted / public; default private when the owner is a living person)
- redaction-aware separation of personal fields from object/identity fields

---

## CLI

```
python3 scripts/contributors.py --create-user --email <addr>        # create a CON-USER-{id} (unverified)
python3 scripts/contributors.py --set-verification CON-USER-42 identity_verified

python3 scripts/submissions.py --list-pending                       # queue of submissions awaiting review
python3 scripts/submissions.py --review SRC-USER-42-0007 --accept    # staff action; records reviewer + basis
python3 scripts/submissions.py --review SRC-USER-42-0007 --reject --reason "<text>"

python3 scripts/build_source_ledger.py --check                      # ledger reflects roles incl. owner_asserted
python3 scripts/audit_provenance.py --check-origins                 # flag any entity with no origin source
python3 scripts/gdpr.py --redact <entity_id> --request <REQ-id>     # redact personal fields, keep object + ID
python3 scripts/gdpr.py --list-requests
```

---

## Acceptance tests

1. A `private_collector` contributor is created with `wikidata_citable: false`, `can_confirm: false`, regardless of `verification_level`.
2. Raising a contributor's `verification_level` to `identity_verified` does **not** change its trust flags.
3. A user submission creates a `user_submission` Source_Document with `status: pending_review`; any new entity it creates has `publication_status: pending_review`.
4. While `pending_review`: the entity is absent from the canonical export, absent from the public site, and not eligible for Wikidata contribution or `confirmed` status.
5. On `accept`, the entity becomes publishable; its `owner_asserted` attestation is active but the entity is **not** auto-`confirmed`.
6. A Source_Document `wikidata_citable_override: false` on an `institutional` contributor blocks that document from being cited even though the contributor default is true.
7. An `owner_asserted` attestation appears under `origin` in the source ledger (`citable: false`); a fact it alone supports shows `has_citable_source: false`.
8. Setting `confirmed` via staff action with no recorded basis fails; with a recorded authority basis it succeeds and `verification.basis` is populated.
9. `audit_provenance.py --check-origins` flags any of the 14 artists still lacking an origin source.
10. A living owner's identity defaults to `owner_visibility: private`; making it public requires a recorded consent flag.
11. `gdpr.py --redact` removes the personal fields of a living person while the object record and permanent ID persist (tombstone), and logs the action.

---

## What this component does NOT do

- It does **not** let user-submitted data reach the public site, the canonical export, or Wikidata before review. Quarantine is unconditional.
- It does **not** make any user a citable Wikidata authority or let a user submission confirm a record.
- It does **not** treat owner-asserted attribution/provenance as fact without independent corroboration, and never displays it with authority-confirmed weight.
- It does **not** raise trust flags based on `verification_level` — identity verification gates scrutiny, not citability.
- It does **not** publish living individuals' ownership data by default, and does **not** store personal data beyond what the catalogue function requires.
- It does **not** promise to retract data already published or contributed to Wikidata — erasure is scoped to redactable personal fields, decided before publication.
- It does **not** constitute legal advice; the privacy design must be validated with a qualified data-protection professional.
