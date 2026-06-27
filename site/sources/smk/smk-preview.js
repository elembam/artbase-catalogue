/**
 * smk-preview.js — Client-side SMK Open API adapter and renderer.
 *
 * Mirrors the field mapping from artbase_export/adapters/smk.py (Spec 16)
 * and data/mappings/smk-field-map.json (the shared declarative table).
 *
 * Discipline (Spec 17):
 *   - Fetches directly from api.smk.dk (CORS: Access-Control-Allow-Origin: *)
 *   - Rights are read per-object; image display is gated on public_domain === true
 *   - Renders in preview only — persists nothing, scores nothing, writes nothing
 *   - Preview banner is injected by this script and must always be visible
 *
 * Also exportable as a Node module for parity testing (acceptance test 6).
 */

'use strict';

/* ── Constants (mirrors smk.py) ───────────────────────────────────────────── */

const SMK_API_BASE    = 'https://api.smk.dk/api/v1';
const SMK_OPEN_BASE   = 'https://open.smk.dk/artwork/image';
const SMK_COLLECTION_QID  = 'Q671249';
const SMK_COLLECTION_NAME = 'Statens Museum for Kunst';

/* ── Config: direct or Worker proxy ──────────────────────────────────────── */

const SMK_CONFIG = {
  // 'direct' uses api.smk.dk (CORS is open; confirmed 2026-06-26).
  // Set to { mode: 'proxy', base: 'https://YOUR_WORKER.workers.dev' } if direct ever blocked.
  mode: 'direct',
  base: SMK_API_BASE,
};

function _apiBase() {
  return SMK_CONFIG.mode === 'direct' ? SMK_API_BASE : SMK_CONFIG.base;
}

/* ── Fetch helpers ────────────────────────────────────────────────────────── */

async function fetchByObjectNumber(objectNumber) {
  const url = `${_apiBase()}/art/?object_number=${encodeURIComponent(objectNumber.trim().toUpperCase())}`;
  const resp = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!resp.ok) throw new Error(`SMK API error: HTTP ${resp.status}`);
  const data = await resp.json();
  const items = data.items || [];
  if (!items.length) throw new Error(`Not found: ${objectNumber}`);
  return items[0];
}

async function searchSMK(query) {
  const url = `${_apiBase()}/art/search/?keys=${encodeURIComponent(query)}`;
  const resp = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!resp.ok) throw new Error(`SMK API error: HTTP ${resp.status}`);
  const data = await resp.json();
  return data.items || [];
}

/* ── Dimension helpers (mirrors Python _dim_cm / _dim_display) ───────────── */

function _dimCm(dimensions, typeName) {
  for (const d of dimensions) {
    if ((d.type || '').toLowerCase() === typeName.toLowerCase()
        && (d.unit || '').toLowerCase() === 'centimeter') {
      const v = parseFloat(d.value);
      return isNaN(v) ? null : v;
    }
  }
  return null;
}

function _fmtDim(n) {
  // Match Python float formatting: 28.0 stays 28.0, 23.5 stays 23.5
  return Number.isInteger(n) ? n.toFixed(1) : String(n);
}

function _dimDisplay(dimensions) {
  const h = _dimCm(dimensions, 'højde');
  const w = _dimCm(dimensions, 'bredde');
  const d = _dimCm(dimensions, 'dybde');
  if (h !== null && w !== null) {
    const base = `${_fmtDim(h)} × ${_fmtDim(w)}`;
    return d !== null ? `${base} × ${_fmtDim(d)} cm` : `${base} cm`;
  }
  return null;
}

/* ── Year parser ──────────────────────────────────────────────────────────── */

function _parseYear(dt) {
  if (!dt) return null;
  const y = parseInt(String(dt).substring(0, 4), 10);
  return isNaN(y) ? null : y;
}

/* ── Materials / techniques ───────────────────────────────────────────────── */

function _materialsDisplay(raw) {
  const t = raw.techniques || [];
  const m = raw.materials || [];
  if (t.length) return t.join('; ');
  if (m.length) return m.join('; ');
  return null;
}

/* ── Core mapping (mirrors Python normalize_to_object_record) ─────────────
   Field paths confirmed against smk-field-map.json and live API 2026-06-26.
   ────────────────────────────────────────────────────────────────────────── */

function mapRecord(raw) {
  const titles      = raw.titles || [];
  const title       = titles.length ? titles[0].title : null;

  const production  = raw.production || [];
  const p0          = production[0] || {};
  const maker       = p0.creator       || null;
  const makerFn     = p0.creator_forename || null;
  const makerSn     = p0.creator_surname  || null;
  const makerBirth  = _parseYear(p0.creator_date_of_birth);
  const makerDeath  = _parseYear(p0.creator_date_of_death);
  const makerNat    = p0.creator_nationality || null;
  const creatorLref = p0.creator_lref || null;

  const prodDates    = raw.production_date || [];
  const pd0          = prodDates[0] || {};
  let dateDisplay    = pd0.period || null;
  const dateEarliest = _parseYear(pd0.start);
  const dateLatest   = _parseYear(pd0.end);
  if (!dateDisplay && dateEarliest) {
    dateDisplay = (dateEarliest === dateLatest || !dateLatest)
      ? String(dateEarliest) : `${dateEarliest}–${dateLatest}`;
  }

  const dims             = raw.dimensions || [];
  const heightCm         = _dimCm(dims, 'højde');
  const widthCm          = _dimCm(dims, 'bredde');
  const dimensionsDisplay = _dimDisplay(dims);
  const materialsDisplay  = _materialsDisplay(raw);

  const objNames    = raw.object_names || [];
  const objectType  = objNames.length ? objNames[0].name : null;

  const objNum      = raw.object_number || '';
  const today       = new Date().toISOString().substring(0, 10);

  // Acquisition provenance step
  const provenance = [];
  if (raw.acquisition_date) {
    provenance.push({
      step:        1,
      description: 'Acquired by Statens Museum for Kunst',
      date:        String(_parseYear(raw.acquisition_date) || ''),
      holder:      SMK_COLLECTION_NAME,
      type:        'acquisition',
      source:      `SRC-SMK-API-${objNum}`,
      source_note: 'Acquisition date per SMK Open API record',
    });
  }

  return {
    _source_adapter: 'SMKAdapter-JS v0.1',
    artbase_id:      `SMK-${objNum}`,

    object_id: {
      title,
      title_original:   title,
      object_type:      objectType,
      materials:        materialsDisplay,
      dimensions_display: dimensionsDisplay,
      height_cm:        heightCm,
      width_cm:         widthCm,
      date_display:     dateDisplay,
      date_earliest:    dateEarliest,
      date_latest:      dateLatest,
      maker_display_name: maker,
      maker_forename:   makerFn,
      maker_surname:    makerSn,
      maker_birth_year: makerBirth,
      maker_death_year: makerDeath,
      maker_nationality: makerNat,
      inventory_number: objNum,
      has_photograph:   raw.has_image || false,
    },

    location: {
      collection:       SMK_COLLECTION_NAME,
      collection_qid:   SMK_COLLECTION_QID,
      inventory_number: objNum,
      location_notes:   raw.current_location_name || null,
      department:       raw.responsible_department || null,
    },

    provenance,
    authority_links: extractAuthorityLinks(raw),
    rights:          extractRights(raw),
    media:           extractMedia(raw),

    sources: [extractSourceCitation(raw)],

    smk_raw: {
      id:                    raw.id || null,
      object_number:         objNum,
      frontend_url:          raw.frontend_url || `${SMK_OPEN_BASE}/${objNum}`,
      iiif_manifest:         raw.iiif_manifest || null,
      on_display:            raw.on_display || false,
      responsible_department: raw.responsible_department || null,
      creator_lref:          creatorLref,
      production_dates_notes: raw.production_dates_notes || [],
    },
  };
}

/* ── Authority links (mirrors Python extract_authority_links) ─────────────── */

function extractAuthorityLinks(raw) {
  const objNum     = raw.object_number || '';
  const frontendUrl = raw.frontend_url || `${SMK_OPEN_BASE}/${objNum}`;
  const today      = new Date().toISOString().substring(0, 10);
  const production = raw.production || [];
  const p0         = production[0] || {};

  return {
    wikidata: {
      scope:  'artwork_object',
      system: 'Wikidata',
      id:     null,
      uri:    null,
      status: 'search_needed',
      notes:  'Wikidata artwork QID not yet reconciled',
    },
    artbase_id: null,
    work_level: [
      {
        scope:          'artwork_object',
        system:         'SMK',
        id:             objNum,
        uri:            frontendUrl,
        api_uri:        raw.object_url || `${SMK_API_BASE}/art/?object_number=${objNum}`,
        status:         'approved_institutional_source',
        verified_date:  today,
        notes:          'Work-level authority record: SMK Open collection entry',
      }
    ],
    artist_smk: p0.creator ? {
      scope:  'artist_maker',
      system: 'SMK',
      id:     p0.creator_lref || null,
      label:  p0.creator,
      status: 'candidate_verify',
      notes:  'SMK internal person reference — reconcile to Wikidata / ULAN / RKD',
    } : null,
  };
}

/* ── Rights (mirrors Python extract_rights; never assumes CC0) ────────────── */

function extractRights(raw) {
  const pd         = raw.public_domain;
  const licenseUri = raw.rights || null;

  if (pd === true) {
    return {
      public_domain:    true,
      license:          licenseUri || 'https://creativecommons.org/publicdomain/mark/1.0/',
      copyright_status: 'public_domain',
      attribution:      null,
      source:           'SMK Open API public_domain field',
    };
  }
  if (pd === false) {
    return {
      public_domain:    false,
      license:          licenseUri,
      copyright_status: 'in_copyright',
      attribution:      `Image: © Statens Museum for Kunst. See ${raw.frontend_url || 'open.smk.dk'}`,
      source:           'SMK Open API public_domain field',
    };
  }
  return {
    public_domain:    null,
    license:          null,
    copyright_status: 'unknown',
    attribution:      null,
    source:           'SMK Open API — public_domain field absent; treated as restricted',
  };
}

/* ── Media (gated strictly on public_domain) ──────────────────────────────── */

function extractMedia(raw) {
  const records = [];
  const pd = raw.public_domain;

  if (raw.iiif_manifest) {
    records.push({ type: 'iiif_manifest', uri: raw.iiif_manifest, rights_verified: true });
  }

  if (pd !== true) return records;   // not confirmed public domain → stop here

  if (raw.image_thumbnail) {
    records.push({
      type:            'image_thumbnail',
      uri:             raw.image_thumbnail,
      rights_verified: true,
    });
  }
  if (raw.image_iiif_id) {
    records.push({
      type:            'image_iiif',
      uri:             raw.image_iiif_id,
      iiif_service:    raw.image_iiif_id,
      width:           raw.image_width  || null,
      height:          raw.image_height || null,
      rights_verified: true,
    });
  }
  return records;
}

/* ── Source citation ──────────────────────────────────────────────────────── */

function extractSourceCitation(raw) {
  const objNum   = raw.object_number || 'unknown';
  const today    = new Date().toISOString().substring(0, 10);
  const modified = raw.modified ? raw.modified.substring(0, 10) : null;
  return {
    source_id:        `SRC-SMK-API-${objNum}`,
    source_type:      'collection_api',
    title:            `SMK Open — ${objNum}`,
    publisher:        SMK_COLLECTION_NAME,
    url:              raw.object_url || `${SMK_API_BASE}/art/?object_number=${objNum}`,
    frontend_url:     raw.frontend_url || null,
    publication_date: modified,
    access_date:      today,
    license:          'https://creativecommons.org/licenses/by/4.0/',
    use_notes:        'SMK Open data is CC BY 4.0. Image reuse governed by per-object public_domain flag.',
  };
}

/* ── Rendering ────────────────────────────────────────────────────────────── */

function _esc(s) {
  if (s == null) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function _gap(label) {
  return `<div class="object-id-field missing">
    <span class="label">${label}</span>
    <span class="value">—</span>
  </div>`;
}

function _field(num, label, value, opts = {}) {
  if (!value && value !== 0) return _gap(label);
  const cls = opts.wide ? 'object-id-field wide' : 'object-id-field';
  const inner = opts.link
    ? `<a href="${_esc(opts.link)}" target="_blank" rel="noopener">${_esc(value)}</a>`
    : _esc(value);
  return `<div class="${cls}">
    <span class="num">${_esc(num)}</span>
    <span class="label">${_esc(label)}</span>
    <div class="value">${inner}</div>
  </div>`;
}

function renderPreview(passport, container) {
  const oid    = passport.object_id;
  const rights = passport.rights;
  const al     = passport.authority_links;
  const media  = passport.media || [];
  const smkRaw = passport.smk_raw || {};

  // Image
  const thumbnail = media.find(m => m.type === 'image_thumbnail');
  const imgHtml = rights.public_domain === true && thumbnail
    ? `<div class="hero-image">
        <div class="corner tl"></div><div class="corner tr"></div>
        <div class="corner bl"></div><div class="corner br"></div>
        <img src="${_esc(thumbnail.uri)}" alt="${_esc(oid.title)}" loading="lazy">
        <div class="img-caption">
          Image: public domain · CC0 ·
          <a href="${_esc(smkRaw.frontend_url)}" target="_blank" rel="noopener">SMK Open ↗</a>
        </div>
      </div>`
    : `<div class="hero-image no-image-wrap">
        <div class="no-image">
          ${rights.copyright_status === 'in_copyright'
            ? `<div>Image under copyright<br><a href="${_esc(smkRaw.frontend_url)}" target="_blank" rel="noopener">View at SMK Open ↗</a></div>`
            : '<div>No image</div>'}
        </div>
      </div>`;

  // Creator dates
  const makerDates = (oid.maker_birth_year || oid.maker_death_year)
    ? `b. ${oid.maker_birth_year || '?'}${oid.maker_death_year ? ` – d. ${oid.maker_death_year}` : ''}` : '';

  // Work-level authority link
  const wl = (al.work_level || [])[0];
  const artistSmk = al.artist_smk;

  // Rights display
  const rightsLabel = {
    public_domain: 'Public domain · CC0',
    in_copyright:  'In copyright · not redistributable',
    unknown:       'Rights unknown · treated as restricted',
  }[rights.copyright_status] || '—';

  const rightsClass = {
    public_domain: 'rights-ok',
    in_copyright:  'rights-copy',
    unknown:       'rights-unknown',
  }[rights.copyright_status] || '';

  container.innerHTML = `
  <div class="passport preview-passport">

    <!-- Header -->
    <div class="header">
      <div class="header-mark">
        <div class="issuer">Ars Accordia · SMK Source Preview</div>
        <div class="title">${_esc(oid.title) || '—'}</div>
        <div class="subtitle">
          ${_esc(oid.maker_display_name) || '—'}
          ${makerDates ? `· <span class="maker-dates">${_esc(makerDates)}</span>` : ''}
          · ${_esc(oid.date_display) || '—'}
        </div>
        <div class="colophon">
          ${_esc(SMK_COLLECTION_NAME)}
          · Inventory: <span class="mono">${_esc(oid.inventory_number)}</span>
          ${smkRaw.on_display ? '· On display' : ''}
        </div>
      </div>
      <div class="seal">
        <div class="seal-text">Live<br>Preview</div>
        <div class="seal-id">${_esc(oid.inventory_number)}</div>
        <div class="seal-year">SMK</div>
      </div>
    </div>

    <!-- Preview Banner -->
    <div class="preview-banner-inline">
      Live preview — this shows how Ars Accordia structures a public museum record.
      It is not a catalogued passport. No record is stored or scored.
      Catalogued passports are produced through Ars Accordia's reviewed pipeline.
    </div>

    <!-- Hero -->
    <div class="hero">
      ${imgHtml}
      <div class="tombstone">
        <div class="label">Work</div>
        <div class="work-title">${_esc(oid.title) || '—'}</div>
        <div class="work-artist">${_esc(oid.maker_display_name) || '—'}</div>
        ${makerDates ? `<div class="work-artist-dates">${_esc(makerDates)}${oid.maker_nationality ? ' · ' + _esc(oid.maker_nationality) : ''}</div>` : ''}
        <dl class="tombstone-grid">
          <dt>Date</dt><dd>${_esc(oid.date_display) || '—'}</dd>
          <dt>Medium</dt><dd>${_esc(oid.materials) || '—'}</dd>
          <dt>Dimensions</dt><dd>${_esc(oid.dimensions_display) || '—'}</dd>
          <dt>Type</dt><dd>${_esc(oid.object_type) || '—'}</dd>
          <dt>Collection</dt><dd>${_esc(SMK_COLLECTION_NAME)}</dd>
          <dt>Inventory</dt><dd class="mono">${_esc(oid.inventory_number)}</dd>
        </dl>
      </div>
    </div>

    <!-- §01 Identity -->
    <div class="section">
      <div class="section-header">
        <span class="section-number">§01</span>
        <span class="section-title">Identity</span>
        <span class="section-rubric">ICOM Object ID · nine categories</span>
      </div>
      <div class="object-id">
        ${_field('01', 'Type of object',          oid.object_type)}
        ${_field('02', 'Materials &amp; techniques', oid.materials)}
        ${_field('03', 'Measurements',             oid.dimensions_display)}
        ${_field('04', 'Inscriptions &amp; marks', null)}
        ${_field('05', 'Distinguishing features',  null)}
        ${_field('06', 'Title',                    oid.title, { wide: true })}
        ${_field('07', 'Subject',                  null)}
        ${_field('08', 'Date or period',           oid.date_display)}
        ${_field('09', 'Maker',                    oid.maker_display_name)}
      </div>
    </div>

    <!-- §02 Authority Links -->
    <div class="section">
      <div class="section-header">
        <span class="section-number">§02</span>
        <span class="section-title">Authority Links</span>
        <span class="section-rubric">Cross-references · scoped by entity type</span>
      </div>

      <div class="authority-group">
        <div class="authority-group-label">Identifies the artist</div>
        <div class="authorities">
          ${artistSmk
            ? `<div class="authority">
                <div class="auth-system">SMK — person record <span class="scope-badge">artist_maker</span></div>
                <div class="auth-id">${_esc(artistSmk.label)}</div>
                <div class="auth-label">SMK internal ref: <span class="mono">${_esc(artistSmk.id) || '—'}</span></div>
                <div class="auth-note">Reconcile to Wikidata / ULAN / RKD before publishing</div>
              </div>`
            : `<div class="authority missing"><div class="auth-label">No confirmed person-level authority yet — reconciliation needed</div></div>`}
        </div>
      </div>

      <div class="authority-group">
        <div class="authority-group-label">Identifies the work</div>
        <div class="authorities">
          ${wl
            ? `<a class="authority" href="${_esc(wl.uri)}" target="_blank" rel="noopener">
                <div class="auth-system">SMK Open <span class="scope-badge">artwork_object</span></div>
                <div class="auth-id">${_esc(wl.id)}</div>
                <div class="auth-label">Work-level authority record</div>
                <div class="auth-uri">${_esc(wl.uri)}</div>
              </a>`
            : _gap('Work-level authority link')}
          ${al.wikidata && al.wikidata.id
            ? `<a class="authority" href="${_esc(al.wikidata.uri)}" target="_blank" rel="noopener">
                <div class="auth-system">Wikidata <span class="scope-badge">artwork_object</span></div>
                <div class="auth-id">${_esc(al.wikidata.id)}</div>
                <div class="auth-label">Linked open data item</div>
                <div class="auth-uri">${_esc(al.wikidata.uri)}</div>
              </a>`
            : `<div class="authority candidate">
                <div class="auth-system">Wikidata <span class="scope-badge">artwork_object</span></div>
                <div class="auth-label">Not yet reconciled — lookup pending</div>
              </div>`}
        </div>
      </div>
    </div>

    <!-- §03 Rights -->
    <div class="section">
      <div class="section-header">
        <span class="section-number">§03</span>
        <span class="section-title">Rights</span>
        <span class="section-rubric">Per-object · read from SMK record · never assumed</span>
      </div>
      <div class="rights-block ${rightsClass}">
        <div class="rights-status-line">
          <span class="rights-dot"></span>
          <strong>${rightsLabel}</strong>
        </div>
        ${rights.license
          ? `<div class="rights-detail">License: <a href="${_esc(rights.license)}" target="_blank" rel="noopener">${_esc(rights.license)}</a></div>`
          : ''}
        ${rights.attribution
          ? `<div class="rights-detail rights-attribution">${_esc(rights.attribution)}</div>`
          : ''}
        <div class="rights-detail rights-source">Source: ${_esc(rights.source)}</div>
        ${smkRaw.frontend_url
          ? `<div class="rights-detail"><a href="${_esc(smkRaw.frontend_url)}" target="_blank" rel="noopener">View on SMK Open ↗</a></div>`
          : ''}
      </div>
    </div>

    <!-- Footer -->
    <div class="passport-footer">
      <div class="footer-cite">
        Source: SMK Open API · <span class="mono">SRC-SMK-API-${_esc(oid.inventory_number)}</span>
        · Retrieved ${new Date().toISOString().substring(0, 10)}
      </div>
      <div class="footer-note">
        Ars Accordia cross-references and cites SMK. This preview is not a catalogued passport.
      </div>
    </div>

  </div>`;
}

function renderSearchResults(results, container, onSelect) {
  if (!results.length) {
    container.innerHTML = '<p class="no-results">No results.</p>';
    return;
  }
  const rows = results.map(item => {
    const titles = item.titles || [];
    const title  = titles.length ? titles[0].title : '—';
    const prod   = item.production || [];
    const creator = prod.length ? prod[0].creator : '—';
    const dates  = item.production_date || [];
    const period = dates.length ? (dates[0].period || '—') : '—';
    const pd     = item.public_domain;
    const pdLabel = pd === true ? '<span class="pd-flag pd">PD</span>'
                  : pd === false ? '<span class="pd-flag copy">©</span>'
                  : '<span class="pd-flag unknown">?</span>';
    return `<div class="result-row" data-num="${_esc(item.object_number)}">
      <span class="result-num mono">${_esc(item.object_number)}</span>
      ${pdLabel}
      <span class="result-creator">${_esc(creator)}</span>
      <span class="result-sep">·</span>
      <span class="result-title">${_esc(title)}</span>
      <span class="result-sep">·</span>
      <span class="result-period">${_esc(period)}</span>
    </div>`;
  }).join('');
  container.innerHTML = `<div class="results-list">${rows}</div>`;
  container.querySelectorAll('.result-row').forEach(row => {
    row.addEventListener('click', () => onSelect(row.dataset.num));
  });
}

function renderError(msg, container) {
  container.innerHTML = `<div class="error-state">
    <div class="error-icon">—</div>
    <div class="error-msg">${_esc(msg)}</div>
  </div>`;
}

function renderLoading(container) {
  container.innerHTML = `<div class="loading-state">
    <div class="loading-bar"></div>
    <div class="loading-label">Fetching from SMK Open API…</div>
  </div>`;
}

/* ── Node export (for parity test) ───────────────────────────────────────── */

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    mapRecord,
    extractRights,
    extractMedia,
    extractAuthorityLinks,
    extractSourceCitation,
    fetchByObjectNumber,
    searchSMK,
    _dimCm,
    _dimDisplay,
    _parseYear,
    _materialsDisplay,
    SMK_COLLECTION_QID,
    SMK_COLLECTION_NAME,
  };
}
