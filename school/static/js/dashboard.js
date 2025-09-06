// Dashboard JavaScript
document.addEventListener("DOMContentLoaded", function () {
  // Toggle sidebar on mobile
  const sidebarToggle = document.querySelector(".sidebar-toggle");
  const sidebar = document.querySelector(".dashboard-sidebar");

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", function () {
      sidebar.classList.toggle("open");
    });
  }

  // Close sidebar when clicking outside on mobile
  document.addEventListener("click", function (e) {
    if (window.innerWidth <= 1024) {
      if (!sidebar.contains(e.target) && !sidebarToggle?.contains(e.target)) {
        sidebar.classList.remove("open");
      }
    }
  });

  // Active navigation link
  const navLinks = document.querySelectorAll(".sidebar-nav .nav-link");
  navLinks.forEach((link) => {
    if (link.href === window.location.href) {
      link.classList.add("active");
    }
  });

  // Profile dropdown - Laisser Bootstrap gérer la dropdown
  // Le code personnalisé a été supprimé pour éviter les conflits avec Bootstrap

  // Dashboard cards animation
  const cards = document.querySelectorAll(".dashboard-card");
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  }, observerOptions);

  cards.forEach((card) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(20px)";
    card.style.transition = "all 0.6s ease";
    observer.observe(card);
  });

  // Chart.js integration (if available)
  if (typeof Chart !== "undefined") {
    initializeCharts();
  }

  // Auto-refresh dashboard data
  setInterval(refreshDashboardData, 300000); // Refresh every 5 minutes
});

// Initialize charts
function initializeCharts() {
  // Presence chart
  const presenceCtx = document.getElementById("presenceChart");
  if (presenceCtx) {
    new Chart(presenceCtx, {
      type: "line",
      data: {
        labels: ["Lun", "Mar", "Mer", "Jeu", "Ven"],
        datasets: [
          {
            label: "Taux de présence (%)",
            data: [95, 92, 88, 94, 96],
            borderColor: "#f79320",
            backgroundColor: "rgba(247, 147, 32, 0.1)",
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
          },
        },
      },
    });
  }

  // Absence chart
  const absenceCtx = document.getElementById("absenceChart");
  if (absenceCtx) {
    new Chart(absenceCtx, {
      type: "bar",
      data: {
        labels: ["6ème", "5ème", "4ème", "3ème"],
        datasets: [
          {
            label: "Absences",
            data: [12, 8, 15, 10],
            backgroundColor: "#00bf63",
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false,
          },
        },
      },
    });
  }
}

// Refresh dashboard data
function refreshDashboardData() {
  // This function would typically make an AJAX call to refresh data
  console.log("Refreshing dashboard data...");

  // Example: Update statistics
  const statCards = document.querySelectorAll(".card-value");
  statCards.forEach((card) => {
    // Simulate data update
    if (card.textContent.includes("%")) {
      const currentValue = parseInt(card.textContent);
      const newValue = Math.max(
        80,
        Math.min(100, currentValue + (Math.random() - 0.5) * 10)
      );
      card.textContent = Math.round(newValue) + "%";
    }
  });
}

// Export functionality
function exportData(format) {
  console.log(`Exporting data in ${format} format...`);
  // Implementation would depend on backend API
}

// Notification system
function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  notification.style.cssText =
    "top: 80px; right: 20px; z-index: 9999; min-width: 300px;";
  notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  document.body.appendChild(notification);

  // Auto-remove after 5 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 5000);
}

// Utility functions
function formatDate(date) {
  return new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);
}

function formatTime(date) {
  return new Intl.DateTimeFormat("fr-FR", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
