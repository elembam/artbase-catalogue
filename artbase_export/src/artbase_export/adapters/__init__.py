"""
Collection source adapters — one interface, many sources.

Each adapter fetches from an authoritative collection API, normalises the
response to the canonical passport object model, extracts authority links with
scope, handles rights per-object, and cites the source (never Ars Accordia).

Current adapters:
    SMKAdapter     — Statens Museum for Kunst (api.smk.dk)

Planned:
    RijksmuseumAdapter, MetAdapter, EuropeanaAdapter, RoyalDanishCollectionAdapter, KunstindeksAdapter
"""

from .base import CollectionSourceAdapter
from .smk import SMKAdapter

__all__ = ["CollectionSourceAdapter", "SMKAdapter"]
