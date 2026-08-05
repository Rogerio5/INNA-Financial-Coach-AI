from __future__ import annotations

import ast
import pprint
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

MODULES_PATH = ROOT / "src" / "platform_modules.py"
I18N_PATH = ROOT / "src" / "platform_modules_i18n.py"
MODULE_TEST_PATH = ROOT / "tests" / "unit" / "test_platform_modules.py"
OVERVIEW_TEST_PATH = ROOT / "tests" / "unit" / "test_platform_modules_overview.py"

BACKUP_DIRECTORY = (
    ROOT
    / ".migration_backups"
    / datetime.now().strftime("technology_batch_1_%Y%m%d_%H%M%S")
)


@dataclass(frozen=True, slots=True)
class TechnologyModuleSpec:
    """Dados necessários para registrar um módulo tecnológico."""

    module_id: str
    icon: str
    family: str
    integration_type: str
    description: str
    titles: dict[str, str]


BASE_LANGUAGES = (
    "pt",
    "en_us",
    "es",
    "fr",
    "de",
    "it",
    "ro",
    "ua",
    "ru",
    "sa",
)


MODULES: tuple[TechnologyModuleSpec, ...] = (
    TechnologyModuleSpec(
        module_id="knowledge_graph_semantic_ai",
        icon="🧠",
        family="AI_KNOWLEDGE_AGENTS",
        integration_type="hybrid",
        description=(
            "Grafos de conhecimento, ontologias, relações "
            "semânticas, entidades e raciocínio contextual "
            "para integrar dados e conhecimento empresarial."
        ),
        titles={
            "pt": "🧠 Knowledge Graph e IA Semântica",
            "en_us": "🧠 Knowledge Graph and Semantic AI",
            "es": "🧠 Knowledge Graph e IA Semántica",
            "fr": "🧠 Graphe de connaissances et IA sémantique",
            "de": "🧠 Wissensgraph und semantische KI",
            "it": "🧠 Knowledge Graph e IA semantica",
            "ro": "🧠 Graf de cunoștințe și IA semantică",
            "ua": "🧠 Граф знань і семантичний ШІ",
            "ru": "🧠 Граф знаний и семантический ИИ",
            "sa": "🧠 الرسم البياني المعرفي والذكاء الدلالي",
        },
    ),
    TechnologyModuleSpec(
        module_id="multimodal_ai",
        icon="🧬",
        family="AI_KNOWLEDGE_AGENTS",
        integration_type="hybrid",
        description=(
            "Processamento integrado de texto, imagens, "
            "áudio, vídeo, documentos e outros formatos "
            "por modelos de inteligência artificial."
        ),
        titles={
            "pt": "🧬 IA Multimodal",
            "en_us": "🧬 Multimodal AI",
            "es": "🧬 IA Multimodal",
            "fr": "🧬 IA multimodale",
            "de": "🧬 Multimodale KI",
            "it": "🧬 IA multimodale",
            "ro": "🧬 IA multimodală",
            "ua": "🧬 Мультимодальний ШІ",
            "ru": "🧬 Мультимодальный ИИ",
            "sa": "🧬 الذكاء الاصطناعي متعدد الوسائط",
        },
    ),
    TechnologyModuleSpec(
        module_id="voice_audio_speech_ai",
        icon="🎙️",
        family="AI_KNOWLEDGE_AGENTS",
        integration_type="api",
        description=(
            "Reconhecimento de voz, síntese de fala, "
            "transcrição, análise de áudio, identificação "
            "de intenção e interfaces conversacionais."
        ),
        titles={
            "pt": "🎙️ Voz, Áudio e Speech AI",
            "en_us": "🎙️ Voice, Audio and Speech AI",
            "es": "🎙️ Voz, Audio y Speech AI",
            "fr": "🎙️ Voix, audio et IA vocale",
            "de": "🎙️ Sprache, Audio und Speech AI",
            "it": "🎙️ Voce, audio e Speech AI",
            "ro": "🎙️ Voce, audio și Speech AI",
            "ua": "🎙️ Голос, аудіо та мовленнєвий ШІ",
            "ru": "🎙️ Голос, аудио и речевой ИИ",
            "sa": "🎙️ الصوت والتسجيل والذكاء الاصطناعي للكلام",
        },
    ),
    TechnologyModuleSpec(
        module_id="agent_process_orchestration",
        icon="🧩",
        family="AI_KNOWLEDGE_AGENTS",
        integration_type="internal",
        description=(
            "Orquestração de agentes, ferramentas, fluxos, "
            "processos empresariais, aprovações humanas, "
            "memória e execução coordenada de tarefas."
        ),
        titles={
            "pt": "🧩 Orquestração de Agentes e Processos",
            "en_us": "🧩 Agent and Process Orchestration",
            "es": "🧩 Orquestación de Agentes y Procesos",
            "fr": "🧩 Orchestration des agents et des processus",
            "de": "🧩 Orchestrierung von Agenten und Prozessen",
            "it": "🧩 Orchestrazione di agenti e processi",
            "ro": "🧩 Orchestrarea agenților și proceselor",
            "ua": "🧩 Оркестрація агентів і процесів",
            "ru": "🧩 Оркестрация агентов и процессов",
            "sa": "🧩 تنسيق الوكلاء والعمليات",
        },
    ),
    TechnologyModuleSpec(
        module_id="ai_model_agent_security",
        icon="🤖",
        family="AI_KNOWLEDGE_AGENTS",
        integration_type="hybrid",
        description=(
            "Proteção de modelos, agentes, ferramentas, "
            "prompts, contexto, bases RAG e permissões "
            "contra ataques, abusos e vazamentos."
        ),
        titles={
            "pt": "🤖 Segurança de IA, Modelos e Agentes",
            "en_us": "🤖 AI, Model and Agent Security",
            "es": "🤖 Seguridad de IA, Modelos y Agentes",
            "fr": "🤖 Sécurité de l'IA, des modèles et des agents",
            "de": "🤖 Sicherheit für KI, Modelle und Agenten",
            "it": "🤖 Sicurezza di IA, modelli e agenti",
            "ro": "🤖 Securitatea IA, modelelor și agenților",
            "ua": "🤖 Безпека ШІ, моделей і агентів",
            "ru": "🤖 Безопасность ИИ, моделей и агентов",
            "sa": "🤖 أمن الذكاء الاصطناعي والنماذج والوكلاء",
        },
    ),
    TechnologyModuleSpec(
        module_id="real_time_event_intelligence",
        icon="⚡",
        family="DATA_INTEGRATION_OPERATIONS",
        integration_type="hybrid",
        description=(
            "Processamento de eventos, streams, filas, "
            "telemetria e alertas em tempo real para "
            "decisões e automações operacionais."
        ),
        titles={
            "pt": "⚡ Inteligência de Eventos em Tempo Real",
            "en_us": "⚡ Real-Time Event Intelligence",
            "es": "⚡ Inteligencia de Eventos en Tiempo Real",
            "fr": "⚡ Intelligence des événements en temps réel",
            "de": "⚡ Echtzeit-Ereignisintelligenz",
            "it": "⚡ Intelligenza degli eventi in tempo reale",
            "ro": "⚡ Inteligența evenimentelor în timp real",
            "ua": "⚡ Аналітика подій у реальному часі",
            "ru": "⚡ Аналитика событий в реальном времени",
            "sa": "⚡ ذكاء الأحداث في الوقت الفعلي",
        },
    ),
    TechnologyModuleSpec(
        module_id="privacy_data_protection_lgpd",
        icon="🔐",
        family="SECURITY_PRIVACY_TRUST",
        integration_type="hybrid",
        description=(
            "Inventário de dados pessoais, consentimento, "
            "retenção, anonimização, solicitações de titulares "
            "e apoio à conformidade com a LGPD."
        ),
        titles={
            "pt": "🔐 Privacidade, Proteção de Dados e LGPD",
            "en_us": "🔐 Privacy, Data Protection and LGPD",
            "es": "🔐 Privacidad, Protección de Datos y LGPD",
            "fr": "🔐 Confidentialité, protection des données et LGPD",
            "de": "🔐 Datenschutz, Datensicherheit und LGPD",
            "it": "🔐 Privacy, protezione dei dati e LGPD",
            "ro": "🔐 Confidențialitate, protecția datelor și LGPD",
            "ua": "🔐 Приватність, захист даних і LGPD",
            "ru": "🔐 Конфиденциальность, защита данных и LGPD",
            "sa": "🔐 الخصوصية وحماية البيانات وقانون LGPD",
        },
    ),
    TechnologyModuleSpec(
        module_id="zero_trust_identity_access",
        icon="🧱",
        family="SECURITY_PRIVACY_TRUST",
        integration_type="hybrid",
        description=(
            "Zero Trust, IAM, autenticação multifator, "
            "SSO, controle de acesso, privilégios mínimos "
            "e identidades de usuários e serviços."
        ),
        titles={
            "pt": "🧱 Zero Trust, Identidade e Gestão de Acessos",
            "en_us": "🧱 Zero Trust, Identity and Access Management",
            "es": "🧱 Zero Trust, Identidad y Gestión de Accesos",
            "fr": "🧱 Zero Trust, identité et gestion des accès",
            "de": "🧱 Zero Trust, Identität und Zugriffsverwaltung",
            "it": "🧱 Zero Trust, identità e gestione degli accessi",
            "ro": "🧱 Zero Trust, identitate și managementul accesului",
            "ua": "🧱 Zero Trust, ідентичність і керування доступом",
            "ru": "🧱 Zero Trust, идентификация и управление доступом",
            "sa": "🧱 الثقة الصفرية وإدارة الهوية والوصول",
        },
    ),
    TechnologyModuleSpec(
        module_id="cryptography_confidential_computing",
        icon="🔏",
        family="SECURITY_PRIVACY_TRUST",
        integration_type="hybrid",
        description=(
            "Criptografia de dados, gestão de chaves, "
            "segredos, assinaturas, ambientes confidenciais "
            "e proteção durante o processamento."
        ),
        titles={
            "pt": "🔏 Criptografia e Computação Confidencial",
            "en_us": "🔏 Cryptography and Confidential Computing",
            "es": "🔏 Criptografía y Computación Confidencial",
            "fr": "🔏 Cryptographie et informatique confidentielle",
            "de": "🔏 Kryptografie und vertrauliches Computing",
            "it": "🔏 Crittografia e confidential computing",
            "ro": "🔏 Criptografie și calcul confidențial",
            "ua": "🔏 Криптографія та конфіденційні обчислення",
            "ru": "🔏 Криптография и конфиденциальные вычисления",
            "sa": "🔏 التشفير والحوسبة السرية",
        },
    ),
    TechnologyModuleSpec(
        module_id="software_supply_chain_security",
        icon="🧬",
        family="SECURITY_PRIVACY_TRUST",
        integration_type="hybrid",
        description=(
            "Proteção da cadeia de software, dependências, "
            "SBOM, imagens de contêiner, artefatos, pipelines "
            "CI/CD e componentes de terceiros."
        ),
        titles={
            "pt": "🧬 Segurança da Cadeia de Software",
            "en_us": "🧬 Software Supply Chain Security",
            "es": "🧬 Seguridad de la Cadena de Software",
            "fr": "🧬 Sécurité de la chaîne logicielle",
            "de": "🧬 Sicherheit der Software-Lieferkette",
            "it": "🧬 Sicurezza della catena del software",
            "ro": "🧬 Securitatea lanțului software",
            "ua": "🧬 Безпека ланцюга постачання ПЗ",
            "ru": "🧬 Безопасность цепочки поставок ПО",
            "sa": "🧬 أمن سلسلة توريد البرمجيات",
        },
    ),
    TechnologyModuleSpec(
        module_id="privacy_enhancing_technologies",
        icon="🕵️",
        family="SECURITY_PRIVACY_TRUST",
        integration_type="hybrid",
        description=(
            "Tecnologias de preservação de privacidade, "
            "dados sintéticos, aprendizado federado, "
            "privacidade diferencial e computação segura."
        ),
        titles={
            "pt": "🕵️ Tecnologias de Preservação de Privacidade",
            "en_us": "🕵️ Privacy-Enhancing Technologies",
            "es": "🕵️ Tecnologías de Preservación de la Privacidad",
            "fr": "🕵️ Technologies de protection de la vie privée",
            "de": "🕵️ Technologien zum Schutz der Privatsphäre",
            "it": "🕵️ Tecnologie per la tutela della privacy",
            "ro": "🕵️ Tehnologii de protejare a confidențialității",
            "ua": "🕵️ Технології збереження приватності",
            "ru": "🕵️ Технологии сохранения конфиденциальности",
            "sa": "🕵️ تقنيات تعزيز الخصوصية",
        },
    ),
    TechnologyModuleSpec(
        module_id="geoai_earth_observation",
        icon="🛰️",
        family="GEOSPATIAL_OBSERVATION",
        integration_type="api",
        description=(
            "Imagens de satélite, sensoriamento remoto, "
            "análise geoespacial, detecção de mudanças "
            "e inteligência territorial apoiada por IA."
        ),
        titles={
            "pt": "🛰️ GeoAI e Observação da Terra",
            "en_us": "🛰️ GeoAI and Earth Observation",
            "es": "🛰️ GeoAI y Observación de la Tierra",
            "fr": "🛰️ GeoAI et observation de la Terre",
            "de": "🛰️ GeoAI und Erdbeobachtung",
            "it": "🛰️ GeoAI e osservazione della Terra",
            "ro": "🛰️ GeoAI și observarea Pământului",
            "ua": "🛰️ GeoAI та спостереження Землі",
            "ru": "🛰️ GeoAI и наблюдение Земли",
            "sa": "🛰️ الذكاء الجغرافي ومراقبة الأرض",
        },
    ),
    TechnologyModuleSpec(
        module_id="gis_location_intelligence",
        icon="🗺️",
        family="GEOSPATIAL_OBSERVATION",
        integration_type="api",
        description=(
            "Mapas, geocodificação, roteamento, consultas "
            "espaciais, territórios, camadas geográficas "
            "e inteligência baseada em localização."
        ),
        titles={
            "pt": "🗺️ GIS e Inteligência de Localização",
            "en_us": "🗺️ GIS and Location Intelligence",
            "es": "🗺️ GIS e Inteligencia de Ubicación",
            "fr": "🗺️ SIG et intelligence de localisation",
            "de": "🗺️ GIS und Standortintelligenz",
            "it": "🗺️ GIS e intelligenza della posizione",
            "ro": "🗺️ GIS și inteligență de localizare",
            "ua": "🗺️ GIS та геолокаційна аналітика",
            "ru": "🗺️ GIS и геолокационная аналитика",
            "sa": "🗺️ نظم المعلومات الجغرافية وذكاء الموقع",
        },
    ),
    TechnologyModuleSpec(
        module_id="drones_aerial_intelligence",
        icon="🛸",
        family="GEOSPATIAL_OBSERVATION",
        integration_type="api",
        description=(
            "Integração de drones, imagens aéreas, missões, "
            "inspeções, mapeamento, monitoramento territorial "
            "e análise automatizada de dados capturados."
        ),
        titles={
            "pt": "🛸 Drones e Inteligência Aérea",
            "en_us": "🛸 Drones and Aerial Intelligence",
            "es": "🛸 Drones e Inteligencia Aérea",
            "fr": "🛸 Drones et intelligence aérienne",
            "de": "🛸 Drohnen und Luftbildintelligenz",
            "it": "🛸 Droni e intelligenza aerea",
            "ro": "🛸 Drone și inteligență aeriană",
            "ua": "🛸 Дрони та повітряна аналітика",
            "ru": "🛸 Дроны и воздушная аналитика",
            "sa": "🛸 الطائرات المسيرة والذكاء الجوي",
        },
    ),
    TechnologyModuleSpec(
        module_id="spatial_computing_augmented_reality",
        icon="🥽",
        family="GEOSPATIAL_OBSERVATION",
        integration_type="hybrid",
        description=(
            "Computação espacial, realidade aumentada, "
            "visualização imersiva, sobreposição de dados "
            "e experiências digitais vinculadas ao espaço."
        ),
        titles={
            "pt": "🥽 Computação Espacial e Realidade Aumentada",
            "en_us": "🥽 Spatial Computing and Augmented Reality",
            "es": "🥽 Computación Espacial y Realidad Aumentada",
            "fr": "🥽 Informatique spatiale et réalité augmentée",
            "de": "🥽 Räumliches Computing und erweiterte Realität",
            "it": "🥽 Spatial computing e realtà aumentata",
            "ro": "🥽 Calcul spațial și realitate augmentată",
            "ua": "🥽 Просторові обчислення та доповнена реальність",
            "ru": "🥽 Пространственные вычисления и дополненная реальность",
            "sa": "🥽 الحوسبة المكانية والواقع المعزز",
        },
    ),
    TechnologyModuleSpec(
        module_id="iot_edge_intelligence",
        icon="📡",
        family="PHYSICAL_AUTOMATION_SIMULATION",
        integration_type="hybrid",
        description=(
            "Sensores, dispositivos conectados, telemetria, "
            "protocolos IoT, processamento de borda e decisões "
            "próximas aos equipamentos físicos."
        ),
        titles={
            "pt": "📡 IoT e Inteligência de Borda",
            "en_us": "📡 IoT and Edge Intelligence",
            "es": "📡 IoT e Inteligencia de Borde",
            "fr": "📡 IoT et intelligence en périphérie",
            "de": "📡 IoT und Edge Intelligence",
            "it": "📡 IoT e intelligenza edge",
            "ro": "📡 IoT și inteligență la margine",
            "ua": "📡 IoT та периферійний інтелект",
            "ru": "📡 IoT и периферийный интеллект",
            "sa": "📡 إنترنت الأشياء وذكاء الحافة",
        },
    ),
    TechnologyModuleSpec(
        module_id="computer_vision_video_analytics",
        icon="👁️",
        family="PHYSICAL_AUTOMATION_SIMULATION",
        integration_type="hybrid",
        description=(
            "Análise de imagens e vídeos, detecção, "
            "classificação, rastreamento, inspeção visual "
            "e monitoramento inteligente em tempo real."
        ),
        titles={
            "pt": "👁️ Visão Computacional e Vídeo Analytics",
            "en_us": "👁️ Computer Vision and Video Analytics",
            "es": "👁️ Visión Computacional y Video Analytics",
            "fr": "👁️ Vision par ordinateur et analyse vidéo",
            "de": "👁️ Computer Vision und Videoanalyse",
            "it": "👁️ Visione artificiale e analisi video",
            "ro": "👁️ Viziune computerizată și analiză video",
            "ua": "👁️ Комп'ютерний зір і відеоаналітика",
            "ru": "👁️ Компьютерное зрение и видеоаналитика",
            "sa": "👁️ الرؤية الحاسوبية وتحليلات الفيديو",
        },
    ),
    TechnologyModuleSpec(
        module_id="digital_twins_simulation",
        icon="🏭",
        family="PHYSICAL_AUTOMATION_SIMULATION",
        integration_type="hybrid",
        description=(
            "Representações digitais de ativos, ambientes "
            "e processos para simulação, monitoramento, "
            "previsão e otimização operacional."
        ),
        titles={
            "pt": "🏭 Gêmeos Digitais e Simulação",
            "en_us": "🏭 Digital Twins and Simulation",
            "es": "🏭 Gemelos Digitales y Simulación",
            "fr": "🏭 Jumeaux numériques et simulation",
            "de": "🏭 Digitale Zwillinge und Simulation",
            "it": "🏭 Gemelli digitali e simulazione",
            "ro": "🏭 Gemeni digitali și simulare",
            "ua": "🏭 Цифрові двійники та моделювання",
            "ru": "🏭 Цифровые двойники и моделирование",
            "sa": "🏭 التوائم الرقمية والمحاكاة",
        },
    ),
    TechnologyModuleSpec(
        module_id="robotics_autonomous_systems",
        icon="🤖",
        family="PHYSICAL_AUTOMATION_SIMULATION",
        integration_type="hybrid",
        description=(
            "Robôs, máquinas autônomas, planejamento de "
            "tarefas, percepção, controle, integração com "
            "sensores e supervisão humana."
        ),
        titles={
            "pt": "🤖 Robótica e Sistemas Autônomos",
            "en_us": "🤖 Robotics and Autonomous Systems",
            "es": "🤖 Robótica y Sistemas Autónomos",
            "fr": "🤖 Robotique et systèmes autonomes",
            "de": "🤖 Robotik und autonome Systeme",
            "it": "🤖 Robotica e sistemi autonomi",
            "ro": "🤖 Robotică și sisteme autonome",
            "ua": "🤖 Робототехніка та автономні системи",
            "ru": "🤖 Робототехника и автономные системы",
            "sa": "🤖 الروبوتات والأنظمة الذاتية",
        },
    ),
)


NEW_MODULE_IDS = {module.module_id for module in MODULES}


def require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")


def create_backups(paths: tuple[Path, ...]) -> None:
    BACKUP_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    for path in paths:
        require_file(path)

        destination = BACKUP_DIRECTORY / path.relative_to(ROOT)

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            path,
            destination,
        )


def source_offsets(
    source: str,
) -> list[int]:
    offsets = [0]

    for line in source.splitlines(
        keepends=True,
    ):
        offsets.append(offsets[-1] + len(line))

    return offsets


def node_span(
    source: str,
    node: ast.AST,
) -> tuple[int, int]:
    offsets = source_offsets(source)

    start = offsets[node.lineno - 1] + node.col_offset
    end = offsets[node.end_lineno - 1] + node.end_col_offset

    return start, end


def format_literal(
    value: Any,
) -> str:
    return pprint.pformat(
        value,
        width=79,
        sort_dicts=False,
        compact=False,
    )


def find_assignment(
    tree: ast.AST,
    variable_name: str,
) -> ast.Assign | ast.AnnAssign:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(
                isinstance(target, ast.Name) and target.id == variable_name
                for target in node.targets
            ):
                return node

        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == variable_name:
                return node

    raise RuntimeError(f"Atribuição não encontrada: {variable_name}")


def assignment_value(
    node: ast.Assign | ast.AnnAssign,
) -> ast.expr:
    value = node.value

    if value is None:
        raise RuntimeError("Atribuição sem valor.")

    return value


def render_platform_module(
    module: TechnologyModuleSpec,
) -> str:
    description_parts = [part.strip() for part in module.description.split(", ")]

    description_lines: list[str] = []

    current = ""

    for part in description_parts:
        candidate = part if not current else f"{current}, {part}"

        if len(candidate) <= 58:
            current = candidate
            continue

        if current:
            description_lines.append(current + ",")

        current = part

    if current:
        description_lines.append(current)

    rendered_description = "\n".join(
        f'            "{line} "'
        if index < len(description_lines) - 1
        else f'            "{line}"'
        for index, line in enumerate(description_lines)
    )

    return (
        "    PlatformModule(\n"
        f'        module_id="{module.module_id}",\n'
        f'        icon="{module.icon}",\n'
        "        category="
        "PlatformModuleCategory.TECHNOLOGY_CORE,\n"
        "        status=PlatformModuleStatus.PLANNED,\n"
        "        navigation_group_id=None,\n"
        f'        integration_type="{module.integration_type}",\n'
        "        description=(\n"
        f"{rendered_description}\n"
        "        ),\n"
        "        technology_family=(\n"
        f"            TechnologyFamily.{module.family}\n"
        "        ),\n"
        "    ),\n"
    )


def update_platform_modules() -> None:
    source = MODULES_PATH.read_text(
        encoding="utf-8",
    )

    missing_modules = tuple(
        module
        for module in MODULES
        if (f'module_id="{module.module_id}"' not in source)
    )

    if not missing_modules:
        print("TECHNOLOGY_BATCH_1_MODULES_ALREADY_PRESENT=OK")
        return

    sector_anchor = (
        '    PlatformModule(\n        module_id="pet_shops_veterinary_services",'
    )

    position = source.find(sector_anchor)

    if position == -1:
        raise RuntimeError("Âncora do primeiro módulo setorial não encontrada.")

    insertion = "".join(render_platform_module(module) for module in missing_modules)

    source = source[:position] + insertion + source[position:]

    MODULES_PATH.write_text(
        source,
        encoding="utf-8",
    )


def update_platform_module_translations() -> None:
    source = I18N_PATH.read_text(
        encoding="utf-8",
    )
    tree = ast.parse(source)

    assignment = find_assignment(
        tree,
        "PLATFORM_MODULE_TEXTS",
    )
    value_node = assignment_value(assignment)

    texts = ast.literal_eval(value_node)

    if not isinstance(texts, dict):
        raise TypeError("PLATFORM_MODULE_TEXTS não é um dicionário.")

    for language in BASE_LANGUAGES:
        language_texts = texts.get(language)

        if not isinstance(
            language_texts,
            dict,
        ):
            raise RuntimeError(f"Idioma ausente ou inválido: {language}")

        for module in MODULES:
            language_texts[module.module_id] = module.titles[language]

    value_start, value_end = node_span(
        source,
        value_node,
    )

    rendered_texts = format_literal(texts)

    source = source[:value_start] + rendered_texts + source[value_end:]

    I18N_PATH.write_text(
        source,
        encoding="utf-8",
    )


def update_named_string_set(
    path: Path,
    variable_name: str,
    new_values: set[str],
) -> bool:
    source = path.read_text(
        encoding="utf-8",
    )
    tree = ast.parse(source)

    assignment = find_assignment(
        tree,
        variable_name,
    )
    value_node = assignment_value(assignment)

    current_value = ast.literal_eval(value_node)

    if not isinstance(
        current_value,
        set,
    ):
        raise TypeError(f"{variable_name} não é um conjunto.")

    updated_value = set(current_value) | new_values

    if updated_value == current_value:
        return False

    value_start, value_end = node_span(
        source,
        value_node,
    )

    rendered = (
        "{\n" + "".join(f'    "{item}",\n' for item in sorted(updated_value)) + "}"
    )

    source = source[:value_start] + rendered + source[value_end:]

    path.write_text(
        source,
        encoding="utf-8",
    )

    return True


def update_planned_literal_sets(
    path: Path,
) -> None:
    source = path.read_text(
        encoding="utf-8",
    )
    tree = ast.parse(source)

    replacements: list[tuple[int, int, str]] = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.Assign,
        ):
            continue

        if len(node.targets) != 1:
            continue

        target = node.targets[0]

        if not isinstance(
            target,
            ast.Name,
        ):
            continue

        if "planned" not in target.id.lower():
            continue

        if not isinstance(
            node.value,
            ast.Set,
        ):
            continue

        try:
            current_value = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            continue

        if not isinstance(
            current_value,
            set,
        ):
            continue

        if not all(isinstance(item, str) for item in current_value):
            continue

        module_like_values = {item for item in current_value if "_" in item}

        if len(module_like_values) < 2:
            continue

        updated_value = current_value | NEW_MODULE_IDS

        if updated_value == current_value:
            continue

        start, end = node_span(
            source,
            node.value,
        )

        indentation = " " * node.col_offset

        rendered = (
            "{\n"
            + "".join(f'{indentation}    "{item}",\n' for item in sorted(updated_value))
            + indentation
            + "}"
        )

        replacements.append(
            (
                start,
                end,
                rendered,
            )
        )

    for start, end, replacement in sorted(
        replacements,
        reverse=True,
    ):
        source = source[:start] + replacement + source[end:]

    path.write_text(
        source,
        encoding="utf-8",
    )


def update_module_tests() -> None:
    update_named_string_set(
        MODULE_TEST_PATH,
        "EXPECTED_MODULE_IDS",
        NEW_MODULE_IDS,
    )

    update_planned_literal_sets(MODULE_TEST_PATH)

    source = MODULE_TEST_PATH.read_text(
        encoding="utf-8",
    )

    replacements = {
        ("assert len(technology_modules) == 7"): (
            "assert len(technology_modules) == 26"
        ),
        ("assert len(PLATFORM_MODULES) == 25"): ("assert len(PLATFORM_MODULES) == 44"),
        ("        TechnologyFamily.GEOSPATIAL_OBSERVATION,\n"): "",
        ("        TechnologyFamily.PHYSICAL_AUTOMATION_SIMULATION,\n"): "",
    }

    for old, new in replacements.items():
        source = source.replace(
            old,
            new,
        )

    MODULE_TEST_PATH.write_text(
        source,
        encoding="utf-8",
    )


def update_overview_tests() -> None:
    source = OVERVIEW_TEST_PATH.read_text(
        encoding="utf-8",
    )

    source = source.replace(
        ("PlatformModuleCategory.TECHNOLOGY_CORE: 7,"),
        ("PlatformModuleCategory.TECHNOLOGY_CORE: 26,"),
    )

    source = source.replace(
        "assert len(technology_cards) == 7",
        "assert len(technology_cards) == 26",
    )

    OVERVIEW_TEST_PATH.write_text(
        source,
        encoding="utf-8",
    )


def validate_specs() -> None:
    if len(MODULES) != 19:
        raise RuntimeError(
            f"O lote deveria conter exatamente 19 módulos, mas contém {len(MODULES)}."
        )

    module_ids = [module.module_id for module in MODULES]

    if len(module_ids) != len(set(module_ids)):
        raise RuntimeError("Existem IDs duplicados no lote.")

    for module in MODULES:
        if set(module.titles) != set(BASE_LANGUAGES):
            missing = set(BASE_LANGUAGES) - set(module.titles)
            extra = set(module.titles) - set(BASE_LANGUAGES)

            raise RuntimeError(
                "Traduções inválidas para "
                f"{module.module_id}. "
                f"Ausentes={sorted(missing)}; "
                f"Extras={sorted(extra)}"
            )

        if module.integration_type not in {
            "internal",
            "api",
            "hybrid",
        }:
            raise RuntimeError(
                "Tipo de integração inválido para "
                f"{module.module_id}: "
                f"{module.integration_type}"
            )


def validate_result() -> None:
    module_source = MODULES_PATH.read_text(
        encoding="utf-8",
    )

    missing_registry_ids = {
        module_id
        for module_id in NEW_MODULE_IDS
        if (f'module_id="{module_id}"' not in module_source)
    }

    if missing_registry_ids:
        raise RuntimeError(
            f"Módulos ausentes no registro: {sorted(missing_registry_ids)}"
        )

    i18n_source = I18N_PATH.read_text(
        encoding="utf-8",
    )
    tree = ast.parse(i18n_source)

    assignment = find_assignment(
        tree,
        "PLATFORM_MODULE_TEXTS",
    )
    texts = ast.literal_eval(assignment_value(assignment))

    for language in BASE_LANGUAGES:
        missing_translation_ids = NEW_MODULE_IDS - set(texts[language])

        if missing_translation_ids:
            raise RuntimeError(
                f"Traduções ausentes em {language}: {sorted(missing_translation_ids)}"
            )


def main() -> None:
    files = (
        MODULES_PATH,
        I18N_PATH,
        MODULE_TEST_PATH,
        OVERVIEW_TEST_PATH,
    )

    validate_specs()
    create_backups(files)

    print(f"BACKUP_DIRECTORY={BACKUP_DIRECTORY}")

    update_platform_modules()
    update_platform_module_translations()
    update_module_tests()
    update_overview_tests()
    validate_result()

    print("TECHNOLOGY_MODULES_BATCH_1_CREATED=OK")
    print(f"NEW_TECHNOLOGY_MODULES={len(MODULES)}")
    print("EXPECTED_TECHNOLOGY_TOTAL=26")
    print("EXPECTED_PLATFORM_TOTAL=44")


if __name__ == "__main__":
    main()
