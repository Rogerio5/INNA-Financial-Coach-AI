export type GraphLocale =
  | "pt"
  | "en_us"
  | "en_gb"
  | "es"
  | "fr"
  | "de"
  | "it"
  | "ro"
  | "ru"
  | "ar";

const TEXT: Record<
  GraphLocale,
  Record<string, string>
> = {
  pt: {
    overview: "Visão geral",
    module_structure: "Estrutura do módulo",
    search_placeholder: "Buscar módulo, tecnologia ou finalidade",
    all_categories: "Todas as categorias",
    relationships: "Relações",
    back_overview: "← Visão geral",
    fit: "Ajustar",
    platform: "Plataforma",
    category: "Categoria",
    module: "Módulo",
    area: "Área",
    capability: "Capacidade",
    real_relationship: "Relação real",
    legend: "Legenda",
  },

  en_us: {
    overview: "Overview",
    module_structure: "Module structure",
    search_placeholder: "Search module, technology or purpose",
    all_categories: "All categories",
    relationships: "Relationships",
    back_overview: "← Overview",
    fit: "Fit",
    platform: "Platform",
    category: "Category",
    module: "Module",
    area: "Area",
    capability: "Capability",
    real_relationship: "Real relationship",
    legend: "Legend",
  },

  en_gb: {
    overview: "Overview",
    module_structure: "Module structure",
    search_placeholder: "Search module, technology or purpose",
    all_categories: "All categories",
    relationships: "Relationships",
    back_overview: "← Overview",
    fit: "Fit",
    platform: "Platform",
    category: "Category",
    module: "Module",
    area: "Area",
    capability: "Capability",
    real_relationship: "Real relationship",
    legend: "Legend",
  },

  es: {
    overview: "Vista general",
    module_structure: "Estructura del módulo",
    search_placeholder: "Buscar módulo, tecnología o finalidad",
    all_categories: "Todas las categorías",
    relationships: "Relaciones",
    back_overview: "← Vista general",
    fit: "Ajustar",
    platform: "Plataforma",
    category: "Categoría",
    module: "Módulo",
    area: "Área",
    capability: "Capacidad",
    real_relationship: "Relación real",
    legend: "Leyenda",
  },

  fr: {
    overview: "Vue d’ensemble",
    module_structure: "Structure du module",
    search_placeholder: "Rechercher un module, une technologie ou un objectif",
    all_categories: "Toutes les catégories",
    relationships: "Relations",
    back_overview: "← Vue d’ensemble",
    fit: "Ajuster",
    platform: "Plateforme",
    category: "Catégorie",
    module: "Module",
    area: "Domaine",
    capability: "Capacité",
    real_relationship: "Relation réelle",
    legend: "Légende",
  },

  de: {
    overview: "Übersicht",
    module_structure: "Modulstruktur",
    search_placeholder: "Modul, Technologie oder Zweck suchen",
    all_categories: "Alle Kategorien",
    relationships: "Beziehungen",
    back_overview: "← Übersicht",
    fit: "Einpassen",
    platform: "Plattform",
    category: "Kategorie",
    module: "Modul",
    area: "Bereich",
    capability: "Fähigkeit",
    real_relationship: "Reale Beziehung",
    legend: "Legende",
  },

  it: {
    overview: "Panoramica",
    module_structure: "Struttura del modulo",
    search_placeholder: "Cerca modulo, tecnologia o finalità",
    all_categories: "Tutte le categorie",
    relationships: "Relazioni",
    back_overview: "← Panoramica",
    fit: "Adatta",
    platform: "Piattaforma",
    category: "Categoria",
    module: "Modulo",
    area: "Area",
    capability: "Capacità",
    real_relationship: "Relazione reale",
    legend: "Legenda",
  },

  ro: {
    overview: "Prezentare generală",
    module_structure: "Structura modulului",
    search_placeholder: "Caută modul, tehnologie sau scop",
    all_categories: "Toate categoriile",
    relationships: "Relații",
    back_overview: "← Prezentare generală",
    fit: "Încadrează",
    platform: "Platformă",
    category: "Categorie",
    module: "Modul",
    area: "Arie",
    capability: "Capacitate",
    real_relationship: "Relație reală",
    legend: "Legendă",
  },

  ru: {
    overview: "Обзор",
    module_structure: "Структура модуля",
    search_placeholder: "Поиск модуля, технологии или назначения",
    all_categories: "Все категории",
    relationships: "Связи",
    back_overview: "← Обзор",
    fit: "Вместить",
    platform: "Платформа",
    category: "Категория",
    module: "Модуль",
    area: "Область",
    capability: "Возможность",
    real_relationship: "Реальная связь",
    legend: "Легенда",
  },

  ar: {
    overview: "نظرة عامة",
    module_structure: "هيكل الوحدة",
    search_placeholder: "البحث عن وحدة أو تقنية أو غرض",
    all_categories: "جميع الفئات",
    relationships: "العلاقات",
    back_overview: "← نظرة عامة",
    fit: "ملاءمة",
    platform: "المنصة",
    category: "الفئة",
    module: "الوحدة",
    area: "المجال",
    capability: "القدرة",
    real_relationship: "علاقة فعلية",
    legend: "وسيلة الإيضاح",
  },
};

export const normalizeGraphLocale = (
  value: string,
): GraphLocale => {
  const normalized = String(
    value || "pt",
  )
    .trim()
    .toLowerCase()
    .replaceAll("-", "_");

  if (
    normalized === "en" ||
    normalized === "en_us"
  ) {
    return "en_us";
  }

  if (normalized === "en_gb") {
    return "en_gb";
  }

  if (
    normalized === "sa" ||
    normalized === "ar"
  ) {
    return "ar";
  }

  if (
    Object.prototype.hasOwnProperty.call(
      TEXT,
      normalized,
    )
  ) {
    return normalized as GraphLocale;
  }

  return "pt";
};

export const graphText = (
  locale: GraphLocale,
  key: string,
): string =>
  TEXT[locale]?.[key]
  ?? TEXT.pt[key]
  ?? key;
