(() => {
  "use strict";

  const MARKER = "SABINO_GLOBAL_I18N_RUNTIME_V1";
  const VERSION = "1.0.0";

  if (window.__SABINO_GLOBAL_I18N_RUNTIME_V1__) {
    return;
  }

  window.__SABINO_GLOBAL_I18N_RUNTIME_V1__ = true;

  const SOURCE_LOCALE = "pt-BR";

  const MANUAL_LANGUAGE_KEY =
    "sabino_language_manual";

  const ACTIVE_LANGUAGE_KEY =
    "sabino_language";

  const catalogs = new Map();

  const textSources =
    new WeakMap();

  const attributeSources =
    new WeakMap();

  let applying = false;

  let observer = null;

  let scheduled = null;

  let currentLocale =
    SOURCE_LOCALE;

  let currentCatalog =
    null;


  // ========================================================
  // LOCALE
  // ========================================================

  function canonicalLocale(value) {

    const raw =
      String(value || "")
        .trim()
        .replace("_", "-");

    if (!raw) {
      return SOURCE_LOCALE;
    }

    try {

      return Intl
        .getCanonicalLocales(raw)[0];

    } catch {

      return raw;
    }
  }


  function activeLocale() {

    const manual =
      localStorage.getItem(
        MANUAL_LANGUAGE_KEY
      );

    const active =
      localStorage.getItem(
        ACTIVE_LANGUAGE_KEY
      );

    const html =
      document.documentElement.lang;

    const browser =
      (
        navigator.languages &&
        navigator.languages.length
      )
        ? navigator.languages[0]
        : navigator.language;

    /*
     * SABINO_I18N_SHARED_STORAGE_V5
     *
     * Ordem:
     * 1. escolha manual da plataforma
     * 2. idioma ativo compartilhado
     * 3. idioma do documento
     * 4. navegador
     */

    return canonicalLocale(
      manual ||
      active ||
      html ||
      browser ||
      SOURCE_LOCALE
    );
  }


  function catalogLocale(locale) {

    const normalized =
      canonicalLocale(locale);

    /*
     * SABINO_GLOBAL_CATALOG_MAP_V8
     */

    const exact = new Set([
      "pt-PT",
      "en-US",
      "en-GB",
      "en-CA",
      "en-AU",
      "en-NZ",
      "en-IN",
      "es-ES",
      "es-MX",
      "fr-FR",
      "de-DE",
      "it-IT",
      "ro-RO",
      "ru-RU",
      "ar-SA"
    ]);

    if (exact.has(normalized)) {
      return normalized;
    }

    if (
      normalized === "pt" ||
      normalized === "pt-BR"
    ) {
      return null;
    }

    const base =
      normalized.split("-")[0];

    const fallback = {
      en: "en-US",
      es: "es-ES",
      fr: "fr-FR",
      de: "de-DE",
      it: "it-IT",
      ro: "ro-RO",
      ru: "ru-RU",
      ar: "ar-SA"
    };

    return fallback[base] || null;
  }


  // ========================================================
  // CATALOG
  // ========================================================

  async function loadCatalog(locale) {

    const target =
      catalogLocale(locale);

    if (!target) {
      return null;
    }

    if (catalogs.has(target)) {
      return catalogs.get(target);
    }

    const response =
      await fetch(
        `/static/i18n/${target}.json`,
        {
          cache: "no-cache"
        }
      );

    if (!response.ok) {

      throw new Error(
        `i18n catalog ${target}: HTTP ${response.status}`
      );
    }

    const payload =
      await response.json();

    const translations =
      payload &&
      payload.translations
        ? payload.translations
        : {};

    catalogs.set(
      target,
      translations
    );

    return translations;
  }


  // ========================================================
  // DOM HELPERS
  // ========================================================

  function normalize(value) {

    return String(value || "")
      .replace(/\s+/g, " ")
      .trim();
  }


  function shouldSkipElement(element) {

    if (!element) {
      return true;
    }

    return Boolean(
      element.closest(
        "script,style,noscript,template,svg"
      )
    );
  }


  function preserveWhitespace(
    original,
    translated
  ) {

    const value =
      String(original || "");

    const start =
      value.match(/^\s*/)?.[0] || "";

    const end =
      value.match(/\s*$/)?.[0] || "";

    return (
      start +
      translated +
      end
    );
  }


  function translationFor(
    source,
    catalog
  ) {

    if (!catalog) {
      return null;
    }

    const key =
      normalize(source);

    if (!key) {
      return null;
    }

    const translated =
      catalog[key];

    if (
      typeof translated !== "string" ||
      !translated.trim()
    ) {
      return null;
    }

    return translated;
  }


  // ========================================================
  // TEXT NODES
  // ========================================================

  function captureTextSource(node) {

    if (!node) {
      return null;
    }

    const current =
      node.nodeValue || "";

    const normalized =
      normalize(current);

    if (!normalized) {
      return null;
    }

    const previous =
      textSources.get(node);

    if (!previous) {

      textSources.set(
        node,
        current
      );

      return current;
    }

    if (
      currentCatalog &&
      translationFor(
        previous,
        currentCatalog
      ) === normalized
    ) {

      return previous;
    }

    const previousNormalized =
      normalize(previous);

    if (
      normalized !==
      previousNormalized
    ) {

      const values =
        currentCatalog
          ? Object.values(
              currentCatalog
            )
          : [];

      const alreadyTranslated =
        values.includes(
          normalized
        );

      if (!alreadyTranslated) {

        textSources.set(
          node,
          current
        );

        return current;
      }
    }

    return previous;
  }


  function translateTextNode(
    node,
    catalog
  ) {

    if (
      !node ||
      !node.parentElement ||
      shouldSkipElement(
        node.parentElement
      )
    ) {
      return;
    }

    const source =
      captureTextSource(node);

    if (!source) {
      return;
    }

    if (!catalog) {

      if (
        node.nodeValue !==
        source
      ) {

        node.nodeValue =
          source;
      }

      return;
    }

    const translated =
      translationFor(
        source,
        catalog
      );

    if (!translated) {

      if (
        node.nodeValue !==
        source
      ) {

        node.nodeValue =
          source;
      }

      return;
    }

    const rendered =
      preserveWhitespace(
        source,
        translated
      );

    if (
      node.nodeValue !==
      rendered
    ) {

      node.nodeValue =
        rendered;
    }
  }


  // ========================================================
  // ATTRIBUTES
  // ========================================================

  const ATTRIBUTES = [
    "placeholder",
    "title",
    "aria-label"
  ];


  function sourceAttributes(
    element
  ) {

    let sources =
      attributeSources.get(
        element
      );

    if (!sources) {

      sources = {};

      attributeSources.set(
        element,
        sources
      );
    }

    return sources;
  }


  function translateAttribute(
    element,
    attribute,
    catalog
  ) {

    if (
      !element ||
      !element.hasAttribute(
        attribute
      )
    ) {
      return;
    }

    if (
      shouldSkipElement(
        element
      )
    ) {
      return;
    }

    const sources =
      sourceAttributes(
        element
      );

    const current =
      element.getAttribute(
        attribute
      ) || "";

    if (
      !sources[attribute]
    ) {

      sources[attribute] =
        current;
    }

    const source =
      sources[attribute];

    if (!catalog) {

      if (
        current !==
        source
      ) {

        element.setAttribute(
          attribute,
          source
        );
      }

      return;
    }

    const translated =
      translationFor(
        source,
        catalog
      );

    if (!translated) {
      return;
    }

    if (
      current !==
      translated
    ) {

      element.setAttribute(
        attribute,
        translated
      );
    }
  }


  // ========================================================
  // SCAN
  // ========================================================

  function scanTextNodes(
    root,
    catalog
  ) {

    if (!root) {
      return;
    }

    if (
      root.nodeType ===
      Node.TEXT_NODE
    ) {

      translateTextNode(
        root,
        catalog
      );

      return;
    }

    if (
      root.nodeType !==
      Node.ELEMENT_NODE &&
      root.nodeType !==
      Node.DOCUMENT_NODE &&
      root.nodeType !==
      Node.DOCUMENT_FRAGMENT_NODE
    ) {
      return;
    }

    const walker =
      document.createTreeWalker(
        root,
        NodeFilter.SHOW_TEXT
      );

    let node =
      walker.nextNode();

    while (node) {

      translateTextNode(
        node,
        catalog
      );

      node =
        walker.nextNode();
    }
  }


  function scanAttributes(
    root,
    catalog
  ) {

    if (!root) {
      return;
    }

    const elements = [];

    if (
      root.nodeType ===
      Node.ELEMENT_NODE
    ) {

      elements.push(root);
    }

    if (
      root.querySelectorAll
    ) {

      elements.push(
        ...root.querySelectorAll("*")
      );
    }

    for (
      const element
      of elements
    ) {

      for (
        const attribute
        of ATTRIBUTES
      ) {

        translateAttribute(
          element,
          attribute,
          catalog
        );
      }
    }
  }


  function applyToDom(
    catalog
  ) {

    applying = true;

    try {

      scanTextNodes(
        document.documentElement,
        catalog
      );

      scanAttributes(
        document.documentElement,
        catalog
      );

    } finally {

      applying = false;
    }
  }


  // ========================================================
  // HEADER COLLISION GUARD
  // ========================================================

  function languageControl() {

    return document.querySelector(
      ".sabino-global-language"
    );
  }


  function visibleRect(element) {

    if (!element) {
      return null;
    }

    const style =
      getComputedStyle(
        element
      );

    if (
      style.display === "none" ||
      style.visibility === "hidden" ||
      Number(style.opacity) === 0
    ) {
      return null;
    }

    const rect =
      element.getBoundingClientRect();

    if (
      rect.width < 1 ||
      rect.height < 1
    ) {
      return null;
    }

    return rect;
  }


  function candidateAncestor(
    element,
    language
  ) {

    let current =
      element;

    let best =
      null;

    for (
      let level = 0;
      level < 5 && current;
      level += 1
    ) {

      if (
        current === language ||
        language.contains(current) ||
        current.contains(language)
      ) {
        break;
      }

      const rect =
        visibleRect(current);

      if (
        rect &&
        rect.width >= 28 &&
        rect.width <= 480 &&
        rect.height >= 20 &&
        rect.height <= 140 &&
        rect.top < 130 &&
        rect.right >
          window.innerWidth * 0.55
      ) {

        best =
          current;
      }

      current =
        current.parentElement;
    }

    return best;
  }


  function adjustLanguagePosition() {
    if (document.documentElement.dataset.financeHeader === "flow") return;

    const language =
      languageControl();

    if (!language) {
      return;
    }

    language.style.removeProperty(
      "left"
    );

    language.style.removeProperty(
      "right"
    );

    requestAnimationFrame(
      () => {

        const rect =
          visibleRect(
            language
          );

        if (!rect) {
          return;
        }

        const points = [
          [
            rect.left + 6,
            rect.top + 6
          ],
          [
            rect.right - 6,
            rect.top + 6
          ],
          [
            rect.left +
              rect.width / 2,
            rect.top +
              rect.height / 2
          ],
          [
            rect.left + 6,
            rect.bottom - 6
          ],
          [
            rect.right - 6,
            rect.bottom - 6
          ]
        ];

        const candidates =
          new Set();

        for (
          const [x, y]
          of points
        ) {

          for (
            const element
            of document.elementsFromPoint(
              x,
              y
            )
          ) {

            if (
              element === language ||
              language.contains(
                element
              )
            ) {
              continue;
            }

            const candidate =
              candidateAncestor(
                element,
                language
              );

            if (candidate) {

              candidates.add(
                candidate
              );
            }
          }
        }

        if (
          candidates.size === 0
        ) {
          return;
        }

        let target =
          null;

        let targetRect =
          null;

        for (
          const candidate
          of candidates
        ) {

          const candidateRect =
            visibleRect(
              candidate
            );

          if (!candidateRect) {
            continue;
          }

          if (
            !targetRect ||
            candidateRect.width >
              targetRect.width
          ) {

            target =
              candidate;

            targetRect =
              candidateRect;
          }
        }

        if (
          !target ||
          !targetRect
        ) {
          return;
        }

        let desiredRight =
          window.innerWidth -
          targetRect.left +
          12;

        const maxRight =
          Math.max(
            12,
            window.innerWidth -
            rect.width -
            12
          );

        desiredRight =
          Math.max(
            12,
            Math.min(
              desiredRight,
              maxRight
            )
          );

        language.style.right =
          `${desiredRight}px`;

        language.dataset
          .sabinoCollisionGuard =
          "active";
      }
    );
  }


  // ========================================================
  // REFRESH
  // ========================================================

  async function refresh() {

    const locale =
      activeLocale();

    currentLocale =
      locale;

    try {

      currentCatalog =
        await loadCatalog(
          locale
        );

    } catch (error) {

      console.error(
        "[SabinoGlobalI18n]",
        error
      );

      currentCatalog =
        null;
    }

    document.documentElement.lang =
      locale;

    applyToDom(
      currentCatalog
    );

    adjustLanguagePosition();

    window.dispatchEvent(
      new CustomEvent(
        "sabino:i18n-rendered",
        {
          detail: {
            locale:
              currentLocale,

            catalog:
              catalogLocale(
                currentLocale
              ),

            translated:
              Boolean(
                currentCatalog
              )
          }
        }
      )
    );
  }


  function scheduleRefresh() {

    clearTimeout(
      scheduled
    );

    scheduled =
      setTimeout(
        refresh,
        40
      );
  }


  // ========================================================
  // OBSERVER
  // ========================================================

  function startObserver() {

    if (
      observer ||
      !document.documentElement
    ) {
      return;
    }

    observer =
      new MutationObserver(
        mutations => {

          if (applying) {
            return;
          }

          let changed =
            false;

          for (
            const mutation
            of mutations
          ) {

            if (
              mutation.type ===
              "characterData"
            ) {

              textSources.delete(
                mutation.target
              );

              changed =
                true;
            }

            if (
              mutation.type ===
              "childList"
            ) {

              changed =
                true;
            }

            if (
              mutation.type ===
              "attributes"
            ) {

              attributeSources.delete(
                mutation.target
              );

              changed =
                true;
            }
          }

          if (changed) {

            scheduleRefresh();
          }
        }
      );


    observer.observe(
      document.documentElement,
      {
        subtree:
          true,

        childList:
          true,

        characterData:
          true,

        attributes:
          true,

        attributeFilter: [
          "placeholder",
          "title",
          "aria-label"
        ]
      }
    );
  }


  // ========================================================
  // EVENTS
  // ========================================================

  window.addEventListener(
    "sabino:locale-change",
    function (event) {

      /*
       * SABINO_I18N_EVENT_BRIDGE_V5
       *
       * sabino-locale-core.js já envia:
       *
       * event.detail.locale
       *
       * Portanto não precisamos inferir o idioma
       * pelo texto do botão.
       */

      const detail =
        event &&
        event.detail
          ?
          event.detail
          :
          null;


      const received =
        (
          detail &&
          typeof detail === "object"
        )
        ?
          (
            detail.locale
            ||
            detail.language
            ||
            detail.lang
            ||
            null
          )
        :
          (
            typeof detail === "string"
              ?
              detail
              :
              null
          );


      if (received) {

        console.log(
          "SABINO_I18N_LOCALE_EVENT_V5",
          received
        );

      }


      scheduleRefresh();

    }
  );


  /*
   * O sistema legado/atual de i18n usa
   * sabino:languagechange.
   *
   * Fazemos a mesma ponte aqui.
   */

  /*
   * SABINO_DIRECT_LOCALE_RENDER_V7
   *
   * O seletor interno já envia o locale correto
   * em event.detail.locale.
   *
   * Aqui usamos esse valor diretamente para o
   * catálogo e para a renderização.
   */
  function handleDirectLanguageChange(
    event
  ) {

    const detail =
      event &&
      event.detail
        ?
        event.detail
        :
        null;


    const received =
      detail &&
      typeof detail === "object"
        ?
        (
          detail.locale
          ||
          detail.language
          ||
          detail.lang
          ||
          null
        )
        :
        (
          typeof detail === "string"
            ?
            detail
            :
            null
        );


    if (!received) {

      scheduleRefresh();

      return;
    }


    const normalized =
      canonicalLocale(
        received
      );


    if (!normalized) {

      scheduleRefresh();

      return;
    }


    currentLocale =
      normalized;


    console.log(
      "SABINO_DIRECT_LOCALE_RENDER_V7",
      normalized
    );


    /*
     * O evento representa uma escolha explícita
     * feita pelo usuário no seletor da plataforma.
     */
    try {

      localStorage.setItem(
        LANGUAGE_KEY,
        normalized
      );

      localStorage.setItem(
        MANUAL_LANGUAGE_KEY,
        normalized
      );

    }
    catch (_) {
      // storage indisponível não interrompe a troca.
    }


    /*
     * Faz a renderização imediatamente,
     * sem depender de uma nova leitura do locale.
     */
    applyLocale();

  }


  window.addEventListener(
    "sabino:languagechange",
    function (event) {

      /*
       * SABINO_I18N_LANGUAGE_EVENT_BRIDGE_V5
       */

      const detail =
        event &&
        event.detail
          ?
          event.detail
          :
          null;


      const received =
        (
          detail &&
          typeof detail === "object"
        )
        ?
          (
            detail.locale
            ||
            detail.language
            ||
            detail.lang
            ||
            null
          )
        :
          (
            typeof detail === "string"
              ?
              detail
              :
              null
          );


      if (received) {

        console.log(
          "SABINO_I18N_LANGUAGE_EVENT_V5",
          received
        );

      }


      scheduleRefresh();

    }
  );


  window.addEventListener(
    "storage",
    event => {

      if (
        event.key ===
          MANUAL_LANGUAGE_KEY ||
        event.key ===
          ACTIVE_LANGUAGE_KEY
      ) {

        scheduleRefresh();
      }
    }
  );


  window.addEventListener(
    "resize",
    () => {

      clearTimeout(
        window
          .__sabinoI18nResizeTimer
      );

      window
        .__sabinoI18nResizeTimer =
        setTimeout(
          adjustLanguagePosition,
          80
        );
    }
  );


  // ========================================================
  // PUBLIC API
  // ========================================================

  window.SabinoGlobalI18n = {

    marker:
      MARKER,

    version:
      VERSION,

    refresh,

    locale:
      () =>
        currentLocale,

    status:
      () => ({
        version:
          VERSION,

        locale:
          currentLocale,

        catalogLocale:
          catalogLocale(
            currentLocale
          ),

        translated:
          Boolean(
            currentCatalog
          ),

        catalogEntries:
          currentCatalog
            ? Object.keys(
                currentCatalog
              ).length
            : 0,

        headerCollisionGuard:
          languageControl()
            ?.dataset
            ?.sabinoCollisionGuard
            ||
            "idle"
      })
  };


  // ========================================================
  // START
  // ========================================================

  function start() {

    startObserver();

    refresh();

    setTimeout(
      adjustLanguagePosition,
      150
    );

    setTimeout(
      adjustLanguagePosition,
      500
    );
  }


  if (
    document.readyState ===
    "loading"
  ) {

    document.addEventListener(
      "DOMContentLoaded",
      start,
      {
        once:
          true
      }
    );

  } else {

    start();
  }

})();
