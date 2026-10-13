document.addEventListener("DOMContentLoaded", function () {
    const userDropdown = document.querySelector(".nav-user-dropdown");
    const dropdownContent = document.querySelector(".dropdown-content");

    userDropdown.addEventListener("click", function (event) {
        event.stopPropagation(); // Evita que el evento se propague y cierre el menú de inmediato
        dropdownContent.classList.toggle("show");
    });

    // Cierra el menú si se hace clic fuera de él
    document.addEventListener("click", function (event) {
        if (!userDropdown.contains(event.target)) {
            dropdownContent.classList.remove("show");
        }
    });
});
