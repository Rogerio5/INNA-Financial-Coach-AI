document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll(".nav a");

    links.forEach((link) => {
        link.addEventListener("click", () => {
            links.forEach((item) => {
                item.classList.remove("active");
            });

            link.classList.add("active");
        });
    });

    console.log("INNA Official Platform ready.");
});
