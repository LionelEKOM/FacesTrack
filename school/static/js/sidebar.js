/**
 * Script pour gérer l'état actif de la sidebar
 */
document.addEventListener("DOMContentLoaded", function () {
  // Fonction pour mettre à jour l'état actif de la sidebar
  function updateActiveSidebarItem() {
    // Récupérer l'URL actuelle
    const currentPath = window.location.pathname;

    // Récupérer tous les liens de la sidebar
    const sidebarLinks = document.querySelectorAll(".sidebar-nav .nav-link");

    // Retirer la classe active de tous les liens
    sidebarLinks.forEach((link) => {
      link.classList.remove("active");
    });

    // Déterminer l'élément actif en fonction de l'URL et du contexte
    let activeItem = null;

    // Cas spécial pour le dashboard admin
    if (
      currentPath === "/admin/dashboard/" ||
      currentPath === "/admin/dashboard"
    ) {
      activeItem = document.querySelector("#sidebar-dashboard");
    }
    // Cas spécial pour le dashboard enseignant
    else if (
      currentPath === "/enseignant/dashboard/" ||
      currentPath === "/enseignant/dashboard"
    ) {
      activeItem = document.querySelector("#sidebar-dashboard");
    }
    // Cas spécial pour le scan QR code
    else if (currentPath.includes("/qr-code-scan/")) {
      activeItem = document.querySelector("#sidebar-attendance");
    }
    // Cas général : essayer de faire correspondre l'URL
    else {
      sidebarLinks.forEach((link) => {
        const href = link.getAttribute("href");
        if (href && href !== "#" && currentPath.includes(href)) {
          activeItem = link;
        }
      });
    }

    // Si aucun élément actif n'a été trouvé, essayer de le déterminer par défaut
    if (!activeItem) {
      // Par défaut, activer le premier élément (généralement le dashboard)
      activeItem =
        document.querySelector("#sidebar-dashboard") || sidebarLinks[0];
    }

    // Ajouter la classe active à l'élément déterminé
    if (activeItem) {
      activeItem.classList.add("active");
    }
  }

  // Mettre à jour l'état actif au chargement de la page
  updateActiveSidebarItem();

  // Ajouter des écouteurs d'événements pour les clics sur les liens
  const sidebarLinks = document.querySelectorAll(".sidebar-nav .nav-link");
  sidebarLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      // Si le lien pointe vers #, ne pas naviguer
      if (this.getAttribute("href") === "#") {
        e.preventDefault();

        // Retirer la classe active de tous les liens
        sidebarLinks.forEach((l) => l.classList.remove("active"));

        // Ajouter la classe active au lien cliqué
        this.classList.add("active");
        return;
      }

      // Pour les liens réels, laisser la navigation se faire
      // L'état actif sera géré par la nouvelle page
    });
  });
});

/**
 * Fonction pour définir manuellement l'élément actif
 * @param {string} itemId - L'ID de l'élément à activer
 */
function setActiveSidebarItem(itemId) {
  const sidebarLinks = document.querySelectorAll(".sidebar-nav .nav-link");

  // Retirer la classe active de tous les liens
  sidebarLinks.forEach((link) => {
    link.classList.remove("active");
  });

  // Ajouter la classe active à l'élément spécifié
  const activeItem = document.querySelector(itemId);
  if (activeItem) {
    activeItem.classList.add("active");
  }
}

/**
 * Fonction pour maintenir l'état actif après rechargement
 * @param {string} itemId - L'ID de l'élément à maintenir actif
 */
function maintainActiveSidebarItem(itemId) {
  // Stocker l'élément actif dans le localStorage
  if (itemId) {
    localStorage.setItem("activeSidebarItem", itemId);
  }

  // Récupérer l'élément actif depuis le localStorage
  const storedActiveItem = localStorage.getItem("activeSidebarItem");
  if (storedActiveItem) {
    setActiveSidebarItem(storedActiveItem);
  }
}
