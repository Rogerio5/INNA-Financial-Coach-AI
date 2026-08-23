from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.knowledge_graph.config import (
    Neo4jCABundleMode,
    Neo4jSettings,
    load_neo4j_settings,
)
from src.knowledge_graph.exceptions import (
    KnowledgeGraphConfigurationError,
    KnowledgeGraphConnectionError,
)
from src.knowledge_graph.neo4j_client import Neo4jClient


def test_neo4j_settings_are_disabled_by_default() -> None:
    settings = load_neo4j_settings({})

    assert settings.enabled is False
    assert settings.uri == "neo4j://localhost:7687"
    assert settings.database == "neo4j"
    assert settings.password is None
    assert settings.ca_bundle_mode is Neo4jCABundleMode.SYSTEM


def test_enabled_neo4j_requires_password() -> None:
    with pytest.raises(KnowledgeGraphConfigurationError):
        load_neo4j_settings({"INNA_KNOWLEDGE_GRAPH_ENABLED": "true"})


def test_invalid_feature_flag_is_rejected() -> None:
    with pytest.raises(KnowledgeGraphConfigurationError):
        load_neo4j_settings({"INNA_KNOWLEDGE_GRAPH_ENABLED": "sometimes"})


def test_invalid_ca_bundle_mode_is_rejected() -> None:
    environment = {
        "INNA_KNOWLEDGE_GRAPH_ENABLED": "true",
        "NEO4J_URI": "neo4j+s://example.databases.neo4j.io",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "unit-test-secret",
        "NEO4J_DATABASE": "neo4j",
        "NEO4J_CA_BUNDLE_MODE": "trust-all",
    }

    with pytest.raises(KnowledgeGraphConfigurationError):
        load_neo4j_settings(environment)


def test_certifi_mode_requires_ca_verified_uri() -> None:
    environment = {
        "INNA_KNOWLEDGE_GRAPH_ENABLED": "true",
        "NEO4J_URI": "neo4j://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "unit-test-secret",
        "NEO4J_DATABASE": "neo4j",
        "NEO4J_CA_BUNDLE_MODE": "certifi",
    }

    with pytest.raises(KnowledgeGraphConfigurationError):
        load_neo4j_settings(environment)


def test_secret_is_not_exposed_in_model_repr() -> None:
    settings = load_neo4j_settings(
        {
            "INNA_KNOWLEDGE_GRAPH_ENABLED": "true",
            "NEO4J_URI": "neo4j://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "unit-test-secret",
            "NEO4J_DATABASE": "neo4j",
        }
    )

    assert "unit-test-secret" not in repr(settings)


@dataclass
class FakeDriver:
    verify_calls: int = 0
    close_calls: int = 0

    def verify_connectivity(self) -> None:
        self.verify_calls += 1

    def close(self) -> None:
        self.close_calls += 1


def _enabled_settings() -> Neo4jSettings:
    return load_neo4j_settings(
        {
            "INNA_KNOWLEDGE_GRAPH_ENABLED": "true",
            "NEO4J_URI": "neo4j://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "unit-test-secret",
            "NEO4J_DATABASE": "neo4j",
        }
    )


def _certifi_settings() -> Neo4jSettings:
    return load_neo4j_settings(
        {
            "INNA_KNOWLEDGE_GRAPH_ENABLED": "true",
            "NEO4J_URI": "neo4j+s://example.databases.neo4j.io",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "unit-test-secret",
            "NEO4J_DATABASE": "neo4j",
            "NEO4J_CA_BUNDLE_MODE": "certifi",
        }
    )


def test_client_reuses_single_driver_and_closes_it() -> None:
    fake_driver = FakeDriver()
    factory_calls: list[tuple[str, dict[str, object]]] = []

    def factory(uri: str, **kwargs: object) -> FakeDriver:
        factory_calls.append((uri, kwargs))
        return fake_driver

    client = Neo4jClient(_enabled_settings(), driver_factory=factory)

    first = client.connect()
    second = client.connect()
    client.verify_connectivity()

    assert first is fake_driver
    assert second is fake_driver
    assert len(factory_calls) == 1
    assert factory_calls[0][0] == "neo4j://localhost:7687"
    assert factory_calls[0][1]["auth"] == ("neo4j", "unit-test-secret")
    assert factory_calls[0][1]["connection_timeout"] == 5.0
    assert "encrypted" not in factory_calls[0][1]
    assert "trusted_certificates" not in factory_calls[0][1]
    assert fake_driver.verify_calls == 1
    assert client.connected is True

    client.close()

    assert fake_driver.close_calls == 1
    assert client.connected is False


def test_certifi_mode_uses_encryption_and_custom_ca() -> None:
    fake_driver = FakeDriver()
    factory_calls: list[tuple[str, dict[str, object]]] = []
    trust_calls: list[str] = []
    trust_marker = object()

    def factory(uri: str, **kwargs: object) -> FakeDriver:
        factory_calls.append((uri, kwargs))
        return fake_driver

    def trust_factory(path: str) -> object:
        trust_calls.append(path)
        return trust_marker

    client = Neo4jClient(
        _certifi_settings(),
        driver_factory=factory,
        trust_custom_cas_factory=trust_factory,
        certificate_path_factory=lambda: "C:/safe/cacert.pem",
    )

    client.connect()

    assert trust_calls == ["C:/safe/cacert.pem"]
    assert len(factory_calls) == 1

    uri, kwargs = factory_calls[0]

    assert uri == "neo4j://example.databases.neo4j.io"
    assert kwargs["auth"] == ("neo4j", "unit-test-secret")
    assert kwargs["connection_timeout"] == 5.0
    assert kwargs["encrypted"] is True
    assert kwargs["trusted_certificates"] is trust_marker


def test_certifi_mode_does_not_disable_certificate_verification() -> None:
    fake_driver = FakeDriver()
    captured_kwargs: dict[str, object] = {}

    def factory(uri: str, **kwargs: object) -> FakeDriver:
        captured_kwargs.update(kwargs)
        return fake_driver

    client = Neo4jClient(
        _certifi_settings(),
        driver_factory=factory,
        trust_custom_cas_factory=lambda _: object(),
        certificate_path_factory=lambda: "C:/safe/cacert.pem",
    )

    client.connect()

    assert captured_kwargs["encrypted"] is True
    assert "trusted_certificates" in captured_kwargs
    assert "trust" not in captured_kwargs


def test_disabled_client_refuses_connection() -> None:
    client = Neo4jClient(
        load_neo4j_settings({}),
        driver_factory=lambda **_: object(),
    )

    with pytest.raises(KnowledgeGraphConfigurationError):
        client.connect()


def test_connectivity_error_is_wrapped() -> None:
    class BrokenDriver(FakeDriver):
        def verify_connectivity(self) -> None:
            raise RuntimeError("provider detail")

    client = Neo4jClient(
        _enabled_settings(),
        driver_factory=lambda *args, **kwargs: BrokenDriver(),
    )

    with pytest.raises(KnowledgeGraphConnectionError) as exc_info:
        client.verify_connectivity()

    assert "provider detail" not in str(exc_info.value)