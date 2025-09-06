// Animation des champs de saisie
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".form-control").forEach((input) => {
    input.addEventListener("focus", function () {
      this.parentElement.classList.add("focused");
    });

    input.addEventListener("blur", function () {
      if (!this.value) {
        this.parentElement.classList.remove("focused");
      }
    });
  });

  // Validation en temps réel
  document.querySelector("form").addEventListener("submit", function (e) {
    const username = document.getElementById("id_username").value.trim();
    const password = document.getElementById("id_password").value.trim();

    if (!username || !password) {
      e.preventDefault();
      alert("Veuillez remplir tous les champs");
      return false;
    }
  });
});
