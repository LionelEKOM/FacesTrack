// ========================================
// RECONNAISSANCE FACIALE FACETRACK
// ========================================

class FacialRecognition {
  constructor() {
    this.video = document.getElementById("video");
    this.canvas = document.getElementById("canvas");
    this.ctx = this.canvas.getContext("2d");
    this.stream = null;
    this.isActive = false;
    this.recognitionInterval = null;
    this.currentCourseId = null;
    this.students = [];
    this.attendanceData = {};

    this.initialize();
  }

  async initialize() {
    try {
      // Initialiser la caméra
      await this.initializeCamera();

      // Charger les données des élèves
      await this.loadStudentsData();

      // Initialiser les événements
      this.initializeEvents();

      this.logMessage("Système de reconnaissance faciale initialisé");
    } catch (error) {
      console.error("Erreur d'initialisation:", error);
      this.logMessage("Erreur d'initialisation: " + error.message);
    }
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
          resolve();
        };
      });
    } catch (error) {
      throw new Error("Impossible d'accéder à la caméra: " + error.message);
    }
  }

  async loadStudentsData() {
    try {
      // Simuler le chargement des données des élèves
      // En production, ceci viendrait d'une API
      this.students = Array.from(
        document.querySelectorAll("#studentsTableBody tr")
      ).map((row) => {
        const studentId = row.dataset.studentId;
        return {
          id: studentId,
          name: row.cells[1].textContent,
          matricule: row.cells[2].textContent,
          photoUrl: row.querySelector("img")?.src || null,
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
    } catch (error) {
      console.error("Erreur de chargement des élèves:", error);
    }
  }

  initializeEvents() {
    // Événements pour les boutons de contrôle
    document
      .getElementById("startRecognition")
      .addEventListener("click", () => {
        this.startRecognition();
      });

    document.getElementById("validateCall").addEventListener("click", () => {
      this.validateCall();
    });

    // Événements pour la caméra
    this.video.addEventListener("play", () => {
      this.logMessage("Caméra activée");
    });

    this.video.addEventListener("error", (error) => {
      this.logMessage("Erreur caméra: " + error.message);
    });
  }

  startRecognition() {
    if (this.isActive) return;

    this.isActive = true;
    this.logMessage("Démarrage de la reconnaissance faciale...");

    // Mettre à jour l'interface
    document.getElementById("startRecognition").disabled = true;
    document.getElementById("validateCall").disabled = false;
    document
      .querySelector(".camera-container")
      .classList.add("recognition-active");
    document.getElementById("cameraStatus").style.display = "none";

    // Démarrer la reconnaissance
    this.startRecognitionLoop();

    this.logMessage("Reconnaissance faciale active - Surveillance en cours...");
  }

  stopRecognition() {
    if (!this.isActive) return;

    this.isActive = false;
    this.logMessage("Arrêt de la reconnaissance faciale");

    // Mettre à jour l'interface
    document.getElementById("startRecognition").disabled = false;
    document.getElementById("validateCall").disabled = true;
    document
      .querySelector(".camera-container")
      .classList.remove("recognition-active");
    document.getElementById("cameraStatus").style.display = "block";

    // Arrêter la boucle de reconnaissance
    if (this.recognitionInterval) {
      clearInterval(this.recognitionInterval);
      this.recognitionInterval = null;
    }
  }

  startRecognitionLoop() {
    // Simuler la reconnaissance toutes les 2 secondes
    this.recognitionInterval = setInterval(() => {
      this.processFrame();
    }, 2000);
  }

  async processFrame() {
    try {
      // Capturer une image de la vidéo
      this.canvas.width = this.video.videoWidth;
      this.canvas.height = this.video.videoHeight;
      this.ctx.drawImage(this.video, 0, 0);

      // Simuler la détection de visage
      const detectedFaces = await this.detectFaces();

      if (detectedFaces.length > 0) {
        // Simuler la reconnaissance
        const recognizedStudent = await this.recognizeStudent(detectedFaces[0]);

        if (recognizedStudent) {
          this.handleStudentRecognition(recognizedStudent);
        }
      }
    } catch (error) {
      console.error("Erreur de traitement:", error);
    }
  }

  async detectFaces() {
    // Simulation de détection de visages
    // En production, utiliser une bibliothèque comme face-api.js ou MediaPipe
    return new Promise((resolve) => {
      setTimeout(() => {
        // Simuler la détection d'un visage avec 80% de probabilité
        if (Math.random() > 0.2) {
          resolve([
            {
              x: 100,
              y: 100,
              width: 200,
              height: 200,
              confidence: 0.8,
            },
          ]);
        } else {
          resolve([]);
        }
      }, 100);
    });
  }

  async recognizeStudent(face) {
    // Simulation de reconnaissance d'élève
    // En production, comparer avec la base de photos de référence
    return new Promise((resolve) => {
      setTimeout(() => {
        // Simuler la reconnaissance d'un élève aléatoire
        if (Math.random() > 0.3) {
          const randomStudent =
            this.students[Math.floor(Math.random() * this.students.length)];
          resolve({
            student: randomStudent,
            confidence: 0.7 + Math.random() * 0.3,
            face: face,
          });
        } else {
          resolve(null);
        }
      }, 200);
    });
  }

  handleStudentRecognition(recognition) {
    const { student, confidence } = recognition;

    // Mettre à jour le statut de l'élève
    this.attendanceData[student.id] = {
      status: "PRESENT",
      time: new Date(),
      confidence: confidence,
    };

    // Mettre à jour l'interface
    this.updateStudentStatus(student.id, "PRESENT", confidence);
    this.updateLastRecognition(student, confidence);
    this.updateStatistics();

    // Ajouter au journal
    this.logMessage(
      `${student.name} reconnu (confiance: ${Math.round(confidence * 100)}%)`
    );

    // Notification sonore (optionnel)
    this.playNotificationSound();
  }

  updateStudentStatus(studentId, status, confidence = 0) {
    const statusElement = document.getElementById(`status-${studentId}`);
    const timeElement = document.getElementById(`time-${studentId}`);

    if (statusElement && timeElement) {
      // Mettre à jour le statut
      statusElement.className = `status-badge status-${status.toLowerCase()}`;
      statusElement.textContent = this.getStatusText(status);

      // Mettre à jour l'heure
      if (status !== "ABSENT") {
        const now = new Date();
        timeElement.textContent = now.toLocaleTimeString("fr-FR", {
          hour: "2-digit",
          minute: "2-digit",
        });
      }
    }
  }

  updateLastRecognition(student, confidence) {
    const container = document.getElementById("lastRecognition");

    container.innerHTML = `
            <div class="text-center">
                ${
                  student.photoUrl
                    ? `<img src="${student.photoUrl}" alt="${student.name}" class="rounded-circle">`
                    : `<div class="photo-placeholder mb-3"><i class="fas fa-user-graduate fa-3x"></i></div>`
                }
                <h5 class="mb-2">${student.name}</h5>
                <p class="text-muted mb-1">${student.matricule}</p>
                <div class="badge bg-success">Reconnu</div>
                <small class="d-block text-muted mt-2">Confiance: ${Math.round(
                  confidence * 100
                )}%</small>
            </div>
        `;
  }

  updateStatistics() {
    let present = 0,
      late = 0,
      absent = 0;

    Object.values(this.attendanceData).forEach((data) => {
      switch (data.status) {
        case "PRESENT":
          present++;
          break;
        case "LATE":
          late++;
          break;
        case "ABSENT":
        default:
          absent++;
          break;
      }
    });

    document.getElementById("presentCount").textContent = present;
    document.getElementById("lateCount").textContent = late;
    document.getElementById("absentCount").textContent = absent;
  }

  getStatusText(status) {
    const statusMap = {
      PRESENT: "Présent",
      LATE: "Retard",
      ABSENT: "Absent",
    };
    return statusMap[status] || "Inconnu";
  }

  logMessage(message) {
    const logContainer = document.getElementById("recognitionLog");
    const logItem = document.createElement("div");
    logItem.className = "log-item";

    const now = new Date();
    const timeString = now.toLocaleTimeString("fr-FR", {
      hour: "2-digit",
      minute: "2-digit",
    });

    logItem.innerHTML = `
            <span class="log-time">${timeString}</span>
            <span class="log-message">${message}</span>
        `;

    logContainer.appendChild(logItem);
    logContainer.scrollTop = logContainer.scrollHeight;
  }

  playNotificationSound() {
    // Créer un son de notification simple
    const audioContext = new (window.AudioContext ||
      window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 800;
    gainNode.gain.value = 0.1;

    oscillator.start();
    setTimeout(() => oscillator.stop(), 200);
  }

  async validateCall() {
    try {
      this.logMessage("Validation de l'appel en cours...");

      // Arrêter la reconnaissance
      this.stopRecognition();

      // Préparer les données pour l'envoi
      const attendanceData = Object.entries(this.attendanceData).map(
        ([studentId, data]) => ({
          student_id: studentId,
          status: data.status,
          time: data.time,
          confidence: data.confidence,
          method: "FACIAL",
        })
      );

      // Simuler l'envoi des données
      await this.sendAttendanceData(attendanceData);

      this.logMessage("Appel validé et enregistré avec succès!");

      // Désactiver le bouton de validation
      document.getElementById("validateCall").disabled = true;

      // Afficher un message de succès
      this.showSuccessMessage(
        "Appel validé ! Les présences ont été enregistrées."
      );
    } catch (error) {
      console.error("Erreur de validation:", error);
      this.logMessage("Erreur lors de la validation: " + error.message);
      this.showErrorMessage("Erreur lors de la validation de l'appel");
    }
  }

  async sendAttendanceData(data) {
    // Simulation d'envoi des données
    return new Promise((resolve) => {
      setTimeout(() => {
        console.log("Données de présence envoyées:", data);
        resolve({ success: true });
      }, 1000);
    });
  }

  showSuccessMessage(message) {
    // Créer une notification de succès
    const notification = document.createElement("div");
    notification.className =
      "alert alert-success alert-dismissible fade show position-fixed";
    notification.style.cssText =
      "top: 80px; right: 20px; z-index: 9999; min-width: 300px;";
    notification.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>${message}
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

// ========================================
// FONCTIONS GLOBALES
// ========================================

let facialRecognition;

// Initialiser la reconnaissance faciale au chargement de la page
document.addEventListener("DOMContentLoaded", function () {
  facialRecognition = new FacialRecognition();
});

// Fonctions pour les contrôles manuels
function markPresent(studentId) {
  if (facialRecognition) {
    facialRecognition.attendanceData[studentId] = {
      status: "PRESENT",
      time: new Date(),
      confidence: 1.0,
    };
    facialRecognition.updateStudentStatus(studentId, "PRESENT");
    facialRecognition.updateStatistics();
    facialRecognition.logMessage(`Élève marqué manuellement comme présent`);
  }
}

function markLate(studentId) {
  if (facialRecognition) {
    facialRecognition.attendanceData[studentId] = {
      status: "LATE",
      time: new Date(),
      confidence: 1.0,
    };
    facialRecognition.updateStudentStatus(studentId, "LATE");
    facialRecognition.updateStatistics();
    facialRecognition.logMessage(`Élève marqué manuellement en retard`);
  }
}

function markAbsent(studentId) {
  if (facialRecognition) {
    facialRecognition.attendanceData[studentId] = {
      status: "ABSENT",
      time: null,
      confidence: 0,
    };
    facialRecognition.updateStudentStatus(studentId, "ABSENT");
    facialRecognition.updateStatistics();
    facialRecognition.logMessage(`Élève marqué manuellement comme absent`);
  }
}

// Fonctions pour la caméra
function startFacialRecognition() {
  if (facialRecognition) {
    facialRecognition.startRecognition();
  }
}

function validateCall() {
  if (facialRecognition) {
    facialRecognition.validateCall();
  }
}

function switchCamera() {
  if (facialRecognition) {
    facialRecognition.logMessage("Changement de caméra...");
    // Implémentation du changement de caméra
  }
}

function takeSnapshot() {
  if (facialRecognition) {
    facialRecognition.logMessage("Capture manuelle effectuée");
    // Implémentation de la capture manuelle
  }
}

// Gestion des erreurs globales
window.addEventListener("error", function (e) {
  console.error("Erreur globale:", e.error);
  if (facialRecognition) {
    facialRecognition.logMessage("Erreur système: " + e.error.message);
  }
});

// Gestion de la fermeture de la page
window.addEventListener("beforeunload", function () {
  if (facialRecognition && facialRecognition.isActive) {
    facialRecognition.stopRecognition();
  }
});
