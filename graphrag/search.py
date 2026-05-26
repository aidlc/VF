"""
Search helpers for MCS GraphRAG.

Provides:
  - search_spec()   : high-level edge/fact search (graphiti.search)
  - search_nodes()  : node-level hybrid search (graphiti._search + RRF)
  - diff_customers(): cross-customer comparison for the same topic
"""
from __future__ import annotations

from graphiti_core import Graphiti
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF


def _namespace(system_category: str, customer: str) -> str:
    return f"{system_category}__{customer}"


async def search_spec(
    graphiti: Graphiti,
    query: str,
    system_category: str,
    customer: str,
    num_results: int = 10,
) -> list:
    """
    Standard Graphiti edge search within a single customer namespace.

    Returns a list of EntityEdge results.
    """
    return await graphiti.search(
        query=query,
        group_id=_namespace(system_category, customer),
        num_results=num_results,
    )


async def search_nodes(
    graphiti: Graphiti,
    query: str,
    system_category: str,
    customer: str,
    limit: int = 10,
) -> list:
    """
    Node-level hybrid search (vector + BM25, RRF fusion) within one namespace.

    Returns a list of EntityNode results.
    """
    cfg = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
    cfg.limit = limit

    return await graphiti._search(
        query=query,
        group_id=_namespace(system_category, customer),
        config=cfg,
    )


async def diff_customers(
    graphiti: Graphiti,
    query: str,
    system_category: str,
    customers: list[str],
    limit: int = 5,
) -> dict[str, list]:
    """
    Cross-customer comparison: run the same node search across multiple namespaces.

    Returns { customer_name: [node_results] }.
    Useful for: "S1メッセージ処理における顧客ごとの差異は？"
    """
    results: dict[str, list] = {}
    for customer in customers:
        results[customer] = await search_nodes(
            graphiti, query, system_category, customer, limit=limit
        )
    return results
