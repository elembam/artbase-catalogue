# Handover — Build the /insights/ Content Section

*Hand to Copilot as a site component (numbering is yours — e.g. Instruction 22). Goal: stand up an editorial **/insights/** section on arsaccordia.com — an index page plus long-form article pages — rendered from the three provided markdown articles, in the site's existing visual language and build pipeline. This is the content-depth engine (the substance Google's indexing wants) and the place the "who is this?" discovery trail lands. It is editorial content, not passports or records — keep the two clearly separate. Where this conflicts with Copilot's instinct, the handover wins — ask before deviating.*

---

## Purpose

Publish a small, high-quality **Insights** section that explains the problem Ars Accordia solves, in the project's own voice — starting with three articles. It serves three ends at once: real content depth for search (addressing the "discovered / crawled — not indexed" backlog with substance, not stubs), a credible landing for anyone who arrives via the Wikidata/P973 trail asking who Ars Accordia is, and durable positioning material the advisor conversations can point to.

---

## Part A — Structure & URLs

- **Index page:** `/insights/` — a titled landing page listing the articles newest-first, each as a card (title, one-line standfirst/subtitle, read-time or date optional). Clean, calm, no marketing clutter.
- **Article pages:** `/insights/<slug>/` — one per article, long-form reading layout.
- **Slugs (fixed):** `the-provable-collection`, `what-provenance-is`, `inventory-is-not-a-record`.
- Use the existing static-site conventions (trailing-slash or `.html` — match whatever the rest of the site uses, and set canonicals to the one true form, per the earlier canonical-tag work).

## Part B — Rendering

- Render the three markdown files through the existing Jinja2/build pipeline into HTML in the **site's visual language** (Fraunces display / Public Sans body / JetBrains Mono; paper / oxblood / gilt). Do not invent a new theme.
- Long-form reading layout: comfortable measure (~65–75 characters), generous line-height, clear `<h2>` section breaks, restrained use of the oxblood/gilt accents (a rule under the H1, section markers if consistent with the method page). Prioritise readability over decoration.
- The markdown H1 is the article title; the italic line beneath it is the standfirst/subtitle.

## Part C — SEO essentials (this is the point — get it right)

For each article page:
- **`<title>`** — the article's search title (see Part F), not just the H1.
- **`<meta name="description">`** — the provided description (Part F).
- **`<link rel="canonical">`** to the page's own URL.
- **Schema.org `Article` JSON-LD** in `<head>`: `headline`, `description`, `datePublished`, `author` (Organization: Ars Accordia), `publisher` (Ars Accordia, with logo), `mainEntityOfPage` (the canonical URL). Conditional fields only — omit anything absent; valid JSON (mind trailing commas); validate in Google's Rich Results Test before shipping.
- **Add all four URLs** (`/insights/` + three articles) to `sitemap.xml`, and regenerate it.
- These are substantial, unique pages — exactly the content that should be indexed. After publishing, **request indexing** for the three articles and the index in Search Console.

## Part D — Internal linking (do not skip)

- Link to **/insights/** from the primary navigation and/or the homepage, so the section isn't an orphan reachable only by sitemap.
- **Cross-link the articles** to each other where the text invites it (e.g. "The Provable Collection" → "What Provenance Actually Is"; "Inventory Is Not a Record" → the Collection Assessment / method page). A few honest in-text links, not a link farm.
- From each article, link once to the relevant **method** or **assessment** page, so a persuaded reader has a next step. Keep it a quiet link, not a banner.

## Part E — Editorial voice guardrails (carry from the site)

- **Calm and neutral.** These read like considered essays, not a pitch. No urgency wording, no hard sell.
- **No price promises.** Nothing may imply Ars Accordia raises a work's worth or reveals hidden value. The articles report the *market's* documented behaviour and keep the standing line: **we document; we do not appraise or authenticate.** Preserve that line wherever value is discussed.
- **No pushiness.** The CTAs are the quiet closes already in the copy ("Secure the record.", "Your proof of art."). Do not add pop-ups, banners, or "act now" language.
- **Editorial, not record.** These pages are clearly the Insights section — never styled or labelled to look like a passport, a score, or an institutional rating.

## Part F — The three initial articles

| Slug | H1 (in file) | `<title>` | Meta description |
|---|---|---|---|
| `the-provable-collection` | The Provable Collection | The Provable Collection — Inherited Art & the Great Wealth Transfer | Nearly $1 trillion in art is passing to heirs who can't prove what they hold. Why documentation, not taste, decides what a collection is worth. |
| `what-provenance-is` | What Provenance Actually Is (and What It Isn't) | What Provenance Actually Is — and What It Isn't | Provenance underwrites authenticity and value in art — but it isn't a certificate, a valuation, or a single receipt. A plain-language guide. |
| `inventory-is-not-a-record` | Why an Inventory Is Not a Record | Why an Inventory Is Not a Record — Documenting an Art Collection | A list tells you what you own. A record lets someone else prove it. The difference decides whether a collection survives a handover. |

Source markdown files provided: `ars-accordia-insight-the-provable-collection.md`, `ars-accordia-insight-what-provenance-is.md`, `ars-accordia-insight-inventory-is-not-a-record.md`.

Set `datePublished` to the publish date; order the index newest-first (lead with **The Provable Collection** as the flagship).

## Done criteria

1. `/insights/` index live, listing the three articles, linked from site navigation/homepage (not orphaned).
2. Three article pages live at their fixed slugs, rendered in the site's visual language, readable long-form.
3. Each carries a proper `<title>`, meta description, canonical, and valid `Article` JSON-LD (Rich Results Test passes).
4. Sitemap regenerated with all four URLs; indexing requested for the articles in Search Console.
5. Articles cross-link sensibly and each links once to the method/assessment page; voice guardrails intact; no page implies valuation or authentication by Ars Accordia.

---

*Follow-on (not this task): this section is designed to grow. Publishing one considered piece on a steady cadence is, over time, the strongest organic-content engine the project has — and every article is a genuine artifact, never a stub. Future topics that fit the same voice: the five-layer standards reading, what a catalogue raisonné is and isn't, restitution and the 1933–45 provenance gap, and the Wikidata give-back as public infrastructure.*
