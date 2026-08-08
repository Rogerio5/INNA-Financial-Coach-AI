from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import streamlit as st


_relationship_graph_component = st.components.v2.component(
    "inna-relationship-graph.inna_relationship_graph",
    html='<div class="inna-relationship-graph-host"></div>',
    js="index-*.js",
)


def relationship_graph(
    *,
    catalog: Mapping[str, Any],
    locale: str = "pt",
    key: str | None = None,
    height: int = 920,
) -> Any:
    """Renderiza o grafo profissional da arquitetura da INNA."""

    safe_height = max(
        680,
        min(
            int(height),
            1280,
        ),
    )

    return _relationship_graph_component(
        key=key,
        data={
            "catalog": dict(catalog),
            "locale": str(locale or "pt"),
            "height": safe_height,
        },
        height=safe_height,
    )


__all__ = [
    "relationship_graph",
]
