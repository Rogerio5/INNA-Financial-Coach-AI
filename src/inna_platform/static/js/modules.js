document.addEventListener("DOMContentLoaded", () => {

    const cards = Array.from(
        document.querySelectorAll(".catalog-module-card")
    );

    const categoryButtons = Array.from(
        document.querySelectorAll(".category-chip")
    );

    const searchInput =
        document.getElementById("module-search");

    const statusFilter =
        document.getElementById("status-filter");

    const moduleCount =
        document.getElementById("module-count");

    let activeCategory = "todos";


    function normalize(value) {
        return value
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase();
    }


    function updateModules() {

        const search =
            normalize(searchInput.value.trim());

        const status =
            statusFilter.value;

        let visibleCount = 0;


        cards.forEach((card) => {

            const categories =
                card.dataset.category || "";

            const cardStatus =
                card.dataset.status || "";

            const content =
                normalize(card.textContent);


            const categoryMatch =
                activeCategory === "todos" ||
                categories.includes(activeCategory);


            const statusMatch =
                status === "todos" ||
                cardStatus === status;


            const searchMatch =
                search === "" ||
                content.includes(search);


            const visible =
                categoryMatch &&
                statusMatch &&
                searchMatch;


            card.classList.toggle(
                "hidden",
                !visible
            );


            if (visible) {
                visibleCount += 1;
            }

        });


        moduleCount.textContent =
            `${visibleCount} ${
                visibleCount === 1
                    ? "módulo"
                    : "módulos"
            }`;

    }


    categoryButtons.forEach((button) => {

        button.addEventListener(
            "click",
            () => {

                categoryButtons.forEach(
                    (item) => {
                        item.classList.remove(
                            "active"
                        );
                    }
                );


                button.classList.add(
                    "active"
                );


                activeCategory =
                    button.dataset.category;


                updateModules();

            }
        );

    });


    searchInput.addEventListener(
        "input",
        updateModules
    );


    statusFilter.addEventListener(
        "change",
        updateModules
    );


    updateModules();

});
