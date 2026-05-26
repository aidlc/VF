"""
Graphiti client factory.
Reuses the verified build_graphiti() configuration as-is.
"""
from graphiti_core import Graphiti
from graphiti_core.llm_client import LLMConfig, OpenAIGenericClient
from graphiti_core.embedder import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.cross_encoder.client import LiteLLMRerankerClient

from . import config


def build_graphiti() -> Graphiti:
    """Return an initialized (but not yet indexed) Graphiti instance."""
    llm_config = LLMConfig(
        api_key=config.LITELLM_API_KEY,
        model=config.MAIN_MODEL,
        small_model=config.SMALL_MODEL,
        base_url=config.LITELLM_BASE_URL,
    )
    llm_client = OpenAIGenericClient(config=llm_config)

    embedder = OpenAIEmbedder(
        config=OpenAIEmbedderConfig(
            api_key=config.LITELLM_API_KEY,
            embedding_model=config.EMBED_MODEL,
            embedding_dim=config.EMBED_DIM,
            base_url=config.LITELLM_BASE_URL,
        )
    )

    cross_encoder = LiteLLMRerankerClient(
        base_url=config.LITELLM_BASE_URL,
        api_key=config.LITELLM_API_KEY,
        model=config.RERANKER_MODEL,
    )

    return Graphiti(
        config.NEO4J_URI,
        config.NEO4J_USER,
        config.NEO4J_PASSWORD,
        llm_client=llm_client,
        embedder=embedder,
        cross_encoder=cross_encoder,
    )


async def init_graphiti() -> Graphiti:
    """Build Graphiti and create indices/constraints (safe to call repeatedly)."""
    g = build_graphiti()
    await g.build_indices_and_constraints()
    return g
