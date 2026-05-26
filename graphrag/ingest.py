"""
Episode ingestion helpers for MCS specification documents.

Namespace key:  {system_category}__{customer}
Episode name:   {document_id}__{chapter_number}
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

from .models import ENTITY_TYPES, EDGE_TYPES, EDGE_TYPE_MAP


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class ChapterLink:
    target: str           # chapter number or file path
    relation: str         # "compliance" | "triggers"


@dataclass
class ChapterSpec:
    """All information about a single chapter extracted from YAML / LLM output."""
    document_id: str
    system_category: str
    customer: str
    chapter_number: str
    topic_id: str
    description: str
    links: list[ChapterLink]      = field(default_factory=list)
    is_custom: bool               = False
    reference_time: datetime      = field(default_factory=datetime.now)


# ── Episode body builder ──────────────────────────────────────────────────────

def _build_episode_body(spec: ChapterSpec) -> str:
    """Serialise a ChapterSpec to a plain-text episode body for Graphiti."""
    links_str = ", ".join(
        f"{{'target': '{lnk.target}', 'relation': '{lnk.relation}'}}"
        for lnk in spec.links
    )
    return (
        f"Document: {spec.document_id}\n"
        f"Customer: {spec.customer}\n"
        f"SystemCategory: {spec.system_category}\n"
        f"Chapter: {spec.chapter_number}\n"
        f"Topic: {spec.topic_id}\n"
        f"Description: {spec.description}\n"
        f"IsCustom: {spec.is_custom}\n"
        f"Links: [{links_str}]"
    )


# ── Public ingestion API ──────────────────────────────────────────────────────

async def add_chapter(graphiti: Graphiti, spec: ChapterSpec) -> None:
    """
    Ingest one chapter as a Graphiti episode.

    Namespace: {system_category}__{customer}
    """
    namespace   = f"{spec.system_category}__{spec.customer}"
    episode_name = f"{spec.document_id}__{spec.chapter_number}"

    await graphiti.add_episode(
        name=episode_name,
        episode_body=_build_episode_body(spec),
        source=EpisodeType.text,
        source_description=f"{spec.customer} {spec.system_category} 仕様書",
        reference_time=spec.reference_time,
        group_id=namespace,
        entity_types=ENTITY_TYPES,
        edge_types=EDGE_TYPES,
        edge_type_map=EDGE_TYPE_MAP,
    )


async def add_document(
    graphiti: Graphiti,
    chapters: list[ChapterSpec],
) -> None:
    """Ingest all chapters of a single document sequentially."""
    for spec in chapters:
        await add_chapter(graphiti, spec)


# ── YAML → ChapterSpec converter ──────────────────────────────────────────────

def from_yaml_mapping(
    document_id: str,
    system_category: str,
    customer: str,
    mapping: dict[str, Any],
) -> ChapterSpec:
    """
    Convert one entry from a YAML chapter_mappings list to a ChapterSpec.

    Expected mapping keys: chapter, topic_id, description, links, is_custom
    """
    links = [
        ChapterLink(target=lnk["target"], relation=lnk["relation"])
        for lnk in mapping.get("links", [])
    ]
    return ChapterSpec(
        document_id=document_id,
        system_category=system_category,
        customer=customer,
        chapter_number=mapping["chapter"],
        topic_id=mapping["topic_id"],
        description=mapping.get("description", ""),
        links=links,
        is_custom=mapping.get("is_custom", False),
    )
