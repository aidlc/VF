"""
Pydantic models for MCS knowledge graph ontology.

5-layer design:
  System → Customer → Document → Chapter → Topic
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Entity nodes ─────────────────────────────────────────────────────────────

class Document(BaseModel):
    """Specification file (docx / pdf / pptx) with metadata."""
    document_id: Optional[str]       = Field(None, description="Unique document ID, e.g. DOC-SONY-001")
    customer: Optional[str]          = Field(None, description="Customer name, e.g. ソニー長崎")
    system_category: Optional[str]   = Field(None, description="Product line, e.g. HasMCS / MCS / MACS V2")
    file_type: Optional[str]         = Field(None, description="File extension: docx / pdf / pptx")


class Chapter(BaseModel):
    """A single chapter inside a specification document."""
    chapter_number: Optional[str]    = Field(None, description="Chapter number, e.g. 4.2.2")
    document_id: Optional[str]       = Field(None, description="Parent document ID")
    is_custom: Optional[bool]        = Field(None, description="True if this chapter is customer-specific")


class Topic(BaseModel):
    """Shared concept that anchors equivalent chapters across documents."""
    topic_id: Optional[str]          = Field(None, description="Canonical topic ID, e.g. MSG_S1_JOB_CREATE")
    description: Optional[str]       = Field(None, description="Human-readable topic description")


# ── Edge types ───────────────────────────────────────────────────────────────

class MapsTo(BaseModel):
    """Chapter —[MAPS_TO]→ Topic: links a chapter to its canonical concept."""
    confidence: Optional[float]      = Field(None, description="Mapping confidence, 0.0–1.0")
    mapped_at: Optional[datetime]    = Field(None, description="Timestamp when the mapping was created")


class Triggers(BaseModel):
    """Chapter —[TRIGGERS]→ Chapter: causal / logical dependency between chapters."""
    trigger_type: Optional[str]      = Field(None, description="Type of trigger, e.g. message_receive / state_change")
    description: Optional[str]       = Field(None, description="Description of the causal relationship")


class Compliance(BaseModel):
    """Chapter —[COMPLIANCE]→ Topic(Standard): reference to a shared standard."""
    standard_name: Optional[str]     = Field(None, description="Standard name, e.g. SEMI E82")
    compliance_level: Optional[str]  = Field(None, description="Compliance level, e.g. mandatory / optional")


# ── Ontology registries (passed directly to add_episode) ─────────────────────

ENTITY_TYPES: dict = {
    "Chapter":  Chapter,
    "Topic":    Topic,
    "Document": Document,
}

EDGE_TYPES: dict = {
    "MapsTo":     MapsTo,
    "Triggers":   Triggers,
    "Compliance": Compliance,
}

# Which edge types are valid between which entity pairs
EDGE_TYPE_MAP: dict[tuple[str, str], list[str]] = {
    ("Chapter",  "Topic"):   ["MapsTo", "Compliance"],
    ("Chapter",  "Chapter"): ["Triggers"],
    ("Entity",   "Entity"):  ["MapsTo"],
}
