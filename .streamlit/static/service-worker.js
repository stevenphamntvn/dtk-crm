const CACHE_NAME = 'dtk-crm-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png'
];

// Cache các tài nguyên tĩnh
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Cache mở thành công');
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .catch((error) => {
        console.error('Lỗi cache:', error);
      })
  );
  self.skipWaiting();
});

// Active service worker và xóa cache cũ
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Xóa cache cũ:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Xử lý request với chiến lược Network First với fallback cache
self.addEventListener('fetch', (event) => {
  // Bỏ qua các request không phải HTTP(S)
  if (!event.request.url.startsWith('http')) {
    return;
  }

  // Chiến lược: Network First cho API, Cache First cho static assets
  if (event.request.url.includes('/api/') || 
      event.request.url.includes('/st.')) {
    // Network First cho API và Streamlit assets
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Cache response nếu thành công
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Fallback to cache nếu network fail
          return caches.match(event.request);
        })
    );
  } else {
    // Cache First cho static assets
    event.respondWith(
      caches.match(event.request)
        .then((cachedResponse) => {
          if (cachedResponse) {
            // Background fetch để cập nhật cache
            fetch(event.request).then((response) => {
              if (response.status === 200) {
                caches.open(CACHE_NAME).then((cache) => {
                  cache.put(event.request, response);
                });
              }
            });
            return cachedResponse;
          }
          return fetch(event.request);
        })
    );
  }
});

// Background Sync khi có mạng trở lại
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

async function syncData() {
  // Đọc dữ liệu offline từ IndexedDB và sync lên server
  try {
    const offlineData = await getOfflineData();
    if (offlineData && offlineData.length > 0) {
      // Gửi dữ liệu lên server
      for (const data of offlineData) {
        await sendDataToServer(data);
      }
      // Xóa dữ liệu đã sync
      await clearOfflineData();
    }
  } catch (error) {
    console.error('Lỗi sync:', error);
  }
}

// Helper functions cho IndexedDB
async function getOfflineData() {
  // Implementation sẽ được thêm sau
  return [];
}

async function clearOfflineData() {
  // Implementation sẽ được thêm sau
}

async function sendDataToServer(data) {
  // Implementation sẽ được thêm sau
  return fetch('/api/sync', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
}
