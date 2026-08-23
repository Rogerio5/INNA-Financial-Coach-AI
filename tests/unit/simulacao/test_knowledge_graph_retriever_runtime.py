from __future__ import annotations

from concurrent.futures import (
    ThreadPoolExecutor,
)

import src.knowledge_graph.retriever as retriever_module


class FakeGraphRetriever:
    create_calls = 0
    close_calls = 0

    @classmethod
    def from_environment(cls):
        cls.create_calls += 1
        return cls()

    def close(self) -> None:
        type(self).close_calls += 1


def _install_fake(monkeypatch) -> None:
    retriever_module.reset_shared_graph_retriever()

    FakeGraphRetriever.create_calls = 0
    FakeGraphRetriever.close_calls = 0

    monkeypatch.setattr(
        retriever_module,
        "GraphKnowledgeRetriever",
        FakeGraphRetriever,
    )


def test_shared_retriever_reuses_same_instance(
    monkeypatch,
) -> None:
    _install_fake(monkeypatch)

    try:
        first = (
            retriever_module.get_shared_graph_retriever()
        )
        second = (
            retriever_module.get_shared_graph_retriever()
        )

        assert first is second
        assert FakeGraphRetriever.create_calls == 1
    finally:
        retriever_module.reset_shared_graph_retriever()


def test_reset_closes_and_recreates_shared_retriever(
    monkeypatch,
) -> None:
    _install_fake(monkeypatch)

    try:
        first = (
            retriever_module.get_shared_graph_retriever()
        )

        retriever_module.reset_shared_graph_retriever()

        assert FakeGraphRetriever.close_calls == 1

        second = (
            retriever_module.get_shared_graph_retriever()
        )

        assert second is not first
        assert FakeGraphRetriever.create_calls == 2
    finally:
        retriever_module.reset_shared_graph_retriever()


def test_shared_retriever_initialization_is_thread_safe(
    monkeypatch,
) -> None:
    _install_fake(monkeypatch)

    try:
        with ThreadPoolExecutor(
            max_workers=8,
        ) as executor:
            futures = [
                executor.submit(
                    retriever_module.get_shared_graph_retriever
                )
                for _ in range(16)
            ]

            instances = [
                future.result()
                for future in futures
            ]

        assert len(
            {
                id(instance)
                for instance in instances
            }
        ) == 1

        assert FakeGraphRetriever.create_calls == 1
    finally:
        retriever_module.reset_shared_graph_retriever()
