# Instruction 17 — The Client-Side SMK Preview Widget

*Hand to Copilot as a single front-end component. It builds on Instruction 16 (the SMK source adapter): it reuses that adapter's field mapping (Part D), per-object rights rule (Part E), and authority-scope model (Part A) — but **reimplemented in the browser**, because the Ars Accordia site is **static** (GitHub Pages behind Cloudflare) and cannot run the Python adapter server-side. The widget is a **live demonstration of the engine**, not the engine. The standing discipline holds, and one guardrail governs everything below: **a preview is not a published passport, and the widget must never bypass the reviewed pipeline that makes a passport trustworthy.** Where this conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## Purpose

Put a page on the Ars Accordia site where a visitor can type an SMK object number (or search), and the **browser itself** calls `api.smk.dk` live and renders the result in Ars Accordia passport style — turning a public museum record into a standardized, cross-referenced passport **in front of them**, in real time. It makes the otherwise-abstract claim ("we turn a museum record into a defensible standardized record") tangible, and it is something you can show an advisor in a meeting.

It is a **showcase of the adapter's logic**, not the cataloguing pipeline. It persists nothing, scores nothing, and produces no published record.

---

## Part A — The static-site constraint (read first)

The site has **no server** that can run Python. So "usable from the website" **cannot** mean "the adapter script runs when a visitor clicks." It means: the **visitor's browser** talks to SMK directly and renders the response. Consequences:

- All fetching and rendering happens **client-side**, in JavaScript, at runtime. No build-time data; no backend call to Ars Accordia.
- The widget re-implements the relevant adapter logic (mapping, rights, scope) **in JS**. This is a **second implementation** of Instruction 16's mapping — see Part C for the drift guard.
- No API key is needed (SMK's API is open).

---

## Part B — The CORS check and the Worker fallback

A browser can only call `api.smk.dk` directly if SMK returns permissive CORS headers (`Access-Control-Allow-Origin`).

1. **Verify CORS first.** Check whether `https://api.smk.dk/api/v1/art/?object_number=KMS4185` is fetchable from a browser on the `arsaccordia.com` origin (the API exists precisely for third-party reuse, so this is likely — but confirm, don't assume).
2. **If CORS is permissive → call SMK directly** from the widget. No proxy needed.
3. **If CORS is blocked → route through a thin Cloudflare Worker proxy** (you are already on Cloudflare). The Worker:
   - forwards the request to `api.smk.dk` and returns the response with `Access-Control-Allow-Origin: https://arsaccordia.com`;
   - is **host-restricted** — it forwards **only** to `api.smk.dk` (and only the `art` / `art/search` paths). It is **not** an open proxy;
   - carries **no business logic** — no mapping, no rights decisions, no rendering. It is a CORS shim and nothing else. All logic stays in the widget.

The widget reads one config value — "direct" vs "via Worker" (the Worker base URL) — and uses it for every call.

---

## Part C — Reuse of Instruction 16's logic (and the drift guard)

The widget mirrors three things from Instruction 16, **client-side**:

- **Field mapping** (Instruction 16, Part D): SMK JSON → passport fields (title, creator, dating, technique, dimensions, object type, inscriptions, provenance, inventory number, image). Confirm field names against the live OpenAPI schema, exactly as the adapter does.
- **Authority scope** (Instruction 16, Part A): build authority links with a `scope`, grouped for display — **person-level** (`artist_maker`: the maker, with any external IDs SMK supplies) vs **work-level** (`artwork_object`: the SMK object number + `open.smk.dk` URL).
- **Per-object rights** (Instruction 16, Part E): the rule in Part D below.

**The drift guard.** Two implementations of the same mapping (Python adapter + JS widget) can silently diverge. Mitigate:

- **Preferred:** keep the SMK→passport field map as a **single declarative table** (a small JSON/config) that both the Python adapter and the JS widget read, so there is one mapping, not two.
- **At minimum:** a **parity test** — assert that the widget's mapped output for `KMS4185` matches the Python adapter's `KMS4185.json` on the shared fields. If they disagree, the build fails. (Acceptance test 6.)

---

## Part D — Rights handling in the preview (carried over, never assumed)

The preview honours the same per-object rights rule as the adapter:

- **Read the per-object public-domain / rights flag** from the SMK response on every render.
- **`public_domain = true` (CC0):** show the image **inline** in the preview.
- **`false` / missing / ambiguous:** **do not show the image.** Instead show a clear "Image under copyright — view at SMK" **link** to the SMK page / IIIF. **Never assume CC0.**
- Always display the rights status as a recorded fact in the preview, whichever way it falls.

---

## Part E — Passport-style rendering

Render the live result in the Ars Accordia **passport visual language** (Fraunces / Public Sans / JetBrains Mono; paper / oxblood / gilt), so the demonstration is convincing — it should *look* like a passport. Sections:

- **Header** — title · maker · dating.
- **§ Identity** — the mapped descriptive fields; absent fields shown as **gaps**, never invented (mirrors the adapter's "11 imported, 1 gap" honesty).
- **§ Authority links** — **grouped by scope**: "Identifies the artist" (person-level) and "Identifies the work" (work-level: the SMK object record, linking to `open.smk.dk`). This is where the preview *shows off* the scope model: a visitor can see that the work itself has a public, clickable authority record.
- **§ Rights** — the per-object status (Part D).
- **Image** — inline only if public domain (Part D).
- **The preview banner** — always present (Part F).

---

## Part F — "Preview, not a published passport" (the integrity core)

This guardrail is the point of the component, not a footnote. The widget is a *live preview of how Ars Accordia structures a public record* — it is **not** a catalogued passport, and it must never be mistaken for one.

- **A persistent, always-visible label**, e.g.: *"Live preview — this shows how Ars Accordia structures a public museum record. It is not a catalogued passport. Catalogued passports are produced through Ars Accordia's reviewed process."*
- The widget **persists nothing** — no write to the catalogue, no file, no database; reloading the page clears it.
- The widget **scores nothing** — no Ars Accordia Score, no standard, no band. (Scoring belongs to assessed collections, not a live lookup.)
- The widget **performs no Wikidata give-back** — it generates **no** contribution task and submits **no** edit. Reconciliation stays in the reviewed backend pipeline (Instruction 16, Part G). *(Optional and strictly read-only: it may indicate whether the work already has a Wikidata item and link to it — but it writes nothing.)*
- The widget **never implies an SMK "assessment."** SMK-sourced material is **cross-referenced reference data**, never a scored rating of an institution Ars Accordia was not engaged to assess — the same line held for the LNMM-consent wording.

The reason is the whole project's reason: the moment a public web tool can mint published, scored passports without the review-and-reconcile gate, the records stop being trustworthy. Preview in the browser; real passports through the pipeline.

---

## Files

```
site/sources/smk/index.html        # the static widget page (HTML/CSS/JS, site visual language)
site/sources/smk/smk-preview.js     # fetch + map + rights + render (mirrors Instruction 16)
workers/smk-cors-proxy/             # the thin Cloudflare Worker — ONLY if Part B step 3 is needed
data/mappings/smk-field-map.json    # the shared mapping table (Part C, preferred), read by adapter + widget
```

(Path names are indicative — fit them to the existing site structure. A "Sources" section showcasing the collection sources Ars Accordia connects to is a natural home.)

---

## Acceptance tests

1. **Public-domain work.** Entering `KMS4185` renders a passport-style preview with the image **inline**, a work-level authority link to the SMK record (`scope = artwork_object`, resolving to `open.smk.dk`), the maker shown person-level, the rights status shown, and the **preview banner present**.
2. **Copyrighted work.** A © work from search renders **without** an inline image, showing a "view at SMK" link instead; rights status reflects copyright.
3. **Search.** Searching "Hunæus" returns a result list with public-domain / © flags; selecting a result renders its preview.
4. **Not found.** An invalid object number shows a clean "not found" — **no broken render, no phantom passport, nothing persisted.**
5. **CORS path.** If direct browser calls to `api.smk.dk` succeed, the widget uses them; if blocked, it uses the host-restricted Worker proxy — and the proxy forwards **only** to `api.smk.dk`.
6. **Mapping parity.** The widget's mapped output for `KMS4185` matches the Python adapter's `KMS4185.json` on the shared fields (drift guard, Part C); divergence fails the build.
7. **No persistence.** After any preview, reloading the page clears everything; no catalogue record, file, or score was created anywhere.
8. **Framing always holds.** Every state of the page (result, empty, error) shows the "preview, not a catalogued passport" label, and no state displays a score, a band, or an "SMK assessment."

---

## What this component does NOT do

- It does **not** run server-side — the site is static; all logic is client-side (plus an optional thin CORS Worker).
- It does **not** persist, write to the catalogue, or produce a published passport.
- It does **not** score anything, or imply an SMK assessment / rating.
- It does **not** perform a Wikidata give-back or submit any edit (read-only indication at most).
- It does **not** assume CC0 — image display is gated on the per-object rights flag.
- It does **not** bulk-display SMK's collection — one looked-up work at a time.
- It does **not** replace the reviewed pipeline — it demonstrates the engine; it is not the engine.

---

## First build step

**SMK preview widget v0.1:** a static page that takes `KMS4185`, calls `api.smk.dk` from the browser (direct if CORS allows, else via the thin Worker), maps the response with the shared field map, applies the rights rule (image inline because KMS4185 is public domain), renders it in passport style with person-level and work-level authority links grouped, and shows the persistent "live preview — not a catalogued passport" banner. That single page proves the client-side engine and becomes the template for previewing any future collection source.
