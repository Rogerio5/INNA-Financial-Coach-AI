from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import json
import os
import py_compile
import re
import shutil
import sys

from pathlib import Path


EXPECTED_RAGAS_VERSION = "0.4.3"

PATCH_MARKER_START = "# INNA_RAGAS_0_4_3_VERTEXAI_COMPAT_START"

PATCH_MARKER_END = "# INNA_RAGAS_0_4_3_VERTEXAI_COMPAT_END"


LEGACY_IMPORT_PATTERN = re.compile(
    r"from langchain_community\.chat_models\.vertexai "
    r"import ChatVertexAI\s*\r?\n"
    r"from langchain_community\.llms import VertexAI"
)


PATCH_BLOCK = """# INNA_RAGAS_0_4_3_VERTEXAI_COMPAT_START
# Workaround versionado para o bug upstream do Ragas 0.4.3.
#
# O Ragas importava Vertex AI obrigatoriamente pelo caminho legado.
# A integração é opcional para a INNA, portanto:
# 1. tenta o pacote moderno;
# 2. tenta o caminho legado;
# 3. usa classes sentinela quando Vertex AI não está instalado.
try:
    from langchain_google_vertexai import ChatVertexAI, VertexAI
except ImportError:
    try:
        from langchain_community.chat_models.vertexai import ChatVertexAI
        from langchain_community.llms import VertexAI
    except ImportError:
        class ChatVertexAI:
            \"""Sentinela quando a integração ChatVertexAI não está instalada.\"""

        class VertexAI:
            \"""Sentinela quando a integração VertexAI não está instalada.\"""
# INNA_RAGAS_0_4_3_VERTEXAI_COMPAT_END"""


def sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_evaluation_venv() -> Path:
    configured = os.environ.get(
        "INNA_EVALUATION_VENV",
        "",
    ).strip()

    if not configured:
        raise RuntimeError("INNA_EVALUATION_VENV não foi definido.")

    expected = Path(configured).resolve()

    actual = Path(sys.prefix).resolve()

    if actual != expected:
        raise RuntimeError(
            "O patch só pode ser aplicado na "
            ".venv-evaluation. "
            f"esperado={expected} atual={actual}"
        )

    return expected


def locate_ragas_base() -> Path:
    spec = importlib.util.find_spec("ragas")

    if spec is None or spec.submodule_search_locations is None:
        raise RuntimeError("O pacote Ragas não foi localizado.")

    package_root = Path(next(iter(spec.submodule_search_locations)))

    base_path = package_root / "llms" / "base.py"

    if not base_path.exists():
        raise RuntimeError(f"Arquivo do Ragas não encontrado: {base_path}")

    return base_path


def main() -> int:
    evaluation_venv = require_evaluation_venv()

    installed_version = importlib.metadata.version("ragas")

    if installed_version != EXPECTED_RAGAS_VERSION:
        raise RuntimeError(
            "O patch foi preparado somente para "
            f"Ragas {EXPECTED_RAGAS_VERSION}. "
            f"Instalado={installed_version}"
        )

    backup_root_value = os.environ.get(
        "INNA_RAGAS_PATCH_BACKUP_DIR",
        "",
    ).strip()

    if backup_root_value:
        backup_root = Path(backup_root_value).resolve()
    else:
        backup_root = Path.cwd() / ".backups" / "ragas_0_4_3_vertexai_patch"

    backup_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    base_path = locate_ragas_base()

    source = base_path.read_text(encoding="utf-8")

    hash_before = sha256_file(base_path)

    backup_path = backup_root / "ragas_llms_base_before.py"

    if PATCH_MARKER_START in source:
        if PATCH_MARKER_END not in source:
            raise RuntimeError("Patch parcial detectado no Ragas.")

        patched = False

    else:
        matches = list(LEGACY_IMPORT_PATTERN.finditer(source))

        if len(matches) != 1:
            raise RuntimeError(
                "O contrato esperado do Ragas 0.4.3 "
                "não foi encontrado exatamente uma vez. "
                f"ocorrencias={len(matches)}"
            )

        shutil.copy2(
            base_path,
            backup_path,
        )

        patched_source, replacements = LEGACY_IMPORT_PATTERN.subn(
            PATCH_BLOCK,
            source,
            count=1,
        )

        if replacements != 1:
            raise RuntimeError("A substituição do import não ocorreu.")

        compile(
            patched_source,
            str(base_path),
            "exec",
        )

        base_path.write_text(
            patched_source,
            encoding="utf-8",
            newline="\n",
        )

        patched = True

    py_compile.compile(
        str(base_path),
        doraise=True,
    )

    final_source = base_path.read_text(encoding="utf-8")

    if PATCH_MARKER_START not in final_source or PATCH_MARKER_END not in final_source:
        raise RuntimeError("Os marcadores do patch não foram encontrados.")

    hash_after = sha256_file(base_path)

    manifest = {
        "patch": ("ragas_0_4_3_vertexai_import_compatibility"),
        "ragas_version": installed_version,
        "evaluation_venv": str(evaluation_venv),
        "target": str(base_path),
        "backup": (str(backup_path) if backup_path.exists() else ""),
        "patched_now": patched,
        "sha256_before": hash_before,
        "sha256_after": hash_after,
        "network_called": False,
        "llm_called": False,
    }

    manifest_path = backup_root / "ragas_patch_manifest.json"

    manifest_path.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"RAGAS_VERSION={installed_version}")

    print(f"RAGAS_BASE_PATH={base_path}")

    print(f"RAGAS_PATCH_APPLIED_NOW={patched}")

    print("RAGAS_PATCH_MARKERS_VALID=True")

    print(f"RAGAS_HASH_BEFORE={hash_before}")

    print(f"RAGAS_HASH_AFTER={hash_after}")

    print(f"PATCH_MANIFEST={manifest_path}")

    print("LIVE_API_CALLED=False")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
