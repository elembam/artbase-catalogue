"""
ulan_lib/sparql.py

Getty ULAN SPARQL query helpers.
Endpoint: http://vocab.getty.edu/sparql.json
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

SPARQL_ENDPOINT = "https://vocab.getty.edu/sparql"
USER_AGENT = "ArtBase/1.0 (https://github.com/elembam/artbase-catalogue)"
RATE_SLEEP = 1.05  # seconds between requests


def _sparql_query(query: str, retries: int = 1) -> dict:
    """Execute a SPARQL query against Getty's endpoint using POST."""
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/sparql-results+json"
    }
    data = urllib.parse.urlencode({"query": query}).encode()
    req = urllib.request.Request(SPARQL_ENDPOINT, data=data, headers=headers, method="POST")
    
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                time.sleep(5.0)
                continue
            # Print error response for debugging
            try:
                error_body = e.read().decode(errors="replace")
                print(f"SPARQL HTTP {e.code}: {error_body[:200]}")
            except:
                pass
            raise
    return {}


def fetch_ulan_person(ulan_id: str) -> Optional[dict]:
    """
    Fetch biographical data for a ULAN person.
    Returns dict with biography, roles, places, alternate names, etc.
    """
    ulan_uri = f"http://vocab.getty.edu/ulan/{ulan_id}"
    
    # Simpler query focusing on core fields
    query = f"""
PREFIX gvp: <http://vocab.getty.edu/ontology#>
PREFIX xl: <http://www.w3.org/2008/05/skos-xl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?biography ?roleLabel ?natLabel ?birthPlace ?deathPlace ?altName
WHERE {{
  <{ulan_uri}> foaf:focus ?person .
  
  OPTIONAL {{ <{ulan_uri}> gvp:biographyPreferred [ dct:description ?biography ] . }}
  
  OPTIONAL {{
    ?person schema:hasOccupation ?role .
    ?role gvp:prefLabelGVP [ xl:literalForm ?roleLabel ] .
    FILTER (lang(?roleLabel) = "en")
  }}
  
  OPTIONAL {{
    ?person schema:nationality ?nat .
    ?nat gvp:prefLabelGVP [ xl:literalForm ?natLabel ] .
    FILTER (lang(?natLabel) = "en")
  }}
  
  OPTIONAL {{
    ?person gvp:biographyPreferred [ schema:birthPlace [ skos:prefLabel ?birthPlace ] ] .
    FILTER (lang(?birthPlace) = "en")
  }}
  
  OPTIONAL {{
    ?person gvp:biographyPreferred [ schema:deathPlace [ skos:prefLabel ?deathPlace ] ] .
    FILTER (lang(?deathPlace) = "en")
  }}
  
  OPTIONAL {{
    <{ulan_uri}> xl:altLabel [ xl:literalForm ?altName ] .
  }}
}}
LIMIT 100
"""
    
    try:
        result = _sparql_query(query)
        time.sleep(RATE_SLEEP)
        return result
    except Exception as e:
        print(f"SPARQL query failed for {ulan_id}: {e}")
        return None


def parse_sparql_results(sparql_result: dict) -> dict:
    """
    Parse SPARQL JSON results into structured enrichment dict.
    """
    if not sparql_result or "results" not in sparql_result:
        return {}
    
    bindings = sparql_result["results"]["bindings"]
    if not bindings:
        return {}
    
    enriched = {}
    
    # Biography (take first)
    bio_vals = [b["biography"]["value"] for b in bindings if "biography" in b]
    if bio_vals:
        enriched["biography_note"] = bio_vals[0]
    
    # Roles (collect unique)
    roles = set()
    for b in bindings:
        if "roleLabel" in b:
            roles.add(b["roleLabel"]["value"])
    if roles:
        enriched["roles"] = sorted(list(roles))
    
    # Nationalities (collect unique)
    nats = set()
    for b in bindings:
        if "natLabel" in b:
            nats.add(b["natLabel"]["value"])
    if nats:
        enriched["nationalities"] = sorted(list(nats))
    
    # Birth place (take first)
    birth_vals = [b["birthPlace"]["value"] for b in bindings if "birthPlace" in b]
    if birth_vals:
        enriched["birth_place_ulan"] = birth_vals[0]
    
    # Death place (take first)
    death_vals = [b["deathPlace"]["value"] for b in bindings if "deathPlace" in b]
    if death_vals:
        enriched["death_place_ulan"] = death_vals[0]
    
    # Alternate names (collect unique)
    alt_names = set()
    for b in bindings:
        if "altName" in b:
            alt_names.add(b["altName"]["value"])
    if alt_names:
        enriched["alternate_names"] = sorted(list(alt_names))
    
    # Related people (collect unique by URI)
    related = {}
    for b in bindings:
        if "relatedPerson" in b and "relatedLabel" in b:
            uri = b["relatedPerson"]["value"]
            if uri not in related:
                # Extract ULAN ID from URI
                ulan_id = uri.split("/")[-1] if "/" in uri else uri
                related[uri] = {
                    "ulan_id": ulan_id,
                    "label": b["relatedLabel"]["value"],
                    "relationship": b.get("relationship", {}).get("value", "related")
                }
    if related:
        enriched["related_people"] = list(related.values())
    
    return enriched
