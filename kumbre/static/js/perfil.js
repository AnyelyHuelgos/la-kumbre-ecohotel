document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const passwordInputs = form.querySelectorAll("input[type='password']");

    // Crear un espacio para los mensajes de error
    passwordInputs.forEach(input => {
        let errorMsg = document.createElement("p");
        errorMsg.classList.add("error-message");
        errorMsg.style.color = "red";
        errorMsg.style.fontSize = "14px";
        errorMsg.style.marginTop = "5px";
        input.parentNode.appendChild(errorMsg);
    });

    form.addEventListener("submit", function (event) {
        let valid = true;

        passwordInputs.forEach(input => {
            let errorMsg = input.parentNode.querySelector(".error-message");
            errorMsg.textContent = ""; // Limpiar mensajes anteriores

            if (input.value.trim() === "") {
                valid = false;
                errorMsg.textContent = "⚠️ Este campo es obligatorio.";
            }
        });

        if (passwordInputs[0].value.length < 4) {
            valid = false;
            passwordInputs[0].parentNode.querySelector(".error-message").textContent = "⚠️ La nueva contraseña debe tener al menos 6 caracteres.";
        }

        if (!valid) {
            event.preventDefault();
        }
    });
});
