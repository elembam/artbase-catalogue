# Manual Wikidata Entry — Step-by-Step Runbook
## Ars Accordia · Books Batch 1 · 2026-05-30

Open this file alongside your browser. Complete all steps for Book 1 before starting Book 2.

---

## BEFORE YOU START (both books)

1. **Confirm you are logged in** as `ArsAccordia` at https://www.wikidata.org
2. **Run duplicate check** — go to https://query.wikidata.org/ and run this query.
   It must return **0 results** before you proceed.

```sparql
SELECT ?book ?bookLabel WHERE {
  VALUES ?isbn { "9789984393810" "9789984807522" }
  ?book wdt:P212 ?isbn .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,lv". }
}
```

✅ If 0 results → safe to proceed  
❌ If any results → stop and report back

---

---

# BOOK 1 — Hansabankas mūsdienu mākslas kolekcija (2007)

## Step 1 — Create the item

Go to: https://www.wikidata.org/wiki/Special:NewItem

Fill in the form:

| Field | Value |
|-------|-------|
| **Language** | `lv` |
| **Label** | `Hansabankas mūsdienu mākslas kolekcija` |
| **Description** | `2007. gada Hansabankas mūsdienu mākslas kolekcijas katalogs` |
| **Also known as** | *(leave blank for now)* |

Click **Create**. You will land on the new item page. Note the QID shown in the URL (e.g. `Q12345678`). **Write it down here: ___________**

---

## Step 2 — Add English label and description

Click the **pencil icon** next to "Latvian" at the top, then add:

- Click **"Add language"** (or the `+` next to labels)
- Language: `en`
- Label: `Hansabanka Contemporary Art Collection`
- Description: `2007 catalogue of the Hansabanka contemporary art collection`

Click **Publish**.

---

## Step 3 — Add statements (one by one)

Click **"+ add statement"** for each row below.

### 3.1 — instance of
- Property: **instance of** (P31)
- Value: search for `version, edition, or translation` → select **Q3331189**
- Click **Publish**

### 3.2 — title (Latvian)
- Property: **title** (P1476)
- Value: `Hansabankas mūsdienu mākslas kolekcija`
- Language: `lv`
- Click **Publish**

### 3.3 — title (English)
- Property: **title** (P1476) again (click **"+ add value"** under the same property)
- Value: `Hansabanka contemporary art collection`
- Language: `en`
- Click **Publish**

### 3.4 — ISBN-13
- Property: **ISBN-13** (P212)
- Value: `978-9984-39-381-0`  ← use hyphens exactly as shown
- Click **Publish**

### 3.5 — publisher
- Property: **publisher** (P123)
- Value: search `Swedbank Latvia` → select **Q104429642**
  *(This is the same legal entity — AS Hansabanka was renamed Swedbank Latvia in 2008)*
- Click **Publish**

### 3.6 — author name string
- Property: **author name string** (P2093)
- Value: `Ilze Žeivaite`  ← copy exactly, including the diacritics
- Click **Publish**

### 3.7 — publication date
- Property: **publication date** (P577)
- Value: `2007`  ← enter just the year; Wikidata will set precision to "year" automatically
- Click **Publish**

### 3.8 — place of publication
- Property: **place of publication** (P291)
- Value: search `Riga` → select **Q1773**
- Click **Publish**

### 3.9 — language of work (Latvian)
- Property: **language of work or name** (P407)
- Value: search `Latvian` → select **Q9078**
- Click **Publish**

### 3.10 — language of work (English)
- Property: **language of work or name** (P407) again (click **"+ add value"**)
- Value: search `English` → select **Q1860**
- Click **Publish**

### 3.11 — number of pages
- Property: **number of pages** (P1104)
- Value: `238`
- Click **Publish**

---

## Step 4 — Record the QID

After all statements are saved, copy the QID from the URL bar.

Run this command in your terminal:
```
python3 scripts/record_book_qid.py SRC-HANSABANKA-2007 Q_________
```
Replace `Q_________` with the actual QID.

---

---

# BOOK 2 — Mākslinieks. Portrets. Pašportrets (LNMM, 2009)

## Step 1 — Create the item

Go to: https://www.wikidata.org/wiki/Special:NewItem

| Field | Value |
|-------|-------|
| **Language** | `lv` |
| **Label** | `Mākslinieks. Portrets. Pašportrets` |
| **Description** | `2009. gada Latvijas Nacionālā mākslas muzeja izstādes katalogs` |

Click **Create**. Note the QID. **Write it down here: ___________**

---

## Step 2 — Add English label and description

- Language: `en`
- Label: `Artist. Portrait. Self-portrait`
- Description: `2009 exhibition catalogue, Latvian National Museum of Art`

Click **Publish**.

---

## Step 3 — Add statements

### 3.1 — instance of
- Property: **instance of** (P31)
- Value: **Q3331189** (version, edition, or translation)
- Click **Publish**

### 3.2 — title (Latvian)
- Property: **title** (P1476)
- Value: `Mākslinieks. Portrets. Pašportrets`
- Language: `lv`
- Click **Publish**

### 3.3 — title (English)
- Property: **title** (P1476) — add value
- Value: `Artist. Portrait. Self-portrait`
- Language: `en`
- Click **Publish**

### 3.4 — ISBN-13
- Property: **ISBN-13** (P212)
- Value: `978-9984-807-52-2`
- Click **Publish**

### 3.5 — author / compiler
- Property: **author** (P50)
- Value: search `Dace Lamberga` → select **Q109864986**
- Click **Publish**

### 3.6 — publisher (LNMM)
- Property: **publisher** (P123)
- Value: search `Latvijas Nacionālais mākslas muzejs` → select **Q1370465**
- Click **Publish**

### 3.7 — publisher (Neputns)
- Property: **publisher** (P123) — add value
- Value: search `Neputns` → select **Q30212561**
- Click **Publish**

### 3.8 — publication date
- Property: **publication date** (P577)
- Value: `2009`
- Click **Publish**

### 3.9 — place of publication
- Property: **place of publication** (P291)
- Value: **Q1773** (Riga)
- Click **Publish**

### 3.10 — language of work (Latvian)
- Property: **language of work or name** (P407)
- Value: **Q9078** (Latvian)
- Click **Publish**

### 3.11 — language of work (English)
- Property: **language of work or name** (P407) — add value
- Value: **Q1860** (English)
- Click **Publish**

### 3.12 — number of pages
- Property: **number of pages** (P1104)
- Value: `107`
- Click **Publish**

---

## Step 4 — Record the QID

```
python3 scripts/record_book_qid.py SRC-LNMM-PORTRAITS-2009 Q_________
```

---

---

## AFTER BOTH BOOKS

Once both commands above have been run:

```bash
cd /Users/elemba/VSCode/ArtBank/ArtBase
git add artbase_export/data/sources/SRC-HANSABANKA-2007.json \
        artbase_export/data/sources/SRC-LNMM-PORTRAITS-2009.json
git commit -m "chore: record Wikidata QIDs for Hansabanka 2007 and LNMM Portraits 2009 source records"
```

Done ✓
