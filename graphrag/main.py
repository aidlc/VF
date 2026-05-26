"""
MCS GraphRAG — demo entry point.

Usage:
    python -m graphrag.main ingest    # load sample YAML data
    python -m graphrag.main search    # run sample queries
    python -m graphrag.main diff      # cross-customer comparison
"""
from __future__ import annotations

import asyncio
import sys
import yaml
from pathlib import Path
from datetime import datetime

from .client import init_graphiti
from .ingest import add_document, from_yaml_mapping
from .search import search_spec, search_nodes, diff_customers


# ── Sample YAML (mirrors the design document example) ────────────────────────

SAMPLE_YAML = """
document_id: "DOC-SONY-001"
system_category: "HasMCS"
customer: "ソニー長崎"

chapter_mappings:
  - chapter: "4.2.2"
    topic_id: "MSG_S1_JOB_CREATE"
    description: "Transport Job Create Request (S1) の処理仕様"
    links:
      - target: "COMMON/SEMI/E82.pdf"
        relation: "compliance"
      - target: "8.3"
        relation: "triggers"
    is_custom: true

  - chapter: "8.3"
    topic_id: "CTRL_JOB_EXEC"
    description: "搬送ジョブ実行制御ロジック"
    links:
      - target: "8.10"
        relation: "triggers"
    is_custom: false

  - chapter: "8.10"
    topic_id: "ERR_TRANSPORT_FAILOVER"
    description: "代替搬送・エラーリカバリ処理"
    links: []
    is_custom: true
"""

SAMPLE_YAML_JDI = """
document_id: "DOC-JDI-001"
system_category: "HasMCS"
customer: "JDI茂原"

chapter_mappings:
  - chapter: "4.2.2"
    topic_id: "MSG_S1_JOB_CREATE"
    description: "Transport Job Create (S1) — JDI実装"
    links:
      - target: "COMMON/SEMI/E82.pdf"
        relation: "compliance"
      - target: "8.5"
        relation: "triggers"
    is_custom: false

  - chapter: "8.5"
    topic_id: "CTRL_JOB_EXEC"
    description: "搬送ジョブ実行制御（JDI標準実装）"
    links: []
    is_custom: false
"""


# ── Ingest command ────────────────────────────────────────────────────────────

async def cmd_ingest() -> None:
    print("Initialising Graphiti …")
    g = await init_graphiti()

    try:
        for raw_yaml in [SAMPLE_YAML, SAMPLE_YAML_JDI]:
            meta = yaml.safe_load(raw_yaml)
            chapters = [
                from_yaml_mapping(
                    document_id=meta["document_id"],
                    system_category=meta["system_category"],
                    customer=meta["customer"],
                    mapping=m,
                )
                for m in meta["chapter_mappings"]
            ]

            print(f"  Ingesting {meta['document_id']} ({meta['customer']}) …")
            await add_document(g, chapters)
            print(f"  ✓ {len(chapters)} chapters ingested.")

    finally:
        await g.close()


# ── Search command ────────────────────────────────────────────────────────────

async def cmd_search() -> None:
    g = await init_graphiti()

    try:
        query = "S1メッセージによる搬送ジョブ作成の処理フロー"
        print(f"\n[Edge search] {query}")
        results = await search_spec(g, query, "HasMCS", "ソニー長崎")
        for r in results:
            print(f"  • {r}")

        print(f"\n[Node search] {query}")
        nodes = await search_nodes(g, query, "HasMCS", "ソニー長崎")
        for n in nodes:
            print(f"  • {n}")

    finally:
        await g.close()


# ── Diff command ──────────────────────────────────────────────────────────────

async def cmd_diff() -> None:
    g = await init_graphiti()

    try:
        query = "S1メッセージ処理における顧客ごとの差異"
        print(f"\n[Cross-customer diff] {query}")
        diff = await diff_customers(
            g, query, "HasMCS", ["ソニー長崎", "JDI茂原"]
        )
        for customer, nodes in diff.items():
            print(f"\n  ── {customer} ({len(nodes)} nodes) ──")
            for n in nodes:
                print(f"    • {n}")

    finally:
        await g.close()


# ── Dispatch ─────────────────────────────────────────────────────────────────

COMMANDS = {
    "ingest": cmd_ingest,
    "search": cmd_search,
    "diff":   cmd_diff,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ingest"
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}. Available: {list(COMMANDS)}")
        sys.exit(1)
    asyncio.run(COMMANDS[cmd]())
