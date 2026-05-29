import os
import json, time, urllib.request, urllib.error, urllib.parse

TOKEN   = os.getenv("AIRTABLE_TOKEN", "")
BASE_ID = "appoyRXU3qxxKZcbp"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def api(method, path, body=None):
    url = f"https://api.airtable.com{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"  ERROR {e.code}: {e.read().decode()[:400]}")
        return None

def mk(table, fields):
    r = api("POST", f"/v0/{BASE_ID}/{urllib.parse.quote(table)}", {"fields": fields})
    if r:
        print(f"  ok {table}: {r['id']}")
    return r

print("1. Artist...")
a = mk("Artists_Makers", {
    "Artist ID": "ART-HERBERTS-SILINS-1926",
    "Preferred Name":     "Herberts Silins",
    "Display Name":       "Herberts Silins",
    "Sort Name":          "Silins, Herberts",
    "Nationality/Culture":"Latvian",
    "Birth Year":         "1926",
    "Death Year":         "2001",
    "Birth Place":        "Aizupes pagasts, Latvia",
    "Death Place":        "Riga, Latvia",
    "Roles":              "painter",
    "Wikidata QID":       "Q23054868",
    "VIAF ID":            "15148752166141201333",
    "Review Status":      "Draft",
    "Notes":              "Pilot record. Birth date conflict: Wikipedia 28 Aug vs Galerija Jekabs 25 Aug.",
})
aid = a["id"] if a else None
time.sleep(0.3)

print("2. Artwork...")
af = {
    "Passport ID": "AP-2026-000002",
    "Work Title":              "Juras noskana (Sea Mood)",
    "Date Display":            "1979",
    "Date Start":              "1979",
    "Date End":                "1979",
    "Medium Display":          "Oil on canvas",
    "Dimensions Display":      "81 x 81 cm",
    "Height cm":               "81",
    "Width cm":                "81",
    "Object Type Label":       "painting",
    "Subject Display":         "Seascape; open sea with atmospheric sky",
    "Repository / Collection": "Private collection",
    "Current Location Display":"Private collection; exact location confidential",
    "Passport Visibility":     "Private",
    "Passport Status":         "Draft",
    "Photography Status":      "Missing",
    "Cataloguing Notes":       "First real pilot artwork. Source: Galerija Jekabs catalogue.",
}
if aid:
    af["Artist"] = [aid]
w = mk("Artworks", af)
wid = w["id"] if w else None
time.sleep(0.3)

print("3. Object ID checklist...")
cf = {
    "Passport ID":                  "AP-2026-000002",
    "Type of Object Status":        "Complete",
    "Materials/Techniques Status":  "Complete",
    "Measurements Status":          "Complete",
    "Inscriptions/Markings Status": "Not Examined",
    "Distinguishing Features Status":"Not Examined",
    "Title Status":                 "Complete",
    "Subject Status":               "Complete",
    "Date/Period Status":           "Complete",
    "Maker Status":                 "Complete",
    "Primary Photograph Status":    "Missing",
    "Readiness Score":              "8",
    "Notes":                        "Photography needed. Inscriptions/features not examined.",
}
mk("Object_ID_Checklist", cf)
time.sleep(0.3)

print("4. Provenance stub...")
pf = {
    "Passport ID":      "AP-2026-000002",
    "Sequence":         "1",
    "Owner / Holder":   "Private collection",
    "Manner of Acquisition": "Unknown",
    "Confidence":       "Low",
    "Is Gap?":          "Yes",
    "GDPR Public?":     "No",
    "Private Notes":    "Date of acquisition not documented. Research needed.",
}
mk("Provenance_Events", pf)
print("Done.")
