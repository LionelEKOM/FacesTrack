// ========================================
// RECONNAISSANCE FACIALE AMÉLIORÉE FACETRACK
// ========================================

class FacialRecognitionImproved {
  constructor() {
    this.video = document.getElementById("video");
    this.canvas = document.getElementById("canvas");
    this.ctx = this.canvas.getContext("2d");
    this.stream = null;
    this.isActive = false;
    this.recognitionInterval = null;
    this.sessionId = null;
    this.students = [];
    this.attendanceData = {};
    this.lastRecognitionTime = 0;
    this.recognitionCooldown = 2000; // 2 secondes entre les reconnaissances

    this.initialize();
  }

  async initialize() {
    try {
      // Récupérer l'ID de session depuis l'URL ou les données de la page
      this.sessionId = this.getSessionId();

      // Initialiser la caméra
      await this.initializeCamera();

      // Charger les données des élèves
      await this.loadStudentsData();

      // Initialiser les événements
      this.initializeEvents();

      this.logMessage("Système de reconnaissance faciale amélioré initialisé");
    } catch (error) {
      console.error("Erreur d'initialisation:", error);
      this.logMessage("Erreur d'initialisation: " + error.message);
    }
  }

  getSessionId() {
    // Récupérer l'ID de session depuis les données de la page
    const sessionElement = document.querySelector("[data-session-id]");
    if (sessionElement) {
      return sessionElement.dataset.sessionId;
    }

    // Fallback: essayer de récupérer depuis l'URL
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get("session_id");
  }

  async initializeCamera() {
    try {
      const constraints = {
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "user",
        },
      };

      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.video.srcObject = this.stream;

      // Attendre que la vidéo soit prête
      return new Promise((resolve) => {
        this.video.onloadedmetadata = () => {
          this.video.play();
          this.hideCameraStatus();
          resolve();
        };
      });
    } catch (error) {
      throw new Error("Impossible d'accéder à la caméra: " + error.message);
    }
  }

  async loadStudentsData() {
    try {
      // Charger les données des élèves depuis le DOM
      this.students = Array.from(
        document.querySelectorAll("#studentsTableBody tr")
      ).map((row) => {
        const studentId = row.dataset.studentId;
        const name = row.cells[1].textContent.trim();
        const matricule = row.cells[2].textContent.trim();
        const photoElement = row.querySelector("img");
        const photoUrl = photoElement ? photoElement.src : null;

        return {
          id: studentId,
          name: name,
          matricule: matricule,
          photoUrl: photoUrl,
          status: "ABSENT",
        };
      });

      // Initialiser les données de présence
      this.students.forEach((student) => {
        this.attendanceData[student.id] = {
          status: "ABSENT",
          time: null,
          confidence: 0,
        };
      });

      this.updateStatistics();
      this.logMessage(`Chargement de ${this.students.length} élèves`);
    } catch (error) {
      console.error("Erreur de chargement des élèves:", error);
      this.logMessage("Erreur de chargement des élèves: " + error.message);
    }
  }

  initializeEvents() {
    // Événements pour les boutons de contrôle
    const startBtn = document.getElementById("startRecognition");
    if (startBtn) {
      startBtn.addEventListener("click", () => {
        this.startRecognition();
      });
    }

    const validateBtn = document.getElementById("validateCall");
    if (validateBtn) {
      validateBtn.addEventListener("click", () => {
        this.validateCall();
      });
    }

    // Événements pour les contrôles manuels
    this.initializeManualControls();
  }

  initializeManualControls() {
    // Ajouter les événements pour les boutons manuels
    document.querySelectorAll('[onclick*="markPresent"]').forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const studentId = btn.closest("tr").dataset.studentId;
        this.markPresent(studentId);
      });
    });

    document.querySelectorAll('[onclick*="markLate"]').forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const studentId = btn.closest("tr").dataset.studentId;
        this.markLate(studentId);
      });
    });

    document.querySelectorAll('[onclick*="markAbsent"]').forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const studentId = btn.closest("tr").dataset.studentId;
        this.markAbsent(studentId);
      });
    });
  }

  async startRecognition() {
    if (this.isActive) {
      this.stopRecognition();
      return;
    }

    try {
      this.isActive = true;
      this.showRecognitionActive();
      this.logMessage("Démarrage de la reconnaissance faciale...");

      // Démarrer la capture d'images
      this.recognitionInterval = setInterval(() => {
        this.captureAndRecognize();
      }, 1000); // Capture toutes les secondes

      // Mettre à jour le bouton
      const startBtn = document.getElementById("startRecognition");
      if (startBtn) {
        startBtn.innerHTML =
          '<i class="fas fa-stop me-2"></i>Arrêter la reconnaissance';
        startBtn.classList.remove("btn-success");
        startBtn.classList.add("btn-danger");
      }

      this.logMessage("Reconnaissance faciale active");
    } catch (error) {
      console.error("Erreur lors du démarrage:", error);
      this.logMessage("Erreur lors du démarrage: " + error.message);
      this.isActive = false;
    }
  }

  stopRecognition() {
    this.isActive = false;
    this.hideRecognitionActive();

    if (this.recognitionInterval) {
      clearInterval(this.recognitionInterval);
      this.recognitionInterval = null;
    }

    // Mettre à jour le bouton
    const startBtn = document.getElementById("startRecognition");
    if (startBtn) {
      startBtn.innerHTML = '<i class="fas fa-play me-2"></i>Démarrer l\'appel';
      startBtn.classList.remove("btn-danger");
      startBtn.classList.add("btn-success");
    }

    this.logMessage("Reconnaissance faciale arrêtée");
  }

  async captureAndRecognize() {
    if (!this.isActive || !this.video.videoWidth) {
      return;
    }

    // Vérifier le cooldown
    const now = Date.now();
    if (now - this.lastRecognitionTime < this.recognitionCooldown) {
      return;
    }

    try {
      // Capturer l'image de la vidéo
      this.canvas.width = this.video.videoWidth;
      this.canvas.height = this.video.videoHeight;
      this.ctx.drawImage(this.video, 0, 0);

      // Convertir en base64
      const imageData = this.canvas.toDataURL("image/jpeg", 0.8);

      // Envoyer à l'API de reconnaissance
      await this.sendToRecognitionAPI(imageData);

      this.lastRecognitionTime = now;
    } catch (error) {
      console.error("Erreur lors de la reconnaissance:", error);
    }
  }

  async sendToRecognitionAPI(imageData) {
    try {
      // Afficher un indicateur de traitement
      this.showProcessingIndicator();

      const response = await fetch("/api/facial-recognition/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.getCSRFToken(),
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          image: imageData,
        }),
      });

      const data = await response.json();

      if (data.success) {
        if (data.total_faces > 0) {
          this.handleRecognitionResults(data.detected_faces);
          this.logMessage(
            `Détection réussie: ${data.total_faces} visage(s) détecté(s)`
          );
        } else {
          // Aucun visage détecté
          this.logMessage(data.message || "Aucun visage détecté");
          this.showNoFaceDetected();
        }
      } else {
        console.error("Erreur API:", data.error);
        this.logMessage(
          "Erreur de reconnaissance: " + (data.error || "Erreur inconnue")
        );
        this.showErrorMessage("Erreur lors de la reconnaissance faciale");
      }
    } catch (error) {
      console.error("Erreur lors de l'envoi à l'API:", error);
      this.logMessage("Erreur de connexion à l'API: " + error.message);
      this.showErrorMessage("Erreur de connexion au serveur");
    } finally {
      // Masquer l'indicateur de traitement
      this.hideProcessingIndicator();
    }
  }

  handleRecognitionResults(detectedFaces) {
    detectedFaces.forEach((face) => {
      if (face.eleve_id && face.confidence > 0.6) {
        this.updateStudentStatus(face.eleve_id, "PRESENT", face.confidence);
        this.showLastRecognition(face);
        this.logMessage(
          `Reconnaissance: ${face.name} (${Math.round(face.confidence * 100)}%)`
        );
      }
    });
  }

  updateStudentStatus(studentId, status, confidence = 0) {
    // Mettre à jour les données internes
    this.attendanceData[studentId] = {
      status: status,
      time: new Date().toLocaleTimeString("fr-FR", {
        hour: "2-digit",
        minute: "2-digit",
      }),
      confidence: confidence,
    };

    // Mettre à jour l'interface
    const statusElement = document.getElementById(`status-${studentId}`);
    const timeElement = document.getElementById(`time-${studentId}`);

    if (statusElement) {
      statusElement.className = `status-badge status-${status.toLowerCase()}`;
      statusElement.textContent = this.getStatusDisplay(status);
    }

    if (timeElement) {
      timeElement.textContent = this.attendanceData[studentId].time;
    }

    // Mettre à jour les statistiques
    this.updateStatistics();
  }

  showLastRecognition(face) {
    const lastRecognitionDiv = document.getElementById("lastRecognition");
    if (lastRecognitionDiv) {
      lastRecognitionDiv.innerHTML = `
                <div class="text-center">
                    <div class="recognition-avatar mb-3">
                        <i class="fas fa-user-graduate fa-3x text-success"></i>
                    </div>
                    <h5 class="mb-2">${face.name}</h5>
                    <p class="text-muted mb-1">Confiance: ${Math.round(
                      face.confidence * 100
                    )}%</p>
                    <small class="text-success">Présent détecté</small>
                </div>
            `;
    }
  }

  getStatusDisplay(status) {
    const statusMap = {
      PRESENT: "Présent",
      LATE: "Retard",
      ABSENT: "Absent",
    };
    return statusMap[status] || status;
  }

  updateStatistics() {
    const stats = {
      present: 0,
      late: 0,
      absent: 0,
    };

    Object.values(this.attendanceData).forEach((data) => {
      if (data.status === "PRESENT") stats.present++;
      else if (data.status === "LATE") stats.late++;
      else stats.absent++;
    });

    // Mettre à jour les compteurs
    document.getElementById("presentCount").textContent = stats.present;
    document.getElementById("lateCount").textContent = stats.late;
    document.getElementById("absentCount").textContent = stats.absent;
  }

  // Contrôles manuels
  async markPresent(studentId) {
    await this.updatePresenceAPI(studentId, "PRESENT");
    this.updateStudentStatus(studentId, "PRESENT");
    this.logMessage(
      `Marqué présent manuellement: ${this.getStudentName(studentId)}`
    );
  }

  async markLate(studentId) {
    await this.updatePresenceAPI(studentId, "LATE");
    this.updateStudentStatus(studentId, "LATE");
    this.logMessage(
      `Marqué en retard manuellement: ${this.getStudentName(studentId)}`
    );
  }

  async markAbsent(studentId) {
    await this.updatePresenceAPI(studentId, "ABSENT");
    this.updateStudentStatus(studentId, "ABSENT");
    this.logMessage(
      `Marqué absent manuellement: ${this.getStudentName(studentId)}`
    );
  }

  async updatePresenceAPI(studentId, status) {
    try {
      const response = await fetch("/api/update-presence/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.getCSRFToken(),
        },
        body: JSON.stringify({
          presence_id: studentId,
          statut: status,
        }),
      });

      const data = await response.json();
      if (!data.success) {
        console.error("Erreur mise à jour présence:", data.error);
      }
    } catch (error) {
      console.error("Erreur API mise à jour présence:", error);
    }
  }

  getStudentName(studentId) {
    const student = this.students.find((s) => s.id === studentId);
    return student ? student.name : "Inconnu";
  }

  async validateCall() {
    try {
      const response = await fetch("/api/validate-session/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.getCSRFToken(),
        },
        body: JSON.stringify({
          session_id: this.sessionId,
        }),
      });

      const data = await response.json();
      if (data.success) {
        this.logMessage("Session d'appel validée avec succès");
        // Rediriger vers le dashboard
        setTimeout(() => {
          window.location.href = "/enseignant/dashboard/";
        }, 2000);
      } else {
        this.logMessage("Erreur lors de la validation: " + data.error);
      }
    } catch (error) {
      console.error("Erreur validation session:", error);
      this.logMessage("Erreur lors de la validation de la session");
    }
  }

  // Utilitaires
  getCSRFToken() {
    return (
      document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
      document.cookie
        .split("; ")
        .find((row) => row.startsWith("csrftoken="))
        ?.split("=")[1]
    );
  }

  logMessage(message) {
    const logContainer = document.getElementById("recognitionLog");
    if (logContainer) {
      const time = new Date().toLocaleTimeString("fr-FR", {
        hour: "2-digit",
        minute: "2-digit",
      });
      const logItem = document.createElement("div");
      logItem.className = "log-item";
      logItem.innerHTML = `
                <span class="log-time">${time}</span>
                <span class="log-message">${message}</span>
            `;
      logContainer.appendChild(logItem);
      logContainer.scrollTop = logContainer.scrollHeight;
    }
    console.log(`[${time}] ${message}`);
  }

  hideCameraStatus() {
    const statusElement = document.getElementById("cameraStatus");
    if (statusElement) {
      statusElement.style.display = "none";
    }
  }

  showRecognitionActive() {
    const container = document.querySelector(".camera-container");
    if (container) {
      container.classList.add("recognition-active");
    }
  }

  hideRecognitionActive() {
    const container = document.querySelector(".camera-container");
    if (container) {
      container.classList.remove("recognition-active");
    }
  }

  showProcessingIndicator() {
    // Afficher un indicateur de traitement sur la vidéo
    const video = document.getElementById("video");
    if (video) {
      const indicator = document.createElement("div");
      indicator.id = "processingIndicator";
      indicator.className = "processing-indicator";
      indicator.innerHTML = `
        <div class="spinner-border text-light" role="status">
          <span class="visually-hidden">Traitement...</span>
        </div>
        <p class="mt-2 mb-0">Analyse en cours...</p>
      `;

      const container = video.parentElement;
      container.style.position = "relative";
      container.appendChild(indicator);
    }
  }

  hideProcessingIndicator() {
    const indicator = document.getElementById("processingIndicator");
    if (indicator) {
      indicator.remove();
    }
  }

  showNoFaceDetected() {
    // Afficher un message temporaire sur la vidéo
    const video = document.getElementById("video");
    if (video) {
      const message = document.createElement("div");
      message.id = "noFaceMessage";
      message.className = "no-face-message";
      message.innerHTML = `
        <i class="fas fa-exclamation-triangle text-warning"></i>
        <p class="mt-2 mb-0">Aucun visage détecté</p>
        <small class="text-muted">Vérifiez l'éclairage et la position</small>
      `;

      const container = video.parentElement;
      container.appendChild(message);

      // Masquer le message après 3 secondes
      setTimeout(() => {
        if (message.parentNode) {
          message.remove();
        }
      }, 3000);
    }
  }

  showErrorMessage(message) {
    // Créer une notification d'erreur
    const notification = document.createElement("div");
    notification.className =
      "alert alert-danger alert-dismissible fade show position-fixed";
    notification.style.cssText =
      "top: 80px; right: 20px; z-index: 9999; min-width: 300px;";
    notification.innerHTML = `
      <i class="fas fa-exclamation-triangle me-2"></i>${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // Auto-remove après 5 secondes
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
      }
    }, 5000);
  }
}

// Fonctions globales pour compatibilité
function startFacialRecognition() {
  if (!window.facialRecognition) {
    window.facialRecognition = new FacialRecognitionImproved();
  }
  window.facialRecognition.startRecognition();
}

function validateCall() {
  if (window.facialRecognition) {
    window.facialRecognition.validateCall();
  }
}

function markPresent(studentId) {
  if (window.facialRecognition) {
    window.facialRecognition.markPresent(studentId);
  }
}

function markLate(studentId) {
  if (window.facialRecognition) {
    window.facialRecognition.markLate(studentId);
  }
}

function markAbsent(studentId) {
  if (window.facialRecognition) {
    window.facialRecognition.markAbsent(studentId);
  }
}

// Initialisation au chargement de la page
document.addEventListener("DOMContentLoaded", function () {
  window.facialRecognition = new FacialRecognitionImproved();
});
