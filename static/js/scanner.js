// static/js/scanner.js
let html5QrCode;

async function startScanner() {
  const readerContainer = document.getElementById("reader-container");
  const mainMenu = document.getElementById("main-menu");

  // Cambiar visibilidad de la interfaz
  mainMenu.style.display = "none";
  readerContainer.style.display = "block";

  // Configuración del escáner
  html5QrCode = new Html5Qrcode("reader");

  const config = {
    fps: 10,
    qrbox: { width: 250, height: 250 },
  };

  try {
    await html5QrCode.start(
      { facingMode: "environment" }, // Usa la cámara trasera
      config,
      (decodedText) => {
        // ÉXITO: Si detecta el código
        console.log("Código detectado:", decodedText);
        if (decodedText.startsWith("safelog_zona:")) {
          const zonaCodigo = decodedText.split(":")[1];
          stopScanner();
          window.location.href = `/reportar/?zona=${zonaCodigo}`;
        }
      },
    );
  } catch (err) {
    console.error("Error al iniciar cámara:", err);
    alert("No se pudo acceder a la cámara. Asegúrate de dar permisos.");
    stopScanner();
  }
}

function stopScanner() {
  if (html5QrCode && html5QrCode.isScanning) {
    html5QrCode
      .stop()
      .then(() => {
        document.getElementById("reader-container").style.display = "none";
        document.getElementById("main-menu").style.display = "grid";
      })
      .catch((err) => console.error("Error al detener:", err));
  } else {
    document.getElementById("reader-container").style.display = "none";
    document.getElementById("main-menu").style.display = "grid";
  }
}
