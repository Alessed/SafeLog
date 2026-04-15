var staticCacheName = "safelog-pwa-v" + new Date().getTime();
var filesToCache = [
  "/",
  "/static/css/history.css",
  "/static/js/main.js",
  "/static/css/style.css", // Asegúrate de incluir todos tus CSS
];

// 1. Instalación: Guardar archivos esenciales en el caché
self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(staticCacheName).then((cache) => {
      console.log("Caché SafeLog preparado");
      return cache.addAll(filesToCache);
    }),
  );
});

// 2. Activación: Limpiar versiones viejas del caché
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== staticCacheName)
          .map((name) => caches.delete(name)),
      );
    }),
  );
});

// 3. Estrategia Fetch: Network First
// Intenta obtener datos de la red, si falla (offline), sirve desde el caché.
self.addEventListener("fetch", (event) => {
  // Solo manejamos peticiones GET (archivos, páginas) para el caché
  if (event.request.method !== "GET") return;

  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request) || caches.match("/");
    }),
  );
});
