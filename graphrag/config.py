"""
Environment-based configuration for MCS GraphRAG.
All values can be overridden via environment variables.
"""
import os

# ── LiteLLM proxy ────────────────────────────────────────────────────────────
LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://localhost:10001/v1")
LITELLM_API_KEY  = os.getenv("LITELLM_MASTER_KEY", "muratec_llm_proxy")

# ── Models ───────────────────────────────────────────────────────────────────
MAIN_MODEL     = os.getenv("GRAPHITI_MAIN_MODEL",    "qwen3-5-2b")
SMALL_MODEL    = os.getenv("GRAPHITI_SMALL_MODEL",   "qwen3-5-2b")
EMBED_MODEL    = os.getenv("GRAPHITI_EMBED_MODEL",   "BAAI/bge-m3")
EMBED_DIM      = int(os.getenv("GRAPHITI_EMBED_DIM", "1024"))
RERANKER_MODEL = os.getenv("GRAPHITI_RERANKER_MODEL","BAAI/bge-reranker-v2-m3")

# ── Neo4j ────────────────────────────────────────────────────────────────────
NEO4J_URI      = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
NEO4J_USER     = os.getenv("NEO4J_USER",     "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
