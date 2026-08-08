import cytoscape, { type Core } from "cytoscape";
import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";

import {
  graphText,
  normalizeGraphLocale,
  type GraphLocale,
} from "./i18n";

type GraphState = {
  selected_node_id: string | null;
  selected_module_id: string | null;
  view_mode: "overview" | "module";
};

type Capability = {
  id: string;
  title: string;
  description?: string;
  technologies?: string[];
  status?: string;
};

type Area = {
  id: string;
  title: string;
  description?: string;
  capabilities: Capability[];
  capability_count: number;
};

type PlatformModule = {
  id: string;
  title: string;
  icon?: string;
  description?: string;
  status?: string;
  category?: string;
  technology_family?: string;
  integration_type?: string;
  areas: Area[];
  area_count: number;
  capability_count: number;
  source_registries?: string[];
};

type Relationship = {
  id: string;
  source: string;
  target: string;
  type: string;
  label?: string;
  description?: string;
  source_registry?: string;
};

type Catalog = {
  schema_version: string;
  root: {
    id: string;
    title: string;
    icon?: string;
    description?: string;
    kind?: string;
  };
  modules: PlatformModule[];
  relationships: Relationship[];
  statistics: {
    module_count: number;
    relationship_count: number;
    explicit_relationship_count: number;
    skipped_relationship_count: number;
    area_count: number;
    capability_count: number;
    categories: Record<string, number>;
  };
};

type ComponentData = {
  catalog: Catalog;
  locale?: string;
  height?: number;
};

type ViewMode = "overview" | "module";

type GraphElement = {
  data: Record<string, unknown>;
  position?: { x: number; y: number };
};

type Instance = {
  root: HTMLDivElement;
  cy: Core;
  catalog: Catalog;
  moduleById: Map<string, PlatformModule>;
  selectedNodeId: string | null;
  selectedModuleId: string | null;
  viewMode: ViewMode;
  categoryFilter: string;
  searchTerm: string;
  showRelationships: boolean;
  fitZoom: number;
  zoomPercent: number;
  destroy: () => void;
};

let innaGraphLocale: GraphLocale = "pt";

const innaUi = (
  key: string,
): string =>
  graphText(
    innaGraphLocale,
    key,
  );

const instances: WeakMap<
  FrontendRendererArgs["parentElement"],
  Instance
> = new WeakMap();

const CATEGORY_LABELS: Record<string, string> = {
  business_solutions: "Soluções empresariais",
  platform_administration: "Administração da plataforma",
  sector_solutions: "Soluções setoriais",
  technology_core: "Núcleo tecnológico",
};

const CATEGORY_ORDER = [
  "technology_core",
  "business_solutions",
  "sector_solutions",
  "platform_administration",
];

const clamp = (value: number, minimum: number, maximum: number): number =>
  Math.max(minimum, Math.min(maximum, value));

const normalize = (value: string): string =>
  value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();

const categoryLabel = (category: string): string =>
  CATEGORY_LABELS[category] ??
  category
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());

const createElement = <K extends keyof HTMLElementTagNameMap>(
  tagName: K,
  className?: string,
  text?: string,
): HTMLElementTagNameMap[K] => {
  const element = document.createElement(tagName);

  if (className) {
    element.className = className;
  }

  if (text !== undefined) {
    element.textContent = text;
  }

  return element;
};

const appendBadge = (
  container: HTMLElement,
  text: string,
  tone = "default",
): void => {
  if (!text) {
    return;
  }

  const badge = createElement("span", `irg-badge irg-badge-${tone}`, text);
  container.appendChild(badge);
};

const appendMetric = (
  container: HTMLElement,
  value: string | number,
  label: string,
): void => {
  const metric = createElement("div", "irg-detail-metric");
  metric.appendChild(createElement("strong", undefined, String(value)));
  metric.appendChild(createElement("span", undefined, label));
  container.appendChild(metric);
};

const appendList = (
  container: HTMLElement,
  title: string,
  values: string[],
  emptyText: string,
): void => {
  const section = createElement("section", "irg-detail-section");
  section.appendChild(createElement("h4", undefined, title));

  if (values.length === 0) {
    section.appendChild(createElement("p", "irg-muted", emptyText));
  } else {
    const list = createElement("ul", "irg-detail-list");
    values.slice(0, 18).forEach((value) => {
      list.appendChild(createElement("li", undefined, value));
    });

    if (values.length > 18) {
      list.appendChild(
        createElement(
          "li",
          "irg-muted",
          `Mais ${values.length - 18} itens`,
        ),
      );
    }

    section.appendChild(list);
  }

  container.appendChild(section);
};

const escapeId = (value: string): string =>
  value.replace(/[^a-zA-Z0-9_-]+/g, "-");

const moduleMatches = (
  module: PlatformModule,
  categoryFilter: string,
  searchTerm: string,
): boolean => {
  if (categoryFilter !== "all" && module.category !== categoryFilter) {
    return false;
  }

  if (!searchTerm) {
    return true;
  }

  const searchTarget = normalize(
    [
      module.title,
      module.description ?? "",
      module.technology_family ?? "",
      module.integration_type ?? "",
      module.category ?? "",
    ].join(" "),
  );

  return searchTarget.includes(normalize(searchTerm));
};

const visibleModules = (instance: Instance): PlatformModule[] =>
  instance.catalog.modules.filter((module) =>
    moduleMatches(module, instance.categoryFilter, instance.searchTerm),
  );

const moduleRelationships = (
  instance: Instance,
  moduleId: string,
): Relationship[] =>
  instance.catalog.relationships.filter(
    (relationship) =>
      relationship.source_registry === "platform_technology_relationships" &&
      (relationship.source === moduleId || relationship.target === moduleId),
  );

const positionCategoryModules = (
  categoryIndex: number,
  categoryCount: number,
  modules: PlatformModule[],
): { category: { x: number; y: number }; modules: Map<string, { x: number; y: number }> } => {
  const categoryAngle =
    -Math.PI / 2 + (2 * Math.PI * categoryIndex) / Math.max(categoryCount, 1);
  const categoryRadius = 950;
  const categoryPosition = {
    x: Math.cos(categoryAngle) * categoryRadius,
    y: Math.sin(categoryAngle) * categoryRadius,
  };
  const positions = new Map<string, { x: number; y: number }>();
  const ringCapacities = [12, 18, 26, 34];
  let offset = 0;

  ringCapacities.forEach((capacity, ringIndex) => {
    const ringModules = modules.slice(offset, offset + capacity);
    offset += capacity;
    const radius = 250 + ringIndex * 175;

    ringModules.forEach((module, index) => {
      const angle =
        categoryAngle +
        (2 * Math.PI * index) / Math.max(ringModules.length, 1);
      positions.set(module.id, {
        x: categoryPosition.x + Math.cos(angle) * radius,
        y: categoryPosition.y + Math.sin(angle) * radius,
      });
    });
  });

  modules.slice(offset).forEach((module, index, remainingModules) => {
    const radius = 950;
    const angle =
      categoryAngle +
      (2 * Math.PI * index) / Math.max(remainingModules.length, 1);
    positions.set(module.id, {
      x: categoryPosition.x + Math.cos(angle) * radius,
      y: categoryPosition.y + Math.sin(angle) * radius,
    });
  });

  return {
    category: categoryPosition,
    modules: positions,
  };
};

const createOverviewElements = (instance: Instance): GraphElement[] => {
  const modules = visibleModules(instance);
  const grouped = new Map<string, PlatformModule[]>();

  modules.forEach((module) => {
    const category = module.category || "unknown";
    const group = grouped.get(category) ?? [];
    group.push(module);
    grouped.set(category, group);
  });

  const orderedCategories = Array.from(grouped.keys()).sort((left, right) => {
    const leftIndex = CATEGORY_ORDER.indexOf(left);
    const rightIndex = CATEGORY_ORDER.indexOf(right);
    return (leftIndex < 0 ? 999 : leftIndex) - (rightIndex < 0 ? 999 : rightIndex);
  });

  const elements: GraphElement[] = [
    {
      data: {
        id: instance.catalog.root.id,
        label: instance.catalog.root.title,
        kind: "platform",
        raw: instance.catalog.root,
      },
      position: { x: 0, y: 0 },
    },
  ];

  orderedCategories.forEach((category, categoryIndex) => {
    const categoryModules = grouped.get(category) ?? [];
    const positions = positionCategoryModules(
      categoryIndex,
      orderedCategories.length,
      categoryModules,
    );
    const categoryId = `category:${category}`;

    elements.push({
      data: {
        id: categoryId,
        label: categoryLabel(category),
        kind: "category",
        category,
        count: categoryModules.length,
      },
      position: positions.category,
    });

    elements.push({
      data: {
        id: `edge:${instance.catalog.root.id}:${categoryId}`,
        source: instance.catalog.root.id,
        target: categoryId,
        kind: "structure",
      },
    });

    categoryModules.forEach((module) => {
      elements.push({
        data: {
          id: module.id,
          label: `${module.icon ? `${module.icon} ` : ""}${module.title}`,
          kind: "module",
          category: module.category ?? "unknown",
          status: module.status ?? "unknown",
          raw: module,
        },
        position: positions.modules.get(module.id),
      });

      elements.push({
        data: {
          id: `edge:${categoryId}:${module.id}`,
          source: categoryId,
          target: module.id,
          kind: "structure",
        },
      });
    });
  });

  if (instance.showRelationships && instance.selectedModuleId) {
    const visibleIds = new Set(modules.map((module) => module.id));
    moduleRelationships(instance, instance.selectedModuleId).forEach(
      (relationship, index) => {
        if (!visibleIds.has(relationship.source) || !visibleIds.has(relationship.target)) {
          return;
        }

        elements.push({
          data: {
            id: `relationship:${escapeId(relationship.id)}:${index}`,
            source: relationship.source,
            target: relationship.target,
            label: relationship.label ?? relationship.type,
            kind: "relationship",
            raw: relationship,
          },
        });
      },
    );
  }

  return elements;
};

const createModuleElements = (instance: Instance): GraphElement[] => {
  const selectedModule = instance.selectedModuleId
    ? instance.moduleById.get(instance.selectedModuleId)
    : undefined;

  if (!selectedModule) {
    return createOverviewElements(instance);
  }

  const elements: GraphElement[] = [
    {
      data: {
        id: selectedModule.id,
        label: `${selectedModule.icon ? `${selectedModule.icon} ` : ""}${selectedModule.title}`,
        kind: "module-focus",
        category: selectedModule.category ?? "unknown",
        status: selectedModule.status ?? "unknown",
        raw: selectedModule,
      },
      position: { x: 0, y: 0 },
    },
  ];

  const areas = selectedModule.areas ?? [];
  const areaCount = Math.max(areas.length, 1);

  areas.forEach((area, areaIndex) => {
    const centerAngle = -Math.PI / 2 + (2 * Math.PI * areaIndex) / areaCount;
    const areaRadius = 360;
    const areaId = `area:${selectedModule.id}:${area.id}`;

    elements.push({
      data: {
        id: areaId,
        label: area.title,
        kind: "area",
        module_id: selectedModule.id,
        raw: area,
      },
      position: {
        x: Math.cos(centerAngle) * areaRadius,
        y: Math.sin(centerAngle) * areaRadius,
      },
    });

    elements.push({
      data: {
        id: `edge:${selectedModule.id}:${areaId}`,
        source: selectedModule.id,
        target: areaId,
        kind: "structure",
      },
    });

    const capabilities = area.capabilities ?? [];
    const capabilityCount = Math.max(capabilities.length, 1);
    const sectorWidth = (2 * Math.PI) / areaCount;
    const spread = Math.min(sectorWidth * 0.82, Math.PI / 2.4);

    capabilities.forEach((capability, capabilityIndex) => {
      const normalizedIndex =
        capabilityCount === 1
          ? 0.5
          : capabilityIndex / (capabilityCount - 1);
      const angle = centerAngle - spread / 2 + spread * normalizedIndex;
      const ring = capabilityIndex % 2;
      const radius = 650 + ring * 145;
      const capabilityId = `capability:${selectedModule.id}:${area.id}:${capability.id}`;

      elements.push({
        data: {
          id: capabilityId,
          label: capability.title,
          kind: "capability",
          module_id: selectedModule.id,
          area_id: area.id,
          raw: capability,
        },
        position: {
          x: Math.cos(angle) * radius,
          y: Math.sin(angle) * radius,
        },
      });

      elements.push({
        data: {
          id: `edge:${areaId}:${capabilityId}`,
          source: areaId,
          target: capabilityId,
          kind: "structure",
        },
      });
    });
  });

  const relationships = moduleRelationships(instance, selectedModule.id);
  const neighborIds: string[] = [];

  relationships.forEach((relationship) => {
    const neighborId =
      relationship.source === selectedModule.id
        ? relationship.target
        : relationship.source;

    if (
      neighborId !== selectedModule.id &&
      instance.moduleById.has(neighborId) &&
      !neighborIds.includes(neighborId)
    ) {
      neighborIds.push(neighborId);
    }
  });

  const visibleNeighborIds = neighborIds.slice(0, 18);

  visibleNeighborIds.forEach((neighborId, index) => {
    const neighbor = instance.moduleById.get(neighborId);

    if (!neighbor) {
      return;
    }

    const angle = -Math.PI / 2 + (2 * Math.PI * index) / Math.max(visibleNeighborIds.length, 1);
    const radius = 1080;

    elements.push({
      data: {
        id: `neighbor:${neighbor.id}`,
        module_id: neighbor.id,
        label: neighbor.title,
        kind: "neighbor",
        category: neighbor.category ?? "unknown",
        raw: neighbor,
      },
      position: {
        x: Math.cos(angle) * radius,
        y: Math.sin(angle) * radius,
      },
    });
  });

  relationships.forEach((relationship, index) => {
    const sourceId =
      relationship.source === selectedModule.id
        ? selectedModule.id
        : `neighbor:${relationship.source}`;
    const targetId =
      relationship.target === selectedModule.id
        ? selectedModule.id
        : `neighbor:${relationship.target}`;
    const neighborId =
      relationship.source === selectedModule.id
        ? relationship.target
        : relationship.source;

    if (!visibleNeighborIds.includes(neighborId)) {
      return;
    }

    elements.push({
      data: {
        id: `detail-relationship:${escapeId(relationship.id)}:${index}`,
        source: sourceId,
        target: targetId,
        label: relationship.label ?? relationship.type,
        kind: "relationship",
        raw: relationship,
      },
    });
  });

  return elements;
};

const stylesheet = [
  {
    selector: "node",
    style: {
      "font-family": "Inter, ui-sans-serif, system-ui, sans-serif",
      "font-size": 12,
      color: "#dbeafe",
      label: "data(label)",
      "text-wrap": "wrap",
      "text-max-width": 145,
      "text-valign": "center",
      "text-halign": "center",
      "background-color": "#1f2937",
      "border-width": 2,
      "border-color": "#475569",
      width: 82,
      height: 82,
      "overlay-opacity": 0,
    },
  },
  {
    selector: 'node[kind = "platform"]',
    style: {
      width: 170,
      height: 170,
      "font-size": 20,
      "font-weight": 800,
      "background-color": "#6d28d9",
      "border-width": 5,
      "border-color": "#c4b5fd",
      color: "#ffffff",
      "text-max-width": 135,
    },
  },
  {
    selector: 'node[kind = "category"]',
    style: {
      width: 150,
      height: 150,
      "font-size": 15,
      "font-weight": 800,
      "background-color": "#312e81",
      "border-width": 4,
      "border-color": "#a5b4fc",
      color: "#ffffff",
      "text-max-width": 118,
    },
  },
  {
    selector: 'node[kind = "module"]',
    style: {
      width: 108,
      height: 108,
      "font-size": 11,
      "font-weight": 650,
      "background-color": "#0c4a6e",
      "border-width": 3,
      "border-color": "#38bdf8",
      color: "#e0f2fe",
      "text-max-width": 94,
    },
  },
  {
    selector: 'node[kind = "module-focus"]',
    style: {
      width: 190,
      height: 190,
      "font-size": 18,
      "font-weight": 800,
      "background-color": "#6d28d9",
      "border-width": 5,
      "border-color": "#ddd6fe",
      color: "#ffffff",
      "text-max-width": 150,
    },
  },
  {
    selector: 'node[kind = "area"]',
    style: {
      width: 125,
      height: 125,
      "font-size": 13,
      "font-weight": 700,
      "background-color": "#0f4c5c",
      "border-color": "#22d3ee",
      "text-max-width": 105,
    },
  },
  {
    selector: 'node[kind = "capability"]',
    style: {
      width: 88,
      height: 88,
      "font-size": 10,
      "background-color": "#14532d",
      "border-color": "#4ade80",
      "text-max-width": 76,
    },
  },
  {
    selector: 'node[kind = "neighbor"]',
    style: {
      width: 96,
      height: 96,
      "font-size": 10,
      "background-color": "#3f2b0c",
      "border-color": "#f59e0b",
      "text-max-width": 82,
    },
  },
  {
    selector: "node:selected",
    style: {
      "border-width": 7,
      "border-color": "#f8fafc",
      "background-blacken": -0.15,
    },
  },
  {
    selector: "edge",
    style: {
      width: 2,
      "line-color": "#334155",
      "target-arrow-color": "#334155",
      "curve-style": "bezier",
      "target-arrow-shape": "none",
      opacity: 0.72,
    },
  },
  {
    selector: 'edge[kind = "structure"]',
    style: {
      width: 2.4,
      "line-color": "#334155",
      "target-arrow-shape": "none",
    },
  },
  {
    selector: 'edge[kind = "relationship"]',
    style: {
      width: 3.2,
      "line-color": "#f59e0b",
      "target-arrow-color": "#f59e0b",
      "target-arrow-shape": "triangle",
      "arrow-scale": 0.8,
      "curve-style": "unbundled-bezier",
      "control-point-distances": 45,
      "control-point-weights": 0.5,
      opacity: 0.9,
    },
  },
  {
    selector: "edge:selected",
    style: {
      width: 5,
      "line-color": "#fde68a",
      "target-arrow-color": "#fde68a",
    },
  },
];

const updateStatistics = (instance: Instance): void => {
  const statisticsContainer = instance.root.querySelector<HTMLElement>(".irg-stats");

  if (!statisticsContainer) {
    return;
  }

  statisticsContainer.textContent = "";
  const statistics = instance.catalog.statistics;
  const metrics = [
    [statistics.module_count, "módulos"],
    [statistics.area_count, "áreas"],
    [statistics.capability_count, "capacidades"],
    [statistics.explicit_relationship_count, "relações reais"],
  ];

  metrics.forEach(([value, label]) => {
    const metric = createElement("div", "irg-stat");
    metric.appendChild(createElement("strong", undefined, String(value)));
    metric.appendChild(createElement("span", undefined, String(label)));
    statisticsContainer.appendChild(metric);
  });
};

const renderEmptyDetails = (instance: Instance): void => {
  const panel = instance.root.querySelector<HTMLElement>(".irg-details");

  if (!panel) {
    return;
  }

  panel.textContent = "";
  panel.appendChild(createElement("div", "irg-detail-kicker", "MAPA DE ARQUITETURA"));
  panel.appendChild(createElement("h3", undefined, "Explore a INNA AI Platform"));
  panel.appendChild(
    createElement(
      "p",
      "irg-detail-description",
      "Selecione um módulo para visualizar finalidade, estrutura, dependências e módulos relacionados. Abra sua estrutura para navegar por áreas e capacidades.",
    ),
  );

  const metrics = createElement("div", "irg-detail-metrics");
  appendMetric(metrics, instance.catalog.statistics.module_count, "módulos");
  appendMetric(metrics, instance.catalog.statistics.relationship_count, "conexões");
  appendMetric(metrics, instance.catalog.statistics.capability_count, "capacidades");
  panel.appendChild(metrics);

  appendList(
    panel,
    "Como navegar",
    [
      "Clique em um módulo para destacar suas relações reais.",
      "Use Abrir estrutura para visualizar áreas e capacidades.",
      "Use a busca e o filtro de categoria para reduzir o mapa.",
      "Volte à visão geral a qualquer momento.",
    ],
    "",
  );
};

const renderDetailsForNode = (instance: Instance, node: any): void => {
  const panel = instance.root.querySelector<HTMLElement>(".irg-details");

  if (!panel) {
    return;
  }

  if (!node) {
    renderEmptyDetails(instance);
    return;
  }

  panel.textContent = "";
  const kind = String(node.data("kind") ?? "unknown");
  const raw = node.data("raw") as any;
  const label = String(node.data("label") ?? "Elemento");

  panel.appendChild(
    createElement(
      "div",
      "irg-detail-kicker",
      kind.replace(/-/g, " ").toUpperCase(),
    ),
  );
  panel.appendChild(createElement("h3", undefined, label));

  const badges = createElement("div", "irg-badges");

  if (kind === "platform") {
    appendBadge(badges, "Plataforma", "purple");
  } else if (kind === "category") {
    appendBadge(badges, categoryLabel(String(node.data("category") ?? "")), "blue");
  } else if (raw) {
    appendBadge(badges, categoryLabel(String(raw.category ?? "")), "blue");
    appendBadge(badges, String(raw.status ?? ""), "green");
    appendBadge(badges, String(raw.integration_type ?? ""), "amber");
  }

  if (badges.childElementCount > 0) {
    panel.appendChild(badges);
  }

  if (kind === "category") {
    const category = String(node.data("category") ?? "");
    const modules = instance.catalog.modules.filter(
      (module) => module.category === category,
    );
    panel.appendChild(
      createElement(
        "p",
        "irg-detail-description",
        `Agrupamento arquitetural com ${modules.length} módulos registrados no catálogo real da plataforma.`,
      ),
    );
    appendList(
      panel,
      "Módulos da categoria",
      modules.map((module) => module.title),
      "Nenhum módulo encontrado.",
    );
    return;
  }

  if (kind === "area") {
    const area = raw as Area;
    panel.appendChild(
      createElement(
        "p",
        "irg-detail-description",
        area.description || "Área especializada do módulo selecionado.",
      ),
    );
    const metrics = createElement("div", "irg-detail-metrics");
    appendMetric(metrics, area.capability_count, "capacidades");
    panel.appendChild(metrics);
    appendList(
      panel,
      "Capacidades da área",
      area.capabilities.map((capability) => capability.title),
      "Nenhuma capacidade cadastrada.",
    );
    return;
  }

  if (kind === "capability") {
    const capability = raw as Capability;
    panel.appendChild(
      createElement(
        "p",
        "irg-detail-description",
        capability.description || "Capacidade especializada do módulo selecionado.",
      ),
    );
    appendList(
      panel,
      "Tecnologias conectadas",
      capability.technologies ?? [],
      "Nenhuma tecnologia específica informada.",
    );
    return;
  }

  if (kind === "platform") {
    panel.appendChild(
      createElement(
        "p",
        "irg-detail-description",
        instance.catalog.root.description || "Plataforma modular de inteligência artificial.",
      ),
    );
    const metrics = createElement("div", "irg-detail-metrics");
    appendMetric(metrics, instance.catalog.statistics.module_count, "módulos");
    appendMetric(metrics, instance.catalog.statistics.area_count, "áreas");
    appendMetric(metrics, instance.catalog.statistics.capability_count, "capacidades");
    appendMetric(metrics, instance.catalog.statistics.explicit_relationship_count, "relações reais");
    panel.appendChild(metrics);
    return;
  }

  const moduleId =
    kind === "neighbor"
      ? String(node.data("module_id") ?? "")
      : String(node.id());
  const module = instance.moduleById.get(moduleId) ?? (raw as PlatformModule | undefined);

  if (!module) {
    panel.appendChild(
      createElement("p", "irg-detail-description", "Informações não disponíveis."),
    );
    return;
  }

  panel.appendChild(
    createElement(
      "p",
      "irg-detail-description",
      module.description || "Módulo registrado na arquitetura da INNA.",
    ),
  );

  const metrics = createElement("div", "irg-detail-metrics");
  appendMetric(metrics, module.area_count, "áreas");
  appendMetric(metrics, module.capability_count, "capacidades");
  appendMetric(metrics, moduleRelationships(instance, module.id).length, "relações");
  panel.appendChild(metrics);

  if (instance.viewMode === "overview" || kind === "neighbor") {
    const openButton = createElement("button", "irg-primary-button", "Abrir estrutura do módulo");
    openButton.type = "button";
    openButton.addEventListener("click", () => {
      instance.selectedModuleId = module.id;
      instance.selectedNodeId = module.id;
      instance.viewMode = "module";
      renderGraph(instance, true);
    });
    panel.appendChild(openButton);
  }

  const relationships = moduleRelationships(instance, module.id);
  const outgoing = relationships
    .filter((relationship) => relationship.source === module.id)
    .map((relationship) => {
      const target = instance.moduleById.get(relationship.target);
      return `${target?.title ?? relationship.target} — ${relationship.label ?? relationship.type}`;
    });
  const incoming = relationships
    .filter((relationship) => relationship.target === module.id)
    .map((relationship) => {
      const source = instance.moduleById.get(relationship.source);
      return `${source?.title ?? relationship.source} — ${relationship.label ?? relationship.type}`;
    });

  appendList(panel, "Utiliza / depende de", outgoing, "Nenhuma dependência explícita registrada.");
  appendList(panel, "Utilizado por", incoming, "Nenhum módulo dependente registrado.");
  appendList(
    panel,
    "Fontes do catálogo",
    module.source_registries ?? [],
    "Fonte não informada.",
  );
};

const updateToolbarState = (instance: Instance): void => {
  const overviewButton = instance.root.querySelector<HTMLButtonElement>("[data-view='overview']");
  const moduleButton = instance.root.querySelector<HTMLButtonElement>("[data-view='module']");
  const searchInput = instance.root.querySelector<HTMLInputElement>(".irg-search");
  const categorySelect = instance.root.querySelector<HTMLSelectElement>(".irg-category-filter");
  const relationshipToggle = instance.root.querySelector<HTMLInputElement>(".irg-relationship-toggle");
  const backButton = instance.root.querySelector<HTMLButtonElement>(".irg-back-button");
  const viewLabel = instance.root.querySelector<HTMLElement>(".irg-view-label");

  overviewButton?.classList.toggle("is-active", instance.viewMode === "overview");
  moduleButton?.classList.toggle("is-active", instance.viewMode === "module");

  if (moduleButton) {
    moduleButton.disabled = !instance.selectedModuleId;
  }

  if (searchInput) {
    searchInput.disabled = instance.viewMode === "module";
  }

  if (categorySelect) {
    categorySelect.disabled = instance.viewMode === "module";
  }

  if (relationshipToggle) {
    relationshipToggle.checked = instance.showRelationships;
    relationshipToggle.disabled =
      instance.viewMode === "module" || !instance.selectedModuleId;
  }

  if (backButton) {
    backButton.hidden = instance.viewMode !== "module";
  }

  if (viewLabel) {
    if (instance.viewMode === "module" && instance.selectedModuleId) {
      viewLabel.textContent =
        instance.moduleById.get(instance.selectedModuleId)?.title ?? "Estrutura do módulo";
    } else {
      viewLabel.textContent = `${visibleModules(instance).length} módulos visíveis`;
    }
  }
};


/* INNA_GRAPH_PROFESSIONAL_ZOOM_V2 */

const updateZoomDisplay = (
  instance: Instance,
): void => {
  const valueElement =
    instance.root.querySelector<HTMLElement>(
      ".irg-zoom-value",
    );

  if (!valueElement) {
    return;
  }

  valueElement.textContent =
    `${Math.round(instance.zoomPercent)}%`;
};

const fitGraphToViewport = (
  instance: Instance,
): void => {
  instance.cy.resize();

  const elements =
    instance.cy.elements();

  if (elements.empty()) {
    instance.fitZoom = 1;
    instance.zoomPercent = 100;

  /* INNA_GRAPH_COMPACT_VERTICAL_VIEWPORT_V1 */

  /*
   * Move o conjunto um pouco para cima depois
   * do enquadramento automático.
   *
   * A visão geral recebe um deslocamento maior.
   */
  const upwardOffset =
    instance.viewMode === "overview"
      ? -36
      : -24;

  instance.cy.panBy({
    x: 0,
    y: upwardOffset,
  });

    updateZoomDisplay(instance);

    return;
  }

  /*
   * O valor de 100% representa todo o grafo
   * enquadrado dentro da área disponível.
   */
  instance.cy.fit(
    elements,
    80,
  );

  instance.fitZoom = Math.max(
    instance.cy.zoom(),
    0.0001,
  );

  instance.zoomPercent = 100;

  updateZoomDisplay(instance);
};

const setGraphZoomPercent = (
  instance: Instance,
  requestedPercent: number,
): void => {
  const percent = clamp(
    requestedPercent,
    30,
    250,
  );

  const baseline = Math.max(
    instance.fitZoom,
    0.0001,
  );

  const level = clamp(
    baseline * (percent / 100),
    0.06,
    2.2,
  );

  instance.cy.zoom({
    level,
    renderedPosition: {
      x: instance.cy.width() / 2,
      y: instance.cy.height() / 2,
    },
  });

  instance.zoomPercent = Math.round(
    (level / baseline) * 100,
  );

  updateZoomDisplay(instance);
};


/* INNA_GRAPH_HORIZONTAL_GEOMETRY_ZOOM_V3 */

/**
 * Transforma as posições do layout preset para um
 * formato mais horizontal.
 *
 * - aumenta as distâncias laterais;
 * - reduz as distâncias verticais;
 * - mantém o centro original do conjunto.
 */
const applyProfessionalHorizontalGeometry = (
  instance: Instance,
): void => {
  const nodes = instance.cy.nodes();

  if (nodes.empty()) {
    return;
  }

  let minimumX = Number.POSITIVE_INFINITY;
  let maximumX = Number.NEGATIVE_INFINITY;
  let minimumY = Number.POSITIVE_INFINITY;
  let maximumY = Number.NEGATIVE_INFINITY;

  nodes.forEach((node) => {
    const position = node.position();

    minimumX = Math.min(
      minimumX,
      position.x,
    );

    maximumX = Math.max(
      maximumX,
      position.x,
    );

    minimumY = Math.min(
      minimumY,
      position.y,
    );

    maximumY = Math.max(
      maximumY,
      position.y,
    );
  });

  const centerX =
    (minimumX + maximumX) / 2;

  const centerY =
    (minimumY + maximumY) / 2;

  /*
   * A visão geral recebe uma abertura horizontal
   * maior. A estrutura interna também fica larga,
   * mas um pouco menos para preservar legibilidade.
   */
  const horizontalScale =
    instance.viewMode === "overview"
      ? 1.72
      : 1.48;

  const verticalScale =
    instance.viewMode === "overview"
      ? 0.55
      : 0.64;

  nodes.forEach((node) => {
    const position = node.position();

    node.position({
      x:
        centerX
        + (
          position.x
          - centerX
        )
        * horizontalScale,

      y:
        centerY
        + (
          position.y
          - centerY
        )
        * verticalScale,
    });
  });
};


/* INNA_PLATFORM_ROOT_DISTANCE_V1 */

/**
 * Mantém a INNA AI Platform próxima das categorias
 * conectadas sem retirar sua posição de nó principal.
 */
const pullPlatformRootCloser = (
  instance: Instance,
): void => {
  if (
    instance.viewMode !== "overview"
  ) {
    return;
  }

  const platformNode =
    instance.cy.getElementById(
      "inna-platform",
    );

  if (
    platformNode.empty()
    || !platformNode.isNode()
  ) {
    return;
  }

  const connectedCategories =
    platformNode
      .neighborhood("node")
      .filter((element) => {
        return (
          element.isNode()
          && element.data("kind")
            === "category"
        );
      });

  if (
    connectedCategories.empty()
  ) {
    return;
  }

  let totalX = 0;
  let totalY = 0;

  connectedCategories.forEach(
    (categoryNode) => {
      const position =
        categoryNode.position();

      totalX += position.x;
      totalY += position.y;
    },
  );

  const categoryCount =
    connectedCategories.length;

  const categoryCenter = {
    x: totalX / categoryCount,
    y: totalY / categoryCount,
  };

  const platformPosition =
    platformNode.position();

  const differenceX =
    platformPosition.x
    - categoryCenter.x;

  const differenceY =
    platformPosition.y
    - categoryCenter.y;

  const currentDistance =
    Math.hypot(
      differenceX,
      differenceY,
    );

  /*
   * Distância máxima entre a plataforma e o centro
   * das categorias conectadas.
   *
   * Um valor próximo de 215 mantém a linha visível,
   * mas elimina o grande espaço vazio.
   */
  const maximumDistance = 285;

  if (
    currentDistance <= maximumDistance
  ) {
    return;
  }

  if (
    currentDistance < 0.001
  ) {
    platformNode.position({
      x: categoryCenter.x,
      y:
        categoryCenter.y
        + maximumDistance,
    });

    return;
  }

  const distanceRatio =
    maximumDistance
    / currentDistance;

  platformNode.position({
    x:
      categoryCenter.x
      + differenceX
      * distanceRatio,

    y:
      categoryCenter.y
      + differenceY
      * distanceRatio,
  });
};


const moveInnaPlatformLowerV3 = (
  instance: Instance,
): void => {
  if (
    instance.viewMode !== "overview"
  ) {
    return;
  }

  const platformNode =
    instance.cy.getElementById(
      "inna-platform",
    );

  if (
    platformNode.empty()
    || !platformNode.isNode()
  ) {
    return;
  }

  const currentPosition =
    platformNode.position();

  /*
   * Mantém a INNA como plataforma principal,
   * mas deixa o nó abaixo dos módulos para evitar
   * sobreposição com hr_people_analytics.
   */
  platformNode.position({
    x: currentPosition.x,
    y: currentPosition.y + 165,
  });
};


/* INNA_GRAPH_DYNAMIC_RELATIONS_V3 */

let innaDynamicCatalog: any = null;

type InnaDynamicRelation = {
  source: string;
  target: string;
  type: string;
  label: string;
  description?: string;
};

const innaEscapeHtml = (
  value: unknown,
): string => {
  return String(
    value ?? "",
  )
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
};

const innaNormalizeKey = (
  value: unknown,
): string => {
  return String(
    value ?? "",
  )
    .normalize("NFD")
    .replace(
      /[\u0300-\u036f]/g,
      "",
    )
    .toLowerCase()
    .replace(
      /[^a-z0-9]+/g,
      "-",
    )
    .replace(
      /^-+|-+$/g,
      "",
    );
};

const getInnaDynamicCatalog = (
  instance: Instance,
): any => {
  const unsafeInstance =
    instance as any;

  return (
    unsafeInstance.catalog
    ?? unsafeInstance.data?.catalog
    ?? unsafeInstance.args?.data?.catalog
    ?? innaDynamicCatalog
    ?? null
  );
};

const getInnaModuleMap = (
  catalog: any,
): Map<string, any> => {
  const moduleMap =
    new Map<string, any>();

  const modules =
    Array.isArray(catalog?.modules)
      ? catalog.modules
      : [];

  modules.forEach(
    (moduleRecord: any) => {
      if (!moduleRecord?.id) {
        return;
      }

      moduleMap.set(
        String(moduleRecord.id),
        moduleRecord,
      );
    },
  );

  return moduleMap;
};

const resolveInnaModuleId = (
  moduleMap: Map<string, any>,
  value: unknown,
): string | null => {
  const rendered =
    String(
      value ?? "",
    ).trim();

  if (!rendered) {
    return null;
  }

  if (moduleMap.has(rendered)) {
    return rendered;
  }

  const normalized =
    innaNormalizeKey(rendered);

  for (
    const [
      moduleId,
      moduleRecord,
    ]
    of moduleMap.entries()
  ) {
    if (
      innaNormalizeKey(moduleId)
      === normalized
    ) {
      return moduleId;
    }

    if (
      innaNormalizeKey(
        moduleRecord?.title,
      )
      === normalized
    ) {
      return moduleId;
    }
  }

  return null;
};

const collectInnaModuleRelations = (
  catalog: any,
  moduleId: string,
): InnaDynamicRelation[] => {
  const moduleMap =
    getInnaModuleMap(catalog);

  const uniqueRelations =
    new Map<
      string,
      InnaDynamicRelation
    >();

  const relationships =
    Array.isArray(
      catalog?.relationships,
    )
      ? catalog.relationships
      : [];

  relationships.forEach(
    (relationship: any) => {
      const source =
        String(
          relationship?.source
          ?? "",
        );

      const target =
        String(
          relationship?.target
          ?? "",
        );

      const relationshipType =
        String(
          relationship?.type
          ?? "related_to",
        );

      if (
        relationshipType
          === "contains"
      ) {
        return;
      }

      if (
        source !== moduleId
        && target !== moduleId
      ) {
        return;
      }

      const relatedId =
        source === moduleId
          ? target
          : source;

      if (
        !moduleMap.has(relatedId)
      ) {
        return;
      }

      const key =
        `${source}|${target}|${relationshipType}`;

      uniqueRelations.set(
        key,
        {
          source,
          target,
          type:
            relationshipType,
          label:
            String(
              relationship?.label
              ?? relationshipType,
            ),
          description:
            String(
              relationship?.description
              ?? "",
            ),
        },
      );
    },
  );

  /*
   * Algumas soluções empresariais declaram as
   * tecnologias conectadas dentro das capacidades.
   * Essas conexões também entram na visão dinâmica.
   */
  const selectedModule =
    moduleMap.get(moduleId);

  const areas =
    Array.isArray(
      selectedModule?.areas,
    )
      ? selectedModule.areas
      : [];

  areas.forEach(
    (area: any) => {
      const capabilities =
        Array.isArray(
          area?.capabilities,
        )
          ? area.capabilities
          : [];

      capabilities.forEach(
        (capability: any) => {
          const technologies =
            Array.isArray(
              capability?.technologies,
            )
              ? capability.technologies
              : [];

          technologies.forEach(
            (technology: unknown) => {
              const relatedId =
                resolveInnaModuleId(
                  moduleMap,
                  technology,
                );

              if (
                !relatedId
                || relatedId === moduleId
              ) {
                return;
              }

              const key =
                `${moduleId}|${relatedId}|capability_technology`;

              if (
                uniqueRelations.has(key)
              ) {
                return;
              }

              uniqueRelations.set(
                key,
                {
                  source: moduleId,
                  target: relatedId,
                  type:
                    "capability_technology",
                  label:
                    "Tecnologia conectada",
                },
              );
            },
          );
        },
      );
    },
  );

  return Array.from(
    uniqueRelations.values(),
  );
};

const getInnaRelationLabel = (
  relation: InnaDynamicRelation,
  selectedModuleId: string,
): string => {
  const direction =
    relation.source
      === selectedModuleId
      ? "Utiliza"
      : "Utilizado por";

  const relationName =
    relation.label
      .replace(
        /_/g,
        " ",
      );

  return (
    `${direction} · ${relationName}`
  );
};

const ensureInnaDynamicPanel = (
  instance: Instance,
): HTMLElement => {
  const existingPanel =
    instance.root
      .querySelector<HTMLElement>(
        ".irg-dynamic-module-panel",
      );

  if (existingPanel) {
    return existingPanel;
  }

  const graphContainer =
    (
      instance.root
        .querySelector<HTMLElement>(
          ".irg-graph-card",
        )
      ?? instance.root
        .querySelector<HTMLElement>(
          ".irg-body",
        )
      ?? instance.root
    );

  graphContainer.style.position =
    "relative";

  const panel =
    document.createElement(
      "aside",
    );

  panel.className =
    "irg-dynamic-module-panel";

  panel.hidden = true;

  panel.setAttribute(
    "aria-live",
    "polite",
  );

  panel.addEventListener(
    "click",
    (event: MouseEvent) => {
      const target =
        event.target
          instanceof Element
          ? event.target
          : null;

      const closeButton =
        target?.closest(
          ".irg-dynamic-panel-close",
        );

      if (closeButton) {
        restoreInnaDynamicOverview(
          instance,
        );

        panel.hidden = true;

        return;
      }

      const relatedButton =
        target
          ?.closest<HTMLButtonElement>(
            ".irg-dynamic-related-button",
          );

      const relatedModuleId =
        relatedButton
          ?.dataset
          .moduleId;

      if (!relatedModuleId) {
        return;
      }

      renderInnaModuleRelationFocus(
        instance,
        relatedModuleId,
      );

      renderInnaDynamicDetails(
        instance,
        relatedModuleId,
      );
    },
  );

  graphContainer.appendChild(
    panel,
  );

  return panel;
};

const restoreInnaDynamicOverview = (
  instance: Instance,
): void => {
  const state =
    instance as any;

  const originalElements =
    state
      .__innaOriginalElements;

  if (
    !Array.isArray(
      originalElements,
    )
  ) {
    instance.cy
      .elements()
      .removeClass(
        "irg-dynamic-unrelated",
      );

    fitGraphToViewport(
      instance,
    );

    return;
  }

  instance.cy.elements().remove();

  instance.cy.add(
    originalElements as any,
  );

  instance.cy.layout({
    name: "preset",
    fit: false,
  }).run();

  state.__innaRelationFocusActive =
    false;

  state.__innaOriginalElements =
    null;

  instance.selectedNodeId =
    null;

  instance.selectedModuleId =
    null;

  const visibleCount =
    instance.root
      .querySelector<HTMLElement>(
        ".irg-visible-count",
      );

  if (visibleCount) {
    visibleCount.textContent =
      `${instance.cy.nodes().length} módulos visíveis`;
  }

  window.requestAnimationFrame(
    () => {
      fitGraphToViewport(
        instance,
      );
    },
  );
};

const renderInnaModuleRelationFocus = (
  instance: Instance,
  moduleId: string,
): void => {
  const catalog =
    getInnaDynamicCatalog(
      instance,
    );

  if (!catalog) {
    return;
  }

  const moduleMap =
    getInnaModuleMap(catalog);

  const selectedModule =
    moduleMap.get(moduleId);

  if (!selectedModule) {
    return;
  }

  const state =
    instance as any;

  if (
    !state
      .__innaRelationFocusActive
  ) {
    state.__innaOriginalElements =
      instance.cy
        .elements()
        .jsons();
  }

  state.__innaRelationFocusActive =
    true;

  const relations =
    collectInnaModuleRelations(
      catalog,
      moduleId,
    );

  const relatedIds: string[] = [];

  relations.forEach(
    (relation) => {
      const relatedId =
        relation.source
          === moduleId
          ? relation.target
          : relation.source;

      if (
        relatedId
        && !relatedIds.includes(
          relatedId,
        )
      ) {
        relatedIds.push(
          relatedId,
        );
      }
    },
  );

  const displayedRelatedIds =
    relatedIds.slice(
      0,
      32,
    );

  const displayedIdSet =
    new Set(
      displayedRelatedIds,
    );

  const elements: any[] = [
    {
      data: {
        id: moduleId,
        label:
          `${
            selectedModule.icon
            ?? "🧩"
          } ${
            selectedModule.title
            ?? moduleId
          }`,
        title:
          selectedModule.title
          ?? moduleId,
        description:
          selectedModule.description
          ?? "",
        kind: "module",
        icon:
          selectedModule.icon
          ?? "🧩",
      },
      position: {
        x: 0,
        y: 0,
      },
      classes:
        "irg-dynamic-focus-node",
    },
  ];

  const nodeCount =
    displayedRelatedIds.length;

  displayedRelatedIds.forEach(
    (
      relatedId,
      index,
    ) => {
      const relatedModule =
        moduleMap.get(
          relatedId,
        );

      if (!relatedModule) {
        return;
      }

      const angle =
        nodeCount > 0
          ? (
              (
                Math.PI
                * 2
                * index
              )
              / nodeCount
            )
            - (
              Math.PI
              / 2
            )
          : 0;

      const horizontalRadius =
        nodeCount <= 8
          ? 430
          : 560;

      const verticalRadius =
        nodeCount <= 8
          ? 185
          : 245;

      elements.push({
        data: {
          id: relatedId,
          label:
            `${
              relatedModule.icon
              ?? "🧩"
            } ${
              relatedModule.title
              ?? relatedId
            }`,
          title:
            relatedModule.title
            ?? relatedId,
          description:
            relatedModule.description
            ?? "",
          kind: "module",
          icon:
            relatedModule.icon
            ?? "🧩",
        },
        position: {
          x:
            Math.cos(angle)
            * horizontalRadius,
          y:
            Math.sin(angle)
            * verticalRadius,
        },
      });
    },
  );

  relations.forEach(
    (
      relation,
      index,
    ) => {
      const relatedId =
        relation.source
          === moduleId
          ? relation.target
          : relation.source;

      if (
        !displayedIdSet.has(
          relatedId,
        )
      ) {
        return;
      }

      elements.push({
        data: {
          id:
            `dynamic-relation-${index}-${moduleId}-${relatedId}`,
          source:
            relation.source,
          target:
            relation.target,
          kind:
            "relationship",
          type:
            relation.type,
          label:
            getInnaRelationLabel(
              relation,
              moduleId,
            ),
        },
        classes:
          "irg-dynamic-relation-edge",
      });
    },
  );

  instance.cy.elements().remove();

  instance.cy.add(
    elements as any,
  );

  instance.cy.layout({
    name: "preset",
    fit: false,
  }).run();

  instance.selectedNodeId =
    moduleId;

  instance.selectedModuleId =
    moduleId;

  const selectedNode =
    instance.cy
      .getElementById(
        moduleId,
      );

  selectedNode.select();

  const visibleCount =
    instance.root
      .querySelector<HTMLElement>(
        ".irg-visible-count",
      );

  if (visibleCount) {
    visibleCount.textContent =
      (
        `${displayedRelatedIds.length} `
        + "módulos relacionados"
      );
  }

  const backButton =
    instance.root
      .querySelector<HTMLButtonElement>(
        ".irg-back-button",
      );

  if (backButton) {
    backButton.hidden = false;
  }

  window.requestAnimationFrame(
    () => {
      instance.cy.resize();

      instance.cy.fit(
        instance.cy.elements(),
        80,
      );
    },
  );
};

const renderInnaDynamicDetails = (
  instance: Instance,
  moduleId: string,
): void => {
  const catalog =
    getInnaDynamicCatalog(
      instance,
    );

  if (!catalog) {
    return;
  }

  const moduleMap =
    getInnaModuleMap(catalog);

  const moduleRecord =
    moduleMap.get(moduleId);

  if (!moduleRecord) {
    return;
  }

  const panel =
    ensureInnaDynamicPanel(
      instance,
    );

  const relations =
    collectInnaModuleRelations(
      catalog,
      moduleId,
    );

  const areas =
    Array.isArray(
      moduleRecord.areas,
    )
      ? moduleRecord.areas
      : [];

  const allCapabilities =
    areas.flatMap(
      (area: any) =>
        Array.isArray(
          area?.capabilities,
        )
          ? area.capabilities
          : [],
    );

  const relatedModuleIds: string[] =
    [];

  relations.forEach(
    (relation) => {
      const relatedId =
        relation.source
          === moduleId
          ? relation.target
          : relation.source;

      if (
        relatedId
        && !relatedModuleIds.includes(
          relatedId,
        )
      ) {
        relatedModuleIds.push(
          relatedId,
        );
      }
    },
  );

  const areasHtml =
    areas.length > 0
      ? areas
          .map(
            (
              area: any,
              areaIndex: number,
            ) => {
              const capabilities =
                Array.isArray(
                  area?.capabilities,
                )
                  ? area.capabilities
                  : [];

              const capabilitiesHtml =
                capabilities.length > 0
                  ? capabilities
                      .map(
                        (
                          capability: any,
                          capabilityIndex: number,
                        ) => {
                          const technologies =
                            Array.isArray(
                              capability
                                ?.technologies,
                            )
                              ? capability
                                  .technologies
                              : [];

                          const technologyHtml =
                            technologies.length > 0
                              ? `
                                <div class="irg-dynamic-technologies">
                                  <strong>
                                    Tecnologias:
                                  </strong>
                                  ${technologies
                                    .map(
                                      (
                                        technology:
                                          unknown,
                                      ) =>
                                        `
                                          <span>
                                            ${innaEscapeHtml(
                                              technology,
                                            )}
                                          </span>
                                        `,
                                    )
                                    .join("")}
                                </div>
                              `
                              : "";

                          return `
                            <article class="irg-dynamic-capability-card">
                              <span class="irg-dynamic-capability-number">
                                ${
                                  areaIndex + 1
                                }.${
                                  capabilityIndex + 1
                                }
                              </span>

                              <h5>
                                ${innaEscapeHtml(
                                  capability?.title
                                  ?? capability?.id
                                  ?? "Capacidade",
                                )}
                              </h5>

                              ${
                                capability?.description
                                  ? `
                                    <p>
                                      ${innaEscapeHtml(
                                        capability.description,
                                      )}
                                    </p>
                                  `
                                  : ""
                              }

                              ${technologyHtml}
                            </article>
                          `;
                        },
                      )
                      .join("")
                  : `
                    <p class="irg-dynamic-empty">
                      Nenhuma capacidade cadastrada.
                    </p>
                  `;

              return `
                <section class="irg-dynamic-area-card">
                  <header>
                    <div>
                      <span>
                        Área ${areaIndex + 1}
                      </span>

                      <h4>
                        ${innaEscapeHtml(
                          area?.title
                          ?? area?.id
                          ?? "Área",
                        )}
                      </h4>
                    </div>

                    <strong>
                      ${capabilities.length}
                      capacidades
                    </strong>
                  </header>

                  ${
                    area?.description
                      ? `
                        <p class="irg-dynamic-area-description">
                          ${innaEscapeHtml(
                            area.description,
                          )}
                        </p>
                      `
                      : ""
                  }

                  <div class="irg-dynamic-capabilities-grid">
                    ${capabilitiesHtml}
                  </div>
                </section>
              `;
            },
          )
          .join("")
      : `
        <p class="irg-dynamic-empty">
          Nenhuma área cadastrada para este módulo.
        </p>
      `;

  const relatedHtml =
    relatedModuleIds.length > 0
      ? relatedModuleIds
          .map(
            (relatedId) => {
              const relatedModule =
                moduleMap.get(
                  relatedId,
                );

              if (!relatedModule) {
                return "";
              }

              const matchingRelation =
                relations.find(
                  (relation) =>
                    relation.source
                      === relatedId
                    || relation.target
                      === relatedId,
                );

              return `
                <button
                  type="button"
                  class="irg-dynamic-related-button"
                  data-module-id="${innaEscapeHtml(
                    relatedId,
                  )}"
                >
                  <span>
                    ${innaEscapeHtml(
                      relatedModule.icon
                      ?? "🧩",
                    )}
                  </span>

                  <span>
                    <strong>
                      ${innaEscapeHtml(
                        relatedModule.title
                        ?? relatedId,
                      )}
                    </strong>

                    <small>
                      ${innaEscapeHtml(
                        matchingRelation
                          ? getInnaRelationLabel(
                              matchingRelation,
                              moduleId,
                            )
                          : "Módulo relacionado",
                      )}
                    </small>
                  </span>
                </button>
              `;
            },
          )
          .join("")
      : `
        <p class="irg-dynamic-empty">
          Nenhuma relação direta foi cadastrada.
        </p>
      `;

  panel.innerHTML = `
    <header class="irg-dynamic-panel-header">
      <div>
        <span class="irg-dynamic-panel-kicker">
          Módulo selecionado
        </span>

        <h3>
          ${innaEscapeHtml(
            moduleRecord.icon
            ?? "🧩",
          )}

          ${innaEscapeHtml(
            moduleRecord.title
            ?? moduleId,
          )}
        </h3>

        <p>
          ${innaEscapeHtml(
            moduleRecord.description
            ?? "Descrição não informada.",
          )}
        </p>
      </div>

      <button
        type="button"
        class="irg-dynamic-panel-close"
        aria-label="Fechar detalhes e voltar"
        title="Fechar e voltar"
      >
        ×
      </button>
    </header>

    <div class="irg-dynamic-panel-metrics">
      <span>
        <strong>
          ${areas.length}
        </strong>
        áreas
      </span>

      <span>
        <strong>
          ${allCapabilities.length}
        </strong>
        capacidades
      </span>

      <span>
        <strong>
          ${relatedModuleIds.length}
        </strong>
        módulos relacionados
      </span>
    </div>

    <section class="irg-dynamic-related-section">
      <h4>
        🔗 O que se relaciona com este módulo
      </h4>

      <div class="irg-dynamic-related-grid">
        ${relatedHtml}
      </div>
    </section>

    <section class="irg-dynamic-complete-section">
      <h4>
        📚 Áreas, capacidades e exemplos completos
      </h4>

      <div class="irg-dynamic-areas-list">
        ${areasHtml}
      </div>
    </section>
  `;

  panel.hidden = false;
};

const renderGraph = (instance: Instance, fit = false): void => {
  const elements =
    instance.viewMode === "module"
      ? createModuleElements(instance)
      : createOverviewElements(instance);

  instance.cy.elements().remove();
  instance.cy.add(elements as any);
  instance.cy.layout({
    name: "preset",
    fit: false,
  }).run();

  applyProfessionalHorizontalGeometry(
    instance,
  );

  pullPlatformRootCloser(
    instance,
  );

  moveInnaPlatformLowerV3(
    instance,
  );

  let detailsRendered = false;

  if (instance.selectedNodeId) {
    const selectedNode = instance.cy.getElementById(instance.selectedNodeId);

    if (selectedNode.nonempty() && selectedNode.isNode()) {
      selectedNode.select();
      renderDetailsForNode(instance, selectedNode);
      detailsRendered = true;
    } else {
      instance.selectedNodeId = null;
    }
  }

  if (
    !detailsRendered &&
    instance.viewMode === "module" &&
    instance.selectedModuleId
  ) {
    const selectedModuleNode = instance.cy.getElementById(instance.selectedModuleId);

    if (selectedModuleNode.nonempty()) {
      selectedModuleNode.select();
      renderDetailsForNode(instance, selectedModuleNode);
      detailsRendered = true;
    }
  }

  if (!detailsRendered) {
    renderEmptyDetails(instance);
  }

  updateToolbarState(instance);

  if (fit) {
    window.requestAnimationFrame(() => {
      instance.cy.resize();
      fitGraphToViewport(instance);
    });
  }
};

const installStyles = (root: HTMLDivElement, height: number): void => {
  const style = createElement("style");
  style.textContent = `
    :host { color-scheme: dark; }
    .irg-root { --irg-height: ${height}px; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #e5eefb; }
    .irg-shell {
      height: var(--irg-height);
      min-height: var(--irg-height);
      display: flex;
      flex-direction: column;
      border: 1px solid rgba(148, 163, 184, .16);
      border-radius: 24px;
      overflow: hidden;
      background:
        radial-gradient(
          circle at 10% 0%,
          rgba(88, 28, 135, .28),
          transparent 32%
        ),
        linear-gradient(
          145deg,
          #08111f 0%,
          #060a12 58%,
          #090d16 100%
        );
      box-shadow: 0 24px 70px rgba(0, 0, 0, .34);
    }
    .irg-toolbar { display: grid; grid-template-columns: auto minmax(220px, 1fr) auto; gap: 14px; align-items: center; padding: 16px 18px; border-bottom: 1px solid rgba(148, 163, 184, .14); background: rgba(8, 15, 27, .82); backdrop-filter: blur(14px); }
    .irg-view-switch { display: flex; padding: 4px; border: 1px solid rgba(148, 163, 184, .18); border-radius: 12px; background: rgba(15, 23, 42, .72); }
    .irg-view-button, .irg-icon-button, .irg-back-button, .irg-primary-button { border: 0; cursor: pointer; font: inherit; }
    .irg-view-button { padding: 9px 13px; border-radius: 9px; color: #94a3b8; background: transparent; font-weight: 700; }
    .irg-view-button.is-active { color: #fff; background: linear-gradient(135deg, #6d28d9, #4f46e5); box-shadow: 0 8px 24px rgba(79, 70, 229, .28); }
    .irg-view-button:disabled { cursor: not-allowed; opacity: .38; }
    .irg-controls { display: flex; gap: 9px; align-items: center; min-width: 0; }
    .irg-search, .irg-category-filter { height: 38px; border: 1px solid rgba(148, 163, 184, .18); border-radius: 10px; background: rgba(15, 23, 42, .78); color: #e2e8f0; outline: none; }
    .irg-search { width: min(280px, 36vw); padding: 0 12px; }
    .irg-category-filter { max-width: 220px; padding: 0 10px; }
    .irg-search:focus, .irg-category-filter:focus { border-color: #8b5cf6; box-shadow: 0 0 0 3px rgba(139, 92, 246, .14); }
    .irg-search:disabled, .irg-category-filter:disabled { opacity: .45; }
    .irg-toggle { display: inline-flex; align-items: center; gap: 7px; color: #cbd5e1; font-size: 12px; white-space: nowrap; }
    .irg-toggle input { accent-color: #8b5cf6; }
    .irg-icon-button, .irg-back-button { height: 38px; padding: 0 12px; border-radius: 10px; color: #dbeafe; background: rgba(30, 41, 59, .85); border: 1px solid rgba(148, 163, 184, .16); }
    .irg-icon-button:hover, .irg-back-button:hover { background: rgba(51, 65, 85, .92); }
    .irg-toolbar-right { display: flex; gap: 9px; align-items: center; }
    .irg-stats { display: flex; gap: 8px; padding: 10px 18px; overflow-x: auto; border-bottom: 1px solid rgba(148, 163, 184, .10); background: rgba(2, 6, 23, .46); }
    .irg-stat { min-width: 118px; display: flex; align-items: baseline; gap: 6px; padding: 8px 11px; border-radius: 10px; background: rgba(15, 23, 42, .68); border: 1px solid rgba(148, 163, 184, .11); }
    .irg-stat strong { color: #f8fafc; font-size: 17px; }
    .irg-stat span { color: #94a3b8; font-size: 11px; }
    .irg-body {
      flex: 1 1 auto;
      min-height: 0;
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      grid-template-rows: minmax(0, 1fr) auto;
    }
    .irg-graph-card {
      position: relative;
      min-width: 0;
      min-height: 0;
      overflow: hidden;
      border-right: 0;
      border-bottom: 1px solid rgba(148, 163, 184, .12);
    }
    .irg-canvas { position: absolute; inset: 0; }
    .irg-graph-topline { position: absolute; z-index: 4; top: 14px; left: 16px; display: flex; align-items: center; gap: 10px; pointer-events: none; }
    .irg-view-label { padding: 7px 10px; border-radius: 9px; color: #cbd5e1; background: rgba(2, 6, 23, .74); border: 1px solid rgba(148, 163, 184, .13); font-size: 12px; backdrop-filter: blur(9px); }
    .irg-legend { position: absolute; z-index: 4; left: 16px; bottom: 14px; display: flex; flex-wrap: wrap; gap: 7px; max-width: calc(100% - 32px); pointer-events: none; }
    .irg-legend-item { display: inline-flex; align-items: center; gap: 6px; padding: 5px 8px; border-radius: 999px; color: #cbd5e1; background: rgba(2, 6, 23, .72); border: 1px solid rgba(148, 163, 184, .12); font-size: 10px; backdrop-filter: blur(8px); }
    .irg-dot { width: 8px; height: 8px; border-radius: 999px; }
    .irg-dot-platform { background: #8b5cf6; }
    .irg-dot-category { background: #818cf8; }
    .irg-dot-module { background: #38bdf8; }
    .irg-dot-area { background: #22d3ee; }
    .irg-dot-capability { background: #4ade80; }
    .irg-dot-relation { background: #f59e0b; }
    .irg-details {
      min-height: 220px;
      max-height: 270px;
      overflow: auto;
      padding: 20px 24px 24px;
      display: grid;
      grid-template-columns:
        minmax(280px, 1.2fr)
        minmax(220px, .8fr)
        minmax(300px, 1fr);
      grid-auto-flow: row dense;
      gap: 10px 24px;
      align-items: start;
      background:
        linear-gradient(
          90deg,
          rgba(15, 23, 42, .88),
          rgba(2, 6, 23, .94)
        );
    }

    .irg-detail-kicker,
    .irg-details h3,
    .irg-badges,
    .irg-detail-description {
      grid-column: 1;
    }

    .irg-details h3 {
      margin-top: 3px;
    }

    .irg-detail-description {
      margin-bottom: 0;
    }

    .irg-detail-metrics {
      grid-column: 2;
      grid-row: 1 / span 4;
      align-self: start;
      margin: 0;
    }

    .irg-primary-button {
      grid-column: 2;
      align-self: start;
      margin: 8px 0 0;
    }

    .irg-detail-section {
      grid-column: 3;
      margin: 0;
      padding: 0 0 0 20px;
      border-top: 0;
      border-left:
        1px solid rgba(148, 163, 184, .14);
    }
    .irg-detail-kicker { color: #a78bfa; font-size: 10px; font-weight: 800; letter-spacing: .15em; }
    .irg-details h3 { margin: 8px 0 10px; color: #f8fafc; font-size: 21px; line-height: 1.22; }
    .irg-detail-description { margin: 0 0 16px; color: #aebed3; font-size: 13px; line-height: 1.62; }
    .irg-badges { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 15px; }
    .irg-badge { display: inline-flex; padding: 5px 8px; border-radius: 999px; color: #cbd5e1; background: rgba(51, 65, 85, .6); border: 1px solid rgba(148, 163, 184, .14); font-size: 10px; }
    .irg-badge-purple { color: #ddd6fe; background: rgba(109, 40, 217, .22); border-color: rgba(167, 139, 250, .3); }
    .irg-badge-blue { color: #bfdbfe; background: rgba(37, 99, 235, .18); border-color: rgba(96, 165, 250, .25); }
    .irg-badge-green { color: #bbf7d0; background: rgba(22, 101, 52, .2); border-color: rgba(74, 222, 128, .22); }
    .irg-badge-amber { color: #fde68a; background: rgba(146, 64, 14, .18); border-color: rgba(245, 158, 11, .24); }
    .irg-detail-metrics { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin: 0 0 16px; }
    .irg-detail-metric { padding: 10px 8px; border-radius: 10px; text-align: center; background: rgba(15, 23, 42, .72); border: 1px solid rgba(148, 163, 184, .11); }
    .irg-detail-metric strong { display: block; color: #f8fafc; font-size: 17px; }
    .irg-detail-metric span { display: block; margin-top: 2px; color: #8293aa; font-size: 9px; text-transform: uppercase; letter-spacing: .06em; }
    .irg-primary-button { width: 100%; margin: 0 0 18px; padding: 11px 13px; border-radius: 11px; color: #fff; font-weight: 800; background: linear-gradient(135deg, #6d28d9, #4f46e5); box-shadow: 0 10px 26px rgba(79, 70, 229, .22); }
    .irg-primary-button:hover { filter: brightness(1.08); }
    .irg-detail-section { padding-top: 14px; margin-top: 14px; border-top: 1px solid rgba(148, 163, 184, .12); }
    .irg-detail-section h4 { margin: 0 0 9px; color: #dbeafe; font-size: 12px; }
    .irg-detail-list { margin: 0; padding-left: 17px; color: #9fb0c5; font-size: 11px; line-height: 1.55; }
    .irg-detail-list li + li { margin-top: 5px; }
    .irg-muted { color: #708197; font-size: 11px; line-height: 1.5; }
    .irg-error { margin: 20px; padding: 18px; border-radius: 14px; color: #fecaca; background: rgba(127, 29, 29, .24); border: 1px solid rgba(248, 113, 113, .25); }
    @media (max-width: 1120px) {
      .irg-toolbar { grid-template-columns: 1fr; }
      .irg-controls { flex-wrap: wrap; }
      .irg-body {
        grid-template-columns: minmax(0, 1fr);
        grid-template-rows: minmax(0, 1fr) auto;
      }

      .irg-graph-card {
        min-height: 0;
        border-right: 0;
        border-bottom:
          1px solid rgba(148, 163, 184, .12);
      }

      .irg-details {
        max-height: 330px;
        grid-template-columns:
          minmax(0, 1fr)
          minmax(230px, .8fr);
      }

      .irg-detail-section {
        grid-column: 1 / -1;
        padding: 14px 0 0;
        border-left: 0;
        border-top:
          1px solid rgba(148, 163, 184, .12);
      }
    }
    @media (max-width: 700px) {
      .irg-toolbar { padding: 12px; }
      .irg-controls { align-items: stretch; }
      .irg-search, .irg-category-filter { width: 100%; max-width: none; }
      .irg-toggle { width: 100%; }
      .irg-body { min-height: auto; }
      .irg-graph-card { min-height: 580px; }
      .irg-details {
        max-height: 390px;
        padding: 17px;
        grid-template-columns: minmax(0, 1fr);
      }

      .irg-detail-kicker,
      .irg-details h3,
      .irg-badges,
      .irg-detail-description,
      .irg-detail-metrics,
      .irg-primary-button,
      .irg-detail-section {
        grid-column: 1;
        grid-row: auto;
      }

      .irg-detail-metrics {
        grid-template-columns:
          repeat(2, minmax(0, 1fr));
      }

      .irg-detail-section {
        padding: 14px 0 0;
        border-left: 0;
        border-top:
          1px solid rgba(148, 163, 184, .12);
      }
    }
    /* INNA_GRAPH_WITHOUT_BOTTOM_DETAILS_START */

    .irg-shell {
      height: var(--irg-height) !important;
      min-height: var(--irg-height) !important;
      display: flex !important;
      flex-direction: column !important;
    }

    .irg-toolbar {
      flex: 0 0 auto !important;
    }

    /*
     * Os indicadores já são apresentados acima do grafo
     * pela página Streamlit. Esta linha interna é removida
     * para não duplicar os números.
     */
    .irg-stats {
      display: none !important;
    }

    .irg-body {
      flex: 1 1 auto !important;
      min-height: 0 !important;
      height: auto !important;
      display: block !important;
      grid-template-columns: none !important;
      grid-template-rows: none !important;
    }

    .irg-graph-card {
      width: 100% !important;
      height: 100% !important;
      min-width: 0 !important;
      min-height: 0 !important;
      border-right: 0 !important;
      border-bottom: 0 !important;
    }

    .irg-canvas {
      position: absolute !important;
      inset: 0 !important;
    }

    /*
     * Segurança adicional caso uma versão antiga do HTML
     * ainda mantenha o elemento de detalhes.
     */
    .irg-details {
      display: none !important;
      width: 0 !important;
      height: 0 !important;
      min-height: 0 !important;
      max-height: 0 !important;
      padding: 0 !important;
      margin: 0 !important;
      border: 0 !important;
      overflow: hidden !important;
    }

    @media (max-width: 1120px) {
      .irg-body {
        min-height: 0 !important;
        height: auto !important;
      }

      .irg-graph-card {
        min-height: 0 !important;
        height: 100% !important;
        border-bottom: 0 !important;
      }
    }

    @media (max-width: 700px) {
      .irg-body {
        min-height: 0 !important;
      }

      .irg-graph-card {
        min-height: 0 !important;
        height: 100% !important;
      }
    }

    /* INNA_GRAPH_WITHOUT_BOTTOM_DETAILS_END */


    .irg-zoom-group {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px;
      border:
        1px solid
        rgba(148, 163, 184, .16);
      border-radius: 11px;
      background:
        rgba(15, 23, 42, .78);
    }

    .irg-zoom-button {
      min-width: 38px;
      height: 32px;
      padding: 0 9px;
      border: 0;
      border-radius: 8px;
      cursor: pointer;
      color: #dbeafe;
      background: transparent;
      font: inherit;
      font-size: 15px;
      font-weight: 800;
    }

    .irg-zoom-button:hover {
      color: #ffffff;
      background:
        rgba(51, 65, 85, .88);
    }

    .irg-zoom-reset {
      min-width: 62px;
      font-size: 11px;
    }

    .irg-zoom-value {
      display: inline-block;
      min-width: 42px;
      text-align: center;
    }


    /* INNA_GRAPH_TOOLBAR_ZOOM_LAYOUT_V3 */

    /*
     * A barra usa flex para impedir que busca,
     * categoria, relações e zoom se sobreponham.
     */
    .irg-toolbar {
      display: flex !important;
      flex-wrap: wrap !important;
      align-items: center !important;
      gap: 10px 14px !important;
    }

    .irg-view-switch {
      flex: 0 0 auto !important;
    }

    .irg-controls {
      flex: 1 1 540px !important;
      min-width: 360px !important;
      display: flex !important;
      align-items: center !important;
      gap: 9px !important;
      overflow: visible !important;
    }

    .irg-toolbar-right {
      flex: 0 0 auto !important;
      margin-left: auto !important;
      display: flex !important;
      flex-wrap: nowrap !important;
      align-items: center !important;
      justify-content: flex-end !important;
      gap: 8px !important;
      position: relative !important;
      z-index: 20 !important;
    }

    .irg-toggle {
      flex: 0 0 auto !important;
      max-width: 96px !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
    }

    .irg-zoom-group {
      flex: 0 0 auto !important;
      position: relative !important;
      z-index: 30 !important;
      pointer-events: auto !important;
    }

    .irg-zoom-button,
    .irg-zoom-value {
      position: relative !important;
      z-index: 31 !important;
      pointer-events: auto !important;
      user-select: none !important;
    }

    .irg-zoom-button {
      touch-action: manipulation !important;
    }

    .irg-zoom-reset {
      min-width: 66px !important;
    }

    .irg-fit-button {
      flex: 0 0 auto !important;
    }

    @media (max-width: 1250px) {
      .irg-view-switch {
        order: 1 !important;
      }

      .irg-toolbar-right {
        order: 2 !important;
      }

      .irg-controls {
        order: 3 !important;
        flex: 1 0 100% !important;
        min-width: 0 !important;
      }

      .irg-search {
        flex: 1 1 260px !important;
        width: auto !important;
      }

      .irg-category-filter {
        flex: 0 1 260px !important;
        max-width: 260px !important;
      }
    }

    @media (max-width: 760px) {
      .irg-toolbar {
        align-items: stretch !important;
      }

      .irg-view-switch,
      .irg-controls,
      .irg-toolbar-right {
        width: 100% !important;
      }

      .irg-toolbar-right {
        margin-left: 0 !important;
        justify-content: flex-start !important;
      }

      .irg-controls {
        flex-wrap: wrap !important;
      }

      .irg-search,
      .irg-category-filter {
        flex: 1 1 100% !important;
        width: 100% !important;
        max-width: none !important;
      }
    }


    /* INNA_GRAPH_COMPACT_LEGEND_POSITION_V1 */

    .irg-legend {
      bottom: 10px !important;
      left: 14px !important;
    }

    .irg-graph-card {
      padding-bottom: 0 !important;
    }

    .irg-canvas {
      bottom: 0 !important;
    }


    /* INNA_GRAPH_DYNAMIC_RELATIONS_CSS_V3 */

    .irg-dynamic-module-panel {
      position: absolute;
      inset: 18px;
      z-index: 90;
      overflow: auto;
      padding: 22px;
      border:
        1px solid
        rgba(96, 165, 250, .42);
      border-radius: 18px;
      background:
        linear-gradient(
          145deg,
          rgba(8, 27, 48, .985),
          rgba(3, 11, 23, .99)
        );
      box-shadow:
        0 28px 90px
        rgba(0, 0, 0, .55);
    }

    .irg-dynamic-module-panel[hidden] {
      display: none !important;
    }

    .irg-dynamic-panel-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 24px;
      padding-bottom: 18px;
      border-bottom:
        1px solid
        rgba(148, 163, 184, .16);
    }

    .irg-dynamic-panel-kicker {
      display: block;
      margin-bottom: 7px;
      color: #a78bfa;
      font-size: 10px;
      font-weight: 850;
      letter-spacing: .85px;
      text-transform: uppercase;
    }

    .irg-dynamic-panel-header h3 {
      margin: 0;
      color: #ffffff;
      font-size: 25px;
      line-height: 1.2;
    }

    .irg-dynamic-panel-header p {
      max-width: 920px;
      margin: 10px 0 0;
      color: #cbd5e1;
      font-size: 14px;
      line-height: 1.55;
    }

    .irg-dynamic-panel-close {
      flex: 0 0 auto;
      width: 38px;
      height: 38px;
      border:
        1px solid
        rgba(148, 163, 184, .28);
      border-radius: 10px;
      cursor: pointer;
      color: #ffffff;
      background:
        rgba(30, 41, 59, .88);
      font-size: 24px;
      line-height: 1;
    }

    .irg-dynamic-panel-close:hover {
      background:
        rgba(71, 85, 105, .95);
    }

    .irg-dynamic-panel-metrics {
      display: grid;
      grid-template-columns:
        repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin: 16px 0;
    }

    .irg-dynamic-panel-metrics span {
      padding: 11px;
      border:
        1px solid
        rgba(96, 165, 250, .2);
      border-radius: 11px;
      color: #93c5fd;
      background:
        rgba(15, 35, 58, .76);
      font-size: 11px;
      text-align: center;
      text-transform: uppercase;
      letter-spacing: .45px;
    }

    .irg-dynamic-panel-metrics strong {
      display: block;
      margin-bottom: 4px;
      color: #ffffff;
      font-size: 20px;
      letter-spacing: normal;
    }

    .irg-dynamic-related-section,
    .irg-dynamic-complete-section {
      margin-top: 18px;
    }

    .irg-dynamic-related-section > h4,
    .irg-dynamic-complete-section > h4 {
      margin: 0 0 12px;
      color: #e0f2fe;
      font-size: 14px;
    }

    .irg-dynamic-related-grid {
      display: grid;
      grid-template-columns:
        repeat(3, minmax(0, 1fr));
      gap: 9px;
    }

    .irg-dynamic-related-button {
      min-width: 0;
      padding: 11px;
      display: flex;
      align-items: center;
      gap: 9px;
      border:
        1px solid
        rgba(56, 189, 248, .24);
      border-radius: 11px;
      cursor: pointer;
      color: #dbeafe;
      background:
        rgba(14, 51, 78, .58);
      text-align: left;
      font: inherit;
    }

    .irg-dynamic-related-button:hover {
      border-color:
        rgba(125, 211, 252, .7);
      background:
        rgba(14, 74, 110, .78);
    }

    .irg-dynamic-related-button strong,
    .irg-dynamic-related-button small {
      display: block;
    }

    .irg-dynamic-related-button strong {
      font-size: 11px;
    }

    .irg-dynamic-related-button small {
      margin-top: 3px;
      color: #7dd3fc;
      font-size: 9px;
    }

    .irg-dynamic-areas-list {
      display: grid;
      gap: 12px;
    }

    .irg-dynamic-area-card {
      padding: 15px;
      border:
        1px solid
        rgba(148, 163, 184, .15);
      border-radius: 13px;
      background:
        rgba(2, 8, 23, .58);
    }

    .irg-dynamic-area-card > header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 14px;
    }

    .irg-dynamic-area-card > header span {
      display: block;
      margin-bottom: 4px;
      color: #22d3ee;
      font-size: 9px;
      font-weight: 800;
      text-transform: uppercase;
    }

    .irg-dynamic-area-card > header h4 {
      margin: 0;
      color: #ffffff;
      font-size: 14px;
    }

    .irg-dynamic-area-card > header > strong {
      color: #93c5fd;
      font-size: 10px;
      white-space: nowrap;
    }

    .irg-dynamic-area-description {
      margin: 8px 0 12px;
      color: #94a3b8;
      font-size: 11px;
      line-height: 1.45;
    }

    .irg-dynamic-capabilities-grid {
      display: grid;
      grid-template-columns:
        repeat(3, minmax(0, 1fr));
      gap: 9px;
      margin-top: 12px;
    }

    .irg-dynamic-capability-card {
      min-width: 0;
      padding: 11px;
      border:
        1px solid
        rgba(74, 222, 128, .18);
      border-radius: 10px;
      background:
        rgba(4, 40, 30, .4);
    }

    .irg-dynamic-capability-number {
      display: block;
      margin-bottom: 5px;
      color: #4ade80;
      font-size: 9px;
      font-weight: 800;
    }

    .irg-dynamic-capability-card h5 {
      margin: 0;
      color: #ecfdf5;
      font-size: 11px;
      line-height: 1.35;
    }

    .irg-dynamic-capability-card p {
      margin: 7px 0 0;
      color: #a7f3d0;
      font-size: 10px;
      line-height: 1.4;
    }

    .irg-dynamic-technologies {
      margin-top: 8px;
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
    }

    .irg-dynamic-technologies strong {
      width: 100%;
      color: #93c5fd;
      font-size: 9px;
    }

    .irg-dynamic-technologies span {
      padding: 3px 6px;
      border-radius: 999px;
      color: #bae6fd;
      background:
        rgba(14, 116, 144, .3);
      font-size: 8px;
    }

    .irg-dynamic-empty {
      margin: 0;
      color: #94a3b8;
      font-size: 11px;
    }

    node.irg-dynamic-focus-node {
      border-width: 7px !important;
      border-color: #ffffff !important;
      overlay-color: #8b5cf6 !important;
      overlay-opacity: .2 !important;
      overlay-padding: 16px !important;
    }

    edge.irg-dynamic-relation-edge {
      width: 3px !important;
      line-color: #f59e0b !important;
      target-arrow-color: #f59e0b !important;
      target-arrow-shape:
        triangle !important;
      curve-style:
        bezier !important;
      opacity: .86 !important;
    }

    @media (max-width: 980px) {
      .irg-dynamic-related-grid,
      .irg-dynamic-capabilities-grid {
        grid-template-columns:
          repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 650px) {
      .irg-dynamic-module-panel {
        inset: 8px;
        padding: 14px;
      }

      .irg-dynamic-panel-metrics,
      .irg-dynamic-related-grid,
      .irg-dynamic-capabilities-grid {
        grid-template-columns:
          minmax(0, 1fr);
      }
    }


  `;
  root.appendChild(style);
};

const buildShell = (root: HTMLDivElement): void => {
  const shell = createElement("div", "irg-shell");
  shell.innerHTML = `
    <div class="irg-toolbar">
      <div class="irg-view-switch" role="group" aria-label="Modo de visualização">
        <button class="irg-view-button is-active" type="button" data-view="overview">${innaUi("overview")}</button>
        <button class="irg-view-button" type="button" data-view="module" disabled>${innaUi("module_structure")}</button>
      </div>
      <div class="irg-controls">
        <input class="irg-search" type="search" placeholder="${innaUi("search_placeholder")}" aria-label="Buscar módulos" />
        <select class="irg-category-filter" aria-label="Filtrar por categoria">
          <option value="all">${innaUi("all_categories")}</option>
        </select>
        <label class="irg-toggle">
          <input class="irg-relationship-toggle" type="checkbox" disabled />
          <span>${innaUi("relationships")}</span>
        </label>
      </div>
      <div class="irg-toolbar-right">
        <button class="irg-back-button" type="button" hidden>${innaUi("back_overview")}</button>
        <div
          class="irg-zoom-group"
          role="group"
          aria-label="Controle de zoom"
        >
          <button
            class="irg-zoom-button irg-zoom-out"
            type="button"
            title="Diminuir zoom"
            aria-label="Diminuir zoom"
          >
            −
          </button>

          <button
            class="irg-zoom-button irg-zoom-reset"
            type="button"
            title="Enquadrar o grafo em 100%"
            aria-label="Enquadrar o grafo em 100%"
          >
            <span class="irg-zoom-value">
              100%
            </span>
          </button>

          <button
            class="irg-zoom-button irg-zoom-in"
            type="button"
            title="Aumentar zoom"
            aria-label="Aumentar zoom"
          >
            +
          </button>
        </div>

        <button
          class="irg-icon-button irg-fit-button"
          type="button"
          title="${innaUi("fit")}"
        >
          ${innaUi("fit")}
        </button>
      </div>
    </div>
    <div class="irg-stats"></div>
    <div class="irg-body">
      <section class="irg-graph-card">
        <div class="irg-graph-topline"><span class="irg-view-label"></span></div>
        <div class="irg-canvas" aria-label="Grafo interativo da arquitetura INNA"></div>
        <div class="irg-legend" aria-label="${innaUi("legend")}">
          <span class="irg-legend-item"><i class="irg-dot irg-dot-platform"></i>${innaUi("platform")}</span>
          <span class="irg-legend-item"><i class="irg-dot irg-dot-category"></i>${innaUi("category")}</span>
          <span class="irg-legend-item"><i class="irg-dot irg-dot-module"></i>${innaUi("module")}</span>
          <span class="irg-legend-item"><i class="irg-dot irg-dot-area"></i>${innaUi("area")}</span>
          <span class="irg-legend-item"><i class="irg-dot irg-dot-capability"></i>${innaUi("capability")}</span>
          <span class="irg-legend-item"><i class="irg-dot irg-dot-relation"></i>${innaUi("real_relationship")}</span>
        </div>
      </section>
    </div>
  `;
  root.appendChild(shell);
};

const configureCategoryFilter = (instance: Instance): void => {
  const select = instance.root.querySelector<HTMLSelectElement>(".irg-category-filter");

  if (!select) {
    return;
  }

  const categories = Array.from(
    new Set(instance.catalog.modules.map((module) => module.category || "unknown")),
  ).sort((left, right) => {
    const leftIndex = CATEGORY_ORDER.indexOf(left);
    const rightIndex = CATEGORY_ORDER.indexOf(right);
    return (leftIndex < 0 ? 999 : leftIndex) - (rightIndex < 0 ? 999 : rightIndex);
  });

  categories.forEach((category) => {
    const option = createElement("option");
    option.value = category;
    option.textContent = `${categoryLabel(category)} (${instance.catalog.statistics.categories[category] ?? 0})`;
    select.appendChild(option);
  });
};

const bindControls = (instance: Instance): Array<() => void> => {
  const cleanups: Array<() => void> = [];
  const overviewButton = instance.root.querySelector<HTMLButtonElement>("[data-view='overview']");
  const moduleButton = instance.root.querySelector<HTMLButtonElement>("[data-view='module']");
  const searchInput = instance.root.querySelector<HTMLInputElement>(".irg-search");
  const categorySelect = instance.root.querySelector<HTMLSelectElement>(".irg-category-filter");
  const relationshipToggle = instance.root.querySelector<HTMLInputElement>(".irg-relationship-toggle");
  const fitButton = instance.root.querySelector<HTMLButtonElement>(".irg-fit-button");
  const zoomOutButton =
    instance.root.querySelector<HTMLButtonElement>(
      ".irg-zoom-out",
    );

  const zoomResetButton =
    instance.root.querySelector<HTMLButtonElement>(
      ".irg-zoom-reset",
    );

  const zoomInButton =
    instance.root.querySelector<HTMLButtonElement>(
      ".irg-zoom-in",
    );
  const backButton = instance.root.querySelector<HTMLButtonElement>(".irg-back-button");

  const onOverview = (): void => {
    instance.viewMode = "overview";
    instance.selectedNodeId = instance.selectedModuleId;
    renderGraph(instance, true);
  };
  const onModule = (): void => {
    if (!instance.selectedModuleId) {
      return;
    }
    instance.viewMode = "module";
    instance.selectedNodeId = instance.selectedModuleId;
    renderGraph(instance, true);
  };
  const onSearch = (): void => {
    instance.searchTerm = searchInput?.value ?? "";
    instance.selectedNodeId = null;
    renderGraph(instance, true);
  };
  const onCategory = (): void => {
    instance.categoryFilter = categorySelect?.value ?? "all";
    instance.selectedNodeId = null;
    renderGraph(instance, true);
  };
  const onRelationships = (): void => {
    instance.showRelationships = Boolean(relationshipToggle?.checked);
    renderGraph(instance, false);
  };
  const onFit = (): void => {
    fitGraphToViewport(instance);
  };

  const onZoomOut = (): void => {
    setGraphZoomPercent(
      instance,
      instance.zoomPercent - 10,
    );
  };

  const onZoomReset = (): void => {
    setGraphZoomPercent(
      instance,
      100,
    );
  };

  const onZoomIn = (): void => {
    setGraphZoomPercent(
      instance,
      instance.zoomPercent + 10,
    );
  };


  overviewButton?.addEventListener("click", onOverview);
  moduleButton?.addEventListener("click", onModule);
  backButton?.addEventListener("click", onOverview);
  searchInput?.addEventListener("input", onSearch);
  categorySelect?.addEventListener("change", onCategory);
  relationshipToggle?.addEventListener("change", onRelationships);
  zoomOutButton?.addEventListener(
    "click",
    onZoomOut,
  );

  zoomResetButton?.addEventListener(
    "click",
    onZoomReset,
  );

  zoomInButton?.addEventListener(
    "click",
    onZoomIn,
  );

  fitButton?.addEventListener(
    "click",
    onFit,
  );

  cleanups.push(() => overviewButton?.removeEventListener("click", onOverview));
  cleanups.push(() => moduleButton?.removeEventListener("click", onModule));
  cleanups.push(() => backButton?.removeEventListener("click", onOverview));
  cleanups.push(() => searchInput?.removeEventListener("input", onSearch));
  cleanups.push(() => categorySelect?.removeEventListener("change", onCategory));
  cleanups.push(() => relationshipToggle?.removeEventListener("change", onRelationships));
  cleanups.push(
    () => zoomOutButton?.removeEventListener(
      "click",
      onZoomOut,
    ),
  );

  cleanups.push(
    () => zoomResetButton?.removeEventListener(
      "click",
      onZoomReset,
    ),
  );

  cleanups.push(
    () => zoomInButton?.removeEventListener(
      "click",
      onZoomIn,
    ),
  );

  cleanups.push(
    () => fitButton?.removeEventListener(
      "click",
      onFit,
    ),
  );


  /* INNA_GRAPH_ZOOM_CAPTURE_HANDLER_V3 */

  /*
   * O listener em modo capture garante que o clique
   * seja reconhecido mesmo quando o usuário clicar
   * no texto 100% ou em outro elemento interno.
   */
  const onZoomControlClick = (
    event: MouseEvent,
  ): void => {
    const eventElement =
      event.target instanceof Element
        ? event.target
        : null;

    const button =
      eventElement?.closest<HTMLButtonElement>(
        ".irg-zoom-button",
      );

    if (!button) {
      return;
    }

    event.preventDefault();
    event.stopImmediatePropagation();

    if (
      button.classList.contains(
        "irg-zoom-out",
      )
    ) {
      setGraphZoomPercent(
        instance,
        instance.zoomPercent - 10,
      );

      return;
    }

    if (
      button.classList.contains(
        "irg-zoom-in",
      )
    ) {
      setGraphZoomPercent(
        instance,
        instance.zoomPercent + 10,
      );

      return;
    }

    if (
      button.classList.contains(
        "irg-zoom-reset",
      )
    ) {
      /*
       * O botão 100% passa a enquadrar novamente
       * todos os elementos do grafo.
       */
      fitGraphToViewport(
        instance,
      );
    }
  };

  instance.root.addEventListener(
    "click",
    onZoomControlClick,
    true,
  );

  cleanups.push(
    () => instance.root.removeEventListener(
      "click",
      onZoomControlClick,
      true,
    ),
  );

  return cleanups;
};

const createInstance = (
  component: FrontendRendererArgs<GraphState, ComponentData>,
): Instance => {
  const { parentElement, data } = component;

  innaGraphLocale = normalizeGraphLocale(
    String(data?.locale ?? "pt"),
  );

  const localizedCategoryLabels = (
    (data?.catalog as any)?.category_labels
    ?? {}
  ) as Record<string, string>;

  Object.assign(
    CATEGORY_LABELS,
    localizedCategoryLabels,
  );

  const height = clamp(Number(data?.height ?? 900), 680, 1280);
  const root = createElement("div", "irg-root");
  installStyles(root, height);
  buildShell(root);
  parentElement.appendChild(root);

  const catalog = data?.catalog;

  if (!catalog || !Array.isArray(catalog.modules) || !Array.isArray(catalog.relationships)) {
    root.textContent = "";
    installStyles(root, height);
    root.appendChild(
      createElement(
        "div",
        "irg-error",
        "O catálogo do grafo não foi recebido ou possui formato inválido.",
      ),
    );
    throw new Error("Invalid relationship graph catalog");
  }

  const canvas = root.querySelector<HTMLElement>(".irg-canvas");

  if (!canvas) {
    throw new Error("Graph canvas was not created");
  }

  const cy = cytoscape({
    container: canvas,
    elements: [],
    style: stylesheet as any,
    layout: { name: "preset" },
    minZoom: 0.06,
    maxZoom: 2.2,
    wheelSensitivity: 0.22,
    boxSelectionEnabled: false,
    autoungrabify: false,
  });

  const moduleById = new Map<string, PlatformModule>(
    catalog.modules.map((module) => [module.id, module]),
  );

  const instance: Instance = {
    root,
    cy,
    catalog,
    moduleById,
    selectedNodeId: null,
    selectedModuleId: null,
    viewMode: "overview",
    categoryFilter: "all",
    searchTerm: "",
    showRelationships: true,
    fitZoom: 1,
    zoomPercent: 100,
    destroy: () => undefined,
  };

  configureCategoryFilter(instance);
  updateStatistics(instance);
  const controlCleanups = bindControls(instance);

  const onNodeTap = (event: any): void => {
  /* INNA_GRAPH_DYNAMIC_NODE_CLICK_V3 */

  const innaClickedNode =
    event.target;

  const innaClickedKind =
    String(
      innaClickedNode.data(
        "kind",
      )
      ?? "",
    );

  if (
    innaClickedKind === "module"
    && instance.viewMode
      === "overview"
  ) {
    event.stopPropagation();

    const innaClickedModuleId =
      innaClickedNode.id();

    renderInnaModuleRelationFocus(
      instance,
      innaClickedModuleId,
    );

    renderInnaDynamicDetails(
      instance,
      innaClickedModuleId,
    );

    return;
  }

    const node = event.target;
    const kind = String(node.data("kind") ?? "");
    const moduleId =
      kind === "neighbor"
        ? String(node.data("module_id") ?? "")
        : kind === "module" || kind === "module-focus"
          ? String(node.id())
          : null;

    instance.selectedNodeId = String(node.id());

    if (moduleId) {
      instance.selectedModuleId = moduleId;
    }

    renderDetailsForNode(instance, node);
    updateToolbarState(instance);

    if (instance.viewMode === "overview" && moduleId && instance.showRelationships) {
      renderGraph(instance, false);
    }
  };

  const onBackgroundTap = (event: any): void => {
  /* INNA_GRAPH_DYNAMIC_BACKGROUND_CLICK_V3 */

  const innaDynamicState =
    instance as any;

  if (
    innaDynamicState
      .__innaRelationFocusActive
    && event.target
      === instance.cy
  ) {
    restoreInnaDynamicOverview(
      instance,
    );

    const innaDynamicPanel =
      instance.root
        .querySelector<HTMLElement>(
          ".irg-dynamic-module-panel",
        );

    if (innaDynamicPanel) {
      innaDynamicPanel.hidden = true;
    }

    return;
  }

    if (event.target !== instance.cy) {
      return;
    }

    instance.selectedNodeId = null;

    if (instance.viewMode === "overview") {
      instance.selectedModuleId = null;
      renderGraph(instance, false);
    } else {
      renderEmptyDetails(instance);
    }

    updateToolbarState(instance);
  };

  const onCyZoom = (): void => {
    const baseline = Math.max(
      instance.fitZoom,
      0.0001,
    );

    instance.zoomPercent = clamp(
      Math.round(
        (
          instance.cy.zoom()
          / baseline
        )
        * 100,
      ),
      30,
      250,
    );

    updateZoomDisplay(instance);
  };

  cy.on("tap", "node", onNodeTap);
  cy.on("tap", onBackgroundTap);
  cy.on("zoom", onCyZoom);

  const resizeObserver = new ResizeObserver(() => {
    cy.resize();
  });
  resizeObserver.observe(canvas);

  instance.destroy = (): void => {
    controlCleanups.forEach((cleanup) => cleanup());
    resizeObserver.disconnect();
    cy.off("tap", "node", onNodeTap);
    cy.off("tap", onBackgroundTap);
    cy.off("zoom", onCyZoom);
    cy.destroy();
    root.remove();
  };

  renderGraph(instance, true);

  return instance;
};

const RelationshipGraphRenderer: FrontendRenderer<GraphState, ComponentData> = (
  component,
) => {
  const previousInstance = instances.get(component.parentElement);

  if (previousInstance) {
    previousInstance.destroy();
    instances.delete(component.parentElement);
  }

  try {
    const instance = createInstance(component);
    instances.set(component.parentElement, instance);

    return () => {
      const currentInstance = instances.get(component.parentElement);
      if (currentInstance === instance) {
        instance.destroy();
        instances.delete(component.parentElement);
      }
    };
  } catch (error) {
    console.error("INNA relationship graph failed to render", error);
    return undefined;
  }
};

export default RelationshipGraphRenderer;
