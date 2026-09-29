/* O botão ocupa espaço no cabeçalho, antes dos indicadores. */
(function () {
    "use strict";
    if (window.SabinoInnaTopPositionV1) return;
    window.SabinoInnaTopPositionV1 = true;
    function mount() {
        const button = document.querySelector(".inna-top");
        const header = document.querySelector("main.main > .page-header");
        if (!button || !header) return;
        if (button.parentElement !== header) header.appendChild(button);
        ["position", "top", "right", "bottom", "left", "transform", "translate"]
            .forEach(property => button.style.removeProperty(property));
    }
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", mount, { once: true });
    } else {
        mount();
    }
})();
