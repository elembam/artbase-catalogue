# Ars Accordia — Standards Mapping

*How Ars Accordia fields map to Object ID, LIDO 1.1, EODEM, and Dublin Core.*

Version 0.1

---

## Object ID

Object ID defines nine categories of information that should be recorded for every
artwork to enable identification and recovery. The mapping below shows the Ars Accordia
canonical field for each category.

| Object ID category | Ars Accordia canonical field | Airtable field |
|---|---|---|
| 1. Type of object | `object_id.object_type` + `object_id.object_type_aat` | Object Type Label + AAT Object Type URI |
| 2. Materials and techniques | `object_id.materials` + `object_id.materials_aat` | Medium Display + AAT Medium URI |
| 3. Measurements | `object_id.dimensions_display`, `height_cm`, `width_cm`, `depth_cm` | Dimensions Display + individual dimension fields |
| 4. Inscriptions and markings | `object_id.inscriptions` | Inscriptions and Markings |
| 5. Distinguishing features | `object_id.distinguishing` | Distinguishing Features |
| 6. Title | `object_id.title` | Work Title |
| 7. Subject | `object_id.subject` + `iconography.iconclass_codes` | Subject Display + ICONCLASS Codes |
| 8. Date or period | `object_id.date_display`, `date_earliest`, `date_latest` | Date Display + Date Start + Date End |
| 9. Maker | `object_id.maker_id` → `CanonicalArtist` | Artist ID → Artists_Makers |

---

## LIDO 1.1

LIDO (Lightweight Information Describing Objects) is the primary exchange format for
cultural heritage object data. Ars Accordia targets LIDO 1.1.

### lido:lidoWrap / lido:lido

| LIDO element | Ars Accordia field | Notes |
|---|---|---|
| `lido:lidoRecID` | `artbase_canonical_id` | Format: `arsaccordia.com/p/AB7F3KQ2X1` |
| `lido:recordType` | fixed: `http://terminology.lido-schema.org/lido00141` | Item |

### lido:descriptiveMetadata

#### lido:objectClassificationWrap

| LIDO element | Ars Accordia field | Notes |
|---|---|---|
| `lido:objectWorkType/lido:conceptID` | `object_id.object_type_aat.uri` | Getty AAT URI |
| `lido:objectWorkType/lido:term` | `object_id.object_type_aat.label` | English preferred label |

#### lido:objectIdentificationWrap

| LIDO element | Ars Accordia field | Notes |
|---|---|---|
| `lido:titleWrap/lido:titleSet/lido:appellationValue` | `object_id.title` | `xml:lang` from `preferred_name_language` |
| `lido:inscriptionsWrap/lido:inscriptions/lido:inscriptionDescription` | `object_id.inscriptions` | |
| `lido:repositoryWrap/lido:repositorySet/lido:repositoryName` | `location.collection` | |
| `lido:repositoryWrap/lido:repositorySet/lido:workID` | `location.inventory_number` | `lido:type="inventory number"` |
| `lido:displayStateEditionWrap/lido:displayState` | `object_id.distinguishing` | For distinguishing features |

#### lido:eventWrap — creation event

| LIDO element | Ars Accordia field | Notes |
|---|---|---|
| `lido:event/lido:eventType/lido:term` | fixed: `Production` | |
| `lido:event/lido:eventActor/lido:actorInRole/lido:actor/lido:actorID` | `authority_links.ulan.uri` | Getty ULAN preferred |
| `lido:event/lido:eventActor/lido:actorInRole/lido:actor/lido:nameActorSet/lido:appellationValue` | `identity.preferred_name` | |
| `lido:event/lido:eventDate/lido:displayDate` | `object_id.date_display` | |
| `lido:event/lido:eventDate/lido:date/lido:earliestDate` | `object_id.date_earliest` | |
| `lido:event/lido:eventDate/lido:date/lido:latestDate` | `object_id.date_latest` | |
| `lido:event/lido:eventPlace/lido:place/lido:placeID` | `life.birth_place.tgn_uri` | Getty TGN URI |

#### lido:objectMeasurementsWrap

| LIDO element | Ars Accordia field | Notes |
|---|---|---|
| `lido:objectMeasurements/lido:measurementsSet/lido:measurementValue` (height) | `object_id.height_cm` | `lido:measurementUnit="cm"` |
| `lido:objectMeasurements/lido:measurementsSet/lido:measurementValue` (width) | `object_id.width_cm` | |
| `lido:objectMeasurements/lido:measurementsSet/lido:measurementValue` (depth) | `object_id.depth_cm` | omit if null |

#### lido:eventWrap — provenance events

Each `provenance[]` entry maps to a separate `lido:event` of type `Provenance`:

| LIDO element | Provenance field | Notes |
|---|---|---|
| `lido:event/lido:eventType/lido:term` | fixed: `Provenance` | |
| `lido:event/lido:eventActor/lido:actorInRole/lido:actor/lido:nameActorSet/lido:appellationValue` | `owner` | Redacted if `gdpr_public = false` |
| `lido:event/lido:eventDate/lido:displayDate` | `start_date` – `end_date` | |
| `lido:event/lido:eventPlace/lido:place/lido:namePlaceSet/lido:appellationValue` | `place` | |

### lido:administrativeMetadata

| LIDO element | Ars Accordia field | Notes |
|---|---|---|
| `lido:rightsWorkWrap/lido:rightsWork/lido:creditLine` | `location.collection` + rights statement | |
| `lido:recordWrap/lido:recordID` | `artbase_canonical_id` | |
| `lido:recordWrap/lido:recordType/lido:term` | fixed: `item` | |
| `lido:recordWrap/lido:recordSource/lido:legalBodyName` | fixed: `Ars Accordia / arsaccordia.com` | |
| `lido:recordWrap/lido:recordRights/lido:rightsType/lido:term` | `CC BY 4.0` | for published records |
| `lido:recordWrap/lido:recordInfoSet/lido:recordInfoLink` | `https://arsaccordia.com/p/{artbase_canonical_id}` | |

---

## EODEM (European Object Data Exchange Model)

EODEM is a constrained profile of LIDO 1.1, defining which elements are mandatory,
recommended, or optional. The mapping inherits everything from LIDO above, with these
additional constraints:

### EODEM-specific requirements

| Requirement | EODEM level | Ars Accordia handling |
|---|---|---|
| `lido:lidoRecID` must be a URI | Mandatory | Use `https://arsaccordia.com/p/{id}` |
| `lido:recordType` must use LIDO terminology | Mandatory | `http://terminology.lido-schema.org/lido00141` |
| At least one `lido:objectWorkType/lido:conceptID` with AAT URI | Mandatory | `object_id.object_type_aat.uri` |
| `lido:titleSet` with at least one `appellationValue` | Mandatory | `object_id.title` |
| `lido:repositorySet` with `workID` | Recommended | `location.inventory_number` |
| `lido:event` of type Production with at least actor or date | Recommended | maker + date |
| `lido:objectMeasurements` for at least height and width | Recommended | `height_cm`, `width_cm` |
| `lido:recordSource` with `legalBodyName` and `legalBodyWeblink` | Mandatory | Ars Accordia / arsaccordia.com |
| `lido:recordRights` | Recommended | CC BY 4.0 |

### EODEM validation

Validation requires:
1. XSD: `https://lido-schema.org/profiles/v1.1/lido-v1.1-profile-EODEM-v1.0.xsd`
2. Schematron rules: `exports/eodem/schematron/` — covers constraints not expressible in XSD

---

## Dublin Core

Used for legacy aggregators and as a minimal metadata floor.

| Dublin Core element | Ars Accordia field |
|---|---|
| `dc:title` | `object_id.title` |
| `dc:creator` | `identity.preferred_name` (of maker) |
| `dc:subject` | `object_id.subject` + ICONCLASS codes as keywords |
| `dc:description` | `object_id.materials` + dimensions + subject |
| `dc:publisher` | Ars Accordia / arsaccordia.com |
| `dc:contributor` | Cataloguer name (if public) |
| `dc:date` | `object_id.date_display` |
| `dc:type` | `object_id.object_type` |
| `dc:format` | `object_id.materials` |
| `dc:identifier` | `https://arsaccordia.com/p/{artbase_canonical_id}` |
| `dc:source` | `location.collection` + `location.inventory_number` |
| `dc:rights` | Rights statement per record |

---

## EDM (Europeana Data Model)

EDM is used for ingestion into Europeana. It extends Dublin Core with linked-data
constructs.

| EDM class/property | Ars Accordia mapping |
|---|---|
| `edm:ProvidedCHO` | The artwork record as a whole |
| `edm:isShownAt` | `https://arsaccordia.com/p/{artbase_canonical_id}` |
| `edm:isShownBy` | Primary image URL (if public) |
| `edm:provider` | Ars Accordia |
| `edm:dataProvider` | Collection / client name |
| `edm:rights` | `https://creativecommons.org/licenses/by/4.0/` |
| `owl:sameAs` | `object_id.wikidata.uri` (if present) |
| `skos:note` | `object_id.distinguishing`, provenance summary |

---

## Wikidata

Ars Accordia cross-references Wikidata but does not write to it without the Wikidata
contribution workflow (see `STRUCTURED_WIKIDATA_WORKFLOW.md`).

| Wikidata property | Ars Accordia field |
|---|---|
| P31 (instance of) | `object_id.object_type_aat` → Wikidata concept mapping |
| P170 (creator) | `object_id.maker_id` → `authority_links.wikidata.id` |
| P571 (inception) | `object_id.date_earliest` – `date_latest` |
| P186 (material) | `object_id.materials_aat` → Wikidata concept mapping |
| P2048 (height) | `object_id.height_cm` (convert to metres) |
| P2049 (width) | `object_id.width_cm` (convert to metres) |
| P276 (location) | `location.collection_qid` |
| P217 (inventory number) | `location.inventory_number` |
| P973 (described at URL) | `https://arsaccordia.com/p/{artbase_canonical_id}` |
| P18 (image) | Primary image URL (Wikimedia Commons link if available) |

---

## Getty vocabularies

| Vocabulary | Used for | Field |
|---|---|---|
| AAT (Art & Architecture Thesaurus) | Object type, materials, techniques, support | `object_type_aat`, `materials_aat` |
| ULAN (Union List of Artist Names) | Artist authority | `authority_links.ulan` |
| TGN (Thesaurus of Geographic Names) | Places — creation, birth, death, provenance | `tgn_uri` on PlaceField |

---

## ICONCLASS

ICONCLASS is a classification system for iconographic subjects.

| Field | Notes |
|---|---|
| `iconography.iconclass_codes` | Notation codes (e.g. `61B2`, `31A45`) |
| `iconography.iconclass_labels` | Human-readable labels in English |

ICONCLASS maps to LIDO `lido:eventWrap` as a `Subject` event with
`lido:subjectConcept/lido:conceptID` using the ICONCLASS URI scheme
(`http://iconclass.org/{notation}`).
