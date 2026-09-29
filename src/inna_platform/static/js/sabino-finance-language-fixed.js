(() => {
    "use strict";

    function findLanguageNode() {
        const selectors = [
            "#sabino-language-button-mount",
            ".sabino-language-button-mount",
            ".sabino-language-button",
            ".language-button-shell",
            ".language-selector-shell",
            "[data-sabino-language-button]",
            "[data-language-selector]"
        ];

        for (const selector of selectors) {
            const found = document.querySelector(selector);
            if (found) return found;
        }

        return null;
    }

    function fixLanguageButton() {
        const node = findLanguageNode();
        if (!node) return;

        if (!node.classList.contains("sabino-finance-language-fixed")) {
            node.classList.add("sabino-finance-language-fixed");
        }

        if (node.parentElement !== document.body) {
            document.body.appendChild(node);
        }

        node.style.position = "fixed";
        node.style.top = "20px";
        node.style.right = "24px";
        node.style.left = "auto";
        node.style.bottom = "auto";
        node.style.margin = "0";
        node.style.zIndex = "99999";
        node.style.transform = "none";
    }

    function removeDuplicates() {
        const nodes = Array.from(document.querySelectorAll(
            "#sabino-language-button-mount, .sabino-language-button-mount, .sabino-language-button"
        ));

        if (nodes.length <= 1) return;

        const keep = nodes.find(n => n.classList.contains("sabino-finance-language-fixed")) || nodes[0];

        nodes.forEach(node => {
            if (node !== keep) {
                node.remove();
            }
        });
    }

    function boot() {
        fixLanguageButton();
        removeDuplicates();
    }

    document.addEventListener("DOMContentLoaded", boot);
    window.addEventListener("load", boot);

    const observer = new MutationObserver(() => {
        boot();
    });

    observer.observe(document.documentElement, {
        childList: true,
        subtree: true
    });
})();
