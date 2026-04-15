// Lógica para el botón de instalación PWA
let deferredPrompt;
const installBtn = document.getElementById("installBtn");

window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredPrompt = e;
  if (installBtn) installBtn.style.display = "block";
});

if (installBtn) {
  installBtn.addEventListener("click", async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === "accepted") {
        installBtn.style.display = "none";
      }
      deferredPrompt = null;
    }
  });
}

// --- LOGICA DE SINCRONIZACIÓN OFFLINE ---
// --- LOGICA DE SINCRONIZACIÓN OFFLINE ---
const incidentForm = document.getElementById("incident-form");

if (incidentForm) {
  incidentForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log("Iniciando proceso de envío...");

    const formData = new FormData(incidentForm);
    const imagenFile = formData.get("imagen");

    // Convertimos imagen a texto
    const imagenBase64 =
      imagenFile && imagenFile.size > 0 ? await toBase64(imagenFile) : null;

    const reporte = {
      titulo: formData.get("titulo"),
      tipo: formData.get("tipo"),
      descripcion: formData.get("descripcion"),
      latitud: formData.get("latitud"),
      longitud: formData.get("longitud"),
      zona_codigo: formData.get("zona_codigo"),
      imagen: imagenBase64,
      csrf: document.querySelector("[name=csrfmiddlewaretoken]").value,
    };

    try {
      console.log("Intentando envío...");
      const response = await enviarReporte(reporte);

      // SI LLEGAMOS AQUÍ, ES QUE HUBO RED
      console.log("Servidor respondió con éxito");
      window.location.href = "/historial/";
    } catch (error) {
      // SI HAY ERROR DE RED O EL SERVICE WORKER DEVOLVIÓ HTML, ENTRA AQUÍ
      console.warn("Fallo detectado (Offline). Guardando en LocalStorage...");

      let pendientes = JSON.parse(
        localStorage.getItem("reportes_pendientes") || "[]",
      );
      pendientes.push(reporte);
      localStorage.setItem("reportes_pendientes", JSON.stringify(pendientes));

      alert("⚠️ MODO OFFLINE: Guardado en LocalStorage.");
      // No redirigimos para que puedas verificarlo en la pestaña Application
    }
  });
}

// Función auxiliar para enviar
async function enviarReporte(datos) {
  const response = await fetch("/reportar/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": datos.csrf,
    },
    body: JSON.stringify(datos),
  });

  // VALIDACIÓN CRÍTICA:
  // Si la respuesta no es OK o no es JSON (es decir, es el HTML del Service Worker)
  // forzamos un error para que el 'catch' de arriba se active.
  const contentType = response.headers.get("content-type");
  if (
    !response.ok ||
    !contentType ||
    !contentType.includes("application/json")
  ) {
    throw new Error("Respuesta inválida (posiblemente offline)");
  }

  return response.json();
}

// ESCUCHADOR DE RECONEXIÓN: Se dispara cuando vuelve el internet (No Throttling)
window.addEventListener("online", async () => {
  const pendientes = JSON.parse(
    localStorage.getItem("reportes_pendientes") || "[]",
  );

  if (pendientes.length > 0) {
    console.log("Reconexión detectada. Sincronizando reportes...");

    for (const reporte of pendientes) {
      try {
        await enviarReporte(reporte);
      } catch (e) {
        console.error("Error al sincronizar uno", e);
      }
    }

    localStorage.removeItem("reportes_pendientes");
    alert("✅ ¡Reportes en caché enviados con éxito!");
    window.location.reload(); // Recargamos para ver los nuevos datos en el historial
  }
});

const toBase64 = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });
