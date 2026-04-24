document.addEventListener("DOMContentLoaded", function () {
  const container = document.querySelector(".container");
  
  // Si el backend ha pasado 'register_mode', abrir automáticamente el registro
  if (document.body.dataset.registerMode === "true") {
      container.classList.add("active");
  }

  const registerBtn = document.querySelector(".register-btn");
  const loginBtn = document.querySelector(".login-btn");

  registerBtn.addEventListener("click", () => {
      container.classList.add("active");
  });

  loginBtn.addEventListener("click", () => {
      container.classList.remove("active");
  });
});
