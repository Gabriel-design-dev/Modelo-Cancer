document.addEventListener("DOMContentLoaded", function() {
    const formContainer = document.getElementById("formContainer");
    const showFormLink = document.getElementById("showFormLink");

    // Función para mostrar u ocultar el contenedor del formulario
    function toggleFormContainer() {
        formContainer.style.display = formContainer.style.display === "none" ? "block" : "none";
    }

    // Agregar el evento click al enlace de "Login/Registro"
    showFormLink.addEventListener("click", function(event) {
        event.preventDefault();
        toggleFormContainer();
    });
});
