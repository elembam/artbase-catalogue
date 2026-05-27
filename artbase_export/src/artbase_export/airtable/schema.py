"""
artbase_export/airtable/schema.py

Single source of truth for Airtable table and field names.
Matches the artwork_passport_airtable_starter_kit exactly.

When your Airtable field names change, update here — nowhere else.
"""


# ── Table names ────────────────────────────────────────────────────────────────

class Tables:
    COLLECTIONS         = "Collections"
    ARTISTS             = "Artists_Makers"
    ARTWORKS            = "Artworks"
    AUTHORITY_LINKS     = "Authority_Links"
    OBJECT_ID_CHECKLIST = "Object_ID_Checklist"
    PHOTOGRAPHY         = "Photography_Media"
    PROVENANCE          = "Provenance_Events"
    CONDITION           = "Condition_Conservation"
    SOURCES             = "Source_Documents"
    PASSPORT_ISSUES     = "Passport_Issues"
    IMPORTS             = "Imports"
    EXPORT_JOBS         = "Export_Jobs"
    CONTROLLED_LISTS    = "Controlled_Lists"
    FIELD_DICTIONARY    = "Field_Dictionary"


# ── Collections ────────────────────────────────────────────────────────────────

class CollectionFields:
    ID                  = "Collection ID"
    CLIENT_CODE         = "Client Code"
    CLIENT_NAME         = "Client Name"
    COLLECTION_NAME     = "Collection Name"
    COLLECTION_TYPE     = "Collection Type"
    DEFAULT_LANGUAGE    = "Default Language"
    DEFAULT_RIGHTS      = "Default Rights Statement"
    PRIVACY_DEFAULT     = "Privacy Default"
    CONTACT_NAME        = "Contact Name"
    CONTACT_EMAIL       = "Contact Email"
    SOURCE_SYSTEM       = "Source System Default"
    NOTES               = "Notes"


# ── Artists_Makers ─────────────────────────────────────────────────────────────

class ArtistFields:
    # Identity
    ID                  = "Artist ID"           # e.g. ART-0001
    DISPLAY_NAME        = "Display Name"         # practical/UI display
    PREFERRED_NAME      = "Preferred Name"       # scholarly preferred form
    SORT_NAME           = "Sort Name"            # Siliņš, Herberts
    BIRTH_YEAR          = "Birth Year"           # integer, not full date
    DEATH_YEAR          = "Death Year"           # integer
    BIRTH_PLACE         = "Birth Place"
    DEATH_PLACE         = "Death Place"
    NATIONALITY         = "Nationality/Culture"
    ROLES               = "Roles"                # semicolon-separated: painter; sculptor
    ATTRIBUTION_NOTES   = "Attribution Notes"

    # Authority IDs — stored directly in the artist row (not in Authority_Links)
    ULAN_ID             = "ULAN ID"
    ULAN_URI            = "ULAN URI"
    WIKIDATA_QID        = "Wikidata QID"
    WIKIDATA_URL        = "Wikidata URL"
    VIAF_ID             = "VIAF ID"
    ISNI                = "ISNI"
    ORCID               = "ORCID"
    RKD_ID              = "RKD Artist ID"
    OFFICIAL_WEBSITE    = "Official Website"
    SOURCE_URLS         = "Source URLs"          # semicolon-separated

    # Status and workflow
    LIVING_PERSON       = "Living Person?"       # Yes / No — GDPR flag
    NOTABILITY_STATUS   = "Notability Status"    # Established / Plausible / Insufficient
    WIKIDATA_STATUS     = "Wikidata Status"      # matched_existing / create_candidate / not_applicable
    REVIEW_STATUS       = "Review Status"        # Approved / Needs review / Draft
    LAST_CHECKED        = "Last Checked"
    NOTES               = "Notes"


# ── Artworks (= Passports) ─────────────────────────────────────────────────────

class ArtworkFields:
    # Identity and import tracking
    PASSPORT_ID         = "Passport ID"          # AP-2026-000001
    SOURCE_SYSTEM       = "Source System"        # Artwork Archive / CatalogIt / Manual
    SOURCE_RECORD_ID    = "Source Record ID"     # ID in the source CRM
    IMPORT_ID           = "Import ID"            # links to Imports table
    COLLECTION_ID       = "Collection ID"        # links to Collections
    CLIENT_CODE         = "Client Code"
    INVENTORY_NUMBER    = "Inventory Number"

    # Tombstone data (Object ID categories)
    WORK_TITLE          = "Work Title"
    ALTERNATE_TITLES    = "Alternate Titles"
    ARTIST_DISPLAY      = "Artist Display Name"
    ARTIST_ID           = "Artist ID"            # links to Artists_Makers
    ATTRIBUTION_QUALIFIER = "Attribution Qualifier"  # By / Attributed to / Studio of / etc.

    DATE_DISPLAY        = "Date Display"         # c. 1503–1519
    DATE_START          = "Date Start"           # numeric year
    DATE_END            = "Date End"             # numeric year

    OBJECT_TYPE_LABEL   = "Object Type Label"    # paintings / sculptures / etc.
    AAT_OBJECT_TYPE_URI = "AAT Object Type URI"

    MEDIUM_DISPLAY      = "Medium Display"       # oil paint on poplar panel
    AAT_MEDIUM_URI      = "AAT Medium URI"
    TECHNIQUE_DISPLAY   = "Technique Display"
    AAT_TECHNIQUE_URI   = "AAT Technique URI"
    SUPPORT_DISPLAY     = "Support Display"
    AAT_SUPPORT_URI     = "AAT Support URI"

    DIMENSIONS_DISPLAY  = "Dimensions Display"
    HEIGHT_CM           = "Height cm"
    WIDTH_CM            = "Width cm"
    DEPTH_CM            = "Depth cm"
    WEIGHT_KG           = "Weight kg"

    SUBJECT_DISPLAY     = "Subject Display"
    ICONCLASS_CODES     = "ICONCLASS Codes"      # semicolon-separated

    INSCRIPTIONS        = "Inscriptions and Markings"
    DISTINGUISHING      = "Distinguishing Features"
    CREATION_PLACE      = "Creation Place"
    TGN_CREATION_URI    = "TGN Creation Place URI"
    LOCATION_DISPLAY    = "Current Location Display"
    REPOSITORY          = "Repository / Collection"
    RIGHTS_STATEMENT    = "Rights Statement"

    # Visibility and status
    CONFIDENTIALITY     = "Confidentiality Level"  # Private / Client Portal / Public Site
    VISIBILITY          = "Passport Visibility"    # Private / Unlisted / Public — Unindexed / Public — Indexed
    STATUS              = "Passport Status"        # Draft / Review / Issued / Archived

    # Readiness dashboard fields (may be formulas or manually set)
    OBJECT_ID_READINESS = "Object ID Readiness"
    GETTY_STATUS        = "Getty Authority Status"
    ICONCLASS_STATUS    = "ICONCLASS Status"
    PROVENANCE_STATUS   = "Provenance Status"
    PHOTOGRAPHY_STATUS  = "Photography Status"
    LIDO_READY          = "LIDO Ready"
    EODEM_READY         = "EODEM Ready"

    PUBLIC_PASSPORT_URL = "Public Passport URL"
    PRIVATE_PASSPORT_URL= "Private Passport URL"

    # Cataloguing
    CREATED_DATE        = "Created Date"
    LAST_REVIEWED       = "Last Reviewed"
    REVIEWED_BY         = "Reviewed By"
    CATALOGUED_BY       = "Catalogued By"
    NOTES               = "Cataloguing Notes"


# ── Authority_Links ────────────────────────────────────────────────────────────
# Universal sidecar for all authority links: AAT terms, ICONCLASS,
# ULAN (works), TGN, Wikidata (works), VIAF (institutions), etc.

class AuthorityFields:
    ID                  = "Authority Link ID"
    PASSPORT_ID         = "Passport ID"          # links to Artworks
    ENTITY_TYPE         = "Entity Type"          # object_type / medium / person / place / subject / etc.
    LOCAL_FIELD         = "Local Field"          # which Artworks field this enriches
    LOCAL_LABEL         = "Local Label"          # the display value in that field
    AUTHORITY_SYSTEM    = "Authority System"     # Getty AAT / Getty ULAN / ICONCLASS / Wikidata / etc.
    AUTHORITY_ID        = "Authority ID"
    AUTHORITY_URI       = "Authority URI"
    PREFERRED_LABEL     = "Preferred Label"
    LANGUAGE            = "Language"
    CONFIDENCE          = "Confidence"           # High / Medium / Low
    REVIEW_STATUS       = "Review Status"        # Approved / Needs review / Candidate
    SOURCE_URL          = "Source URL"
    LAST_CHECKED        = "Last Checked"
    REVIEWED_BY         = "Reviewed By"
    NOTES               = "Notes"


# ── Object_ID_Checklist ────────────────────────────────────────────────────────

class ObjectIDFields:
    ID                  = "Checklist ID"
    PASSPORT_ID         = "Passport ID"
    TYPE_STATUS         = "Type of Object Status"
    MATERIALS_STATUS    = "Materials/Techniques Status"
    MEASUREMENTS_STATUS = "Measurements Status"
    INSCRIPTIONS_STATUS = "Inscriptions/Markings Status"
    DISTINGUISHING_STATUS = "Distinguishing Features Status"
    TITLE_STATUS        = "Title Status"
    SUBJECT_STATUS      = "Subject Status"
    DATE_STATUS         = "Date/Period Status"
    MAKER_STATUS        = "Maker Status"
    PHOTOGRAPH_STATUS   = "Primary Photograph Status"
    # Formula fields (add manually after import):
    READY               = "Object ID Ready?"
    SCORE               = "Readiness Score"
    MISSING             = "Missing Items"
    REVIEWED_BY         = "Reviewed By"
    LAST_REVIEWED       = "Last Reviewed"
    NOTES               = "Notes"


# ── Photography_Media ─────────────────────────────────────────────────────────

class PhotoFields:
    ID                  = "Media ID"
    PASSPORT_ID         = "Passport ID"
    VIEW_TYPE           = "View Type"    # front / verso / signature / inscription / damage / raking_light / in_situ
    MEDIA_ROLE          = "Media Role"   # primary / supplementary / conservation / archive
    FILE_NAME           = "File Name"
    FILE_URL            = "File URL"
    ATTACHMENT          = "Attachment Placeholder"
    CAPTURE_DATE        = "Capture Date"
    PHOTOGRAPHER        = "Photographer"
    RIGHTS_STATEMENT    = "Rights Statement"
    COLOUR_REF          = "Colour Reference Included?"
    RESOLUTION          = "Resolution Long Side px"
    FORMAT              = "Format"
    PUBLIC              = "Public?"
    REVIEW_STATUS       = "Review Status"
    NOTES               = "Notes"


# ── Provenance_Events ─────────────────────────────────────────────────────────

class ProvenanceFields:
    ID                  = "Provenance Event ID"
    PASSPORT_ID         = "Passport ID"
    SEQUENCE            = "Sequence"
    START_DATE          = "Start Date"
    END_DATE            = "End Date"
    OWNER               = "Owner / Holder"
    OWNER_ENTITY_ID     = "Owner Entity ID"
    MANNER              = "Manner of Acquisition"   # purchase / gift / inheritance / commission / etc.
    PLACE               = "Place"
    SOURCE_CITATION     = "Source Citation"
    SOURCE_DOC_ID       = "Source Document ID"
    CONFIDENCE          = "Confidence"              # High / Medium / Low
    IS_GAP              = "Is Gap?"
    WWII_STATUS         = "WWII 1933–1945 Check Status"
    GDPR_PUBLIC         = "GDPR Public?"
    PUBLIC_SUMMARY      = "Public Summary"
    PRIVATE_NOTES       = "Private Notes"


# ── Condition_Conservation ────────────────────────────────────────────────────

class ConditionFields:
    ID                  = "Condition Report ID"
    PASSPORT_ID         = "Passport ID"
    INSPECTION_DATE     = "Inspection Date"
    OBJECT_TYPE         = "Object Type"
    SUMMARY             = "Condition Summary"   # Excellent / Good / Fair / Poor
    NOTES               = "Condition Notes"
    TERMS_OBSERVED      = "Terms Observed"
    SEVERITY            = "Severity"
    PRIORITY            = "Conservation Priority"
    RECOMMENDED_ACTION  = "Recommended Action"
    REVIEWED_BY         = "Reviewed By"
    REPORT_URL          = "Report File URL"
    PUBLIC              = "Public?"
    PRIVATE_NOTES       = "Private Notes"


# ── Source_Documents ──────────────────────────────────────────────────────────

class SourceFields:
    ID                  = "Source Document ID"
    PASSPORT_ID         = "Passport ID"
    RELATED_ENTITY_ID   = "Related Entity ID"   # may be artist ID or passport ID
    DOCUMENT_TYPE       = "Document Type"
    CITATION            = "Citation"
    URL                 = "Source URL"
    ATTACHMENT          = "Attachment Placeholder"
    DOCUMENT_DATE       = "Document Date"
    RELIABILITY         = "Reliability"         # High / Medium / Low
    PUBLIC              = "Public?"
    GDPR_SENSITIVE      = "GDPR Sensitive?"
    NOTES               = "Notes"


# ── Passport_Issues ───────────────────────────────────────────────────────────
# Tracks each issued version of a passport with all output URLs.

class PassportIssueFields:
    ID                  = "Issue ID"
    PASSPORT_ID         = "Passport ID"
    VERSION             = "Version"
    ISSUE_DATE          = "Issue Date"
    VISIBILITY          = "Visibility"
    STATUS              = "Status"              # Draft / Issued / Superseded
    HTML_URL            = "HTML URL"
    PDF_URL             = "PDF URL"
    JSON_LD_URL         = "JSON-LD URL"
    LIDO_XML_URL        = "LIDO XML URL"
    EODEM_XML_URL       = "EODEM XML URL"
    VALIDATION_URL      = "Validation Report URL"
    DATA_HASH           = "Data Hash"
    ISSUED_BY           = "Issued By"
    PUBLIC_REGISTRY     = "Include in Public Registry?"
    REVIEW_NOTES        = "Review Notes"


# ── Imports ───────────────────────────────────────────────────────────────────

class ImportFields:
    ID                  = "Import ID"
    SOURCE_SYSTEM       = "Source System"
    CLIENT_CODE         = "Client Code"
    COLLECTION_ID       = "Collection ID"
    EXPORT_DATE         = "Export Date"
    FILE_NAME           = "File Name"
    FILE_HASH           = "File Hash"
    STATUS              = "Import Status"
    ROWS_IMPORTED       = "Rows Imported"
    RECORDS_CREATED     = "Records Created"
    RECORDS_UPDATED     = "Records Updated"
    OPERATOR            = "Operator"
    NOTES               = "Notes"


# ── Export_Jobs ───────────────────────────────────────────────────────────────

class ExportJobFields:
    ID                  = "Export Job ID"
    MODE                = "Export Mode"
    CLIENT_CODE         = "Client Code"
    COLLECTION_ID       = "Collection ID"
    CONFIG_VERSION      = "Config Version"
    OUTPUT_DIR          = "Output Directory / URL"
    STARTED_AT          = "Started At"
    COMPLETED_AT        = "Completed At"
    STATUS              = "Status"
    RECORDS_INCLUDED    = "Records Included"
    RECORDS_REJECTED    = "Records Rejected"
    VALIDATION_URL      = "Validation Report URL"
    OPERATOR            = "Operator"
    NOTES               = "Notes"


# ── Status controlled vocabularies ────────────────────────────────────────────

class ReviewStatus:
    APPROVED        = "Approved"
    NEEDS_REVIEW    = "Needs review"
    DRAFT           = "Draft"

class PassportStatus:
    DRAFT           = "Draft"
    REVIEW          = "Review"
    ISSUED          = "Issued"
    ARCHIVED        = "Archived"

class Visibility:
    PRIVATE             = "Private"
    CLIENT_PORTAL       = "Client Portal"
    PUBLIC_UNINDEXED    = "Public — Unindexed"
    PUBLIC_INDEXED      = "Public — Indexed"

class Confidence:
    HIGH    = "High"
    MEDIUM  = "Medium"
    LOW     = "Low"

class WikidataStatus:
    MATCHED     = "matched_existing"
    CANDIDATE   = "create_candidate"
    NOT_APPLICABLE = "not_applicable"
