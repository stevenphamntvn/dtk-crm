// PWA Integration Script cho Streamlit CRM
(function() {
  'use strict';

  // Service Worker Registration
  async function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/service-worker.js');
        console.log('Service Worker registered:', registration);

        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New version available
              showUpdateNotification();
            }
          });
        });

        return registration;
      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    }
    return null;
  }

  // Online/Offline Detection
  function setupConnectivityListeners() {
    const updateOnlineStatus = () => {
      const isOnline = navigator.onLine;
      document.body.classList.toggle('offline', !isOnline);
      
      // Send status to Streamlit
      if (window.parent !== window) {
        window.parent.postMessage({
          type: 'streamlit:component',
          value: { online: isOnline }
        }, '*');
      }

      // Show notification
      if (!isOnline) {
        showOfflineNotification();
      } else {
        hideOfflineNotification();
        // Trigger sync when coming back online
        syncPendingData();
      }
    };

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus(); // Initial check
  }

  // IndexedDB Setup
  async function setupIndexedDB() {
    try {
      await crmDB.init();
      console.log('IndexedDB initialized successfully');
      
      // Load cached data if offline
      if (!navigator.onLine) {
        loadOfflineData();
      }
    } catch (error) {
      console.error('IndexedDB setup failed:', error);
    }
  }

  // Sync Functions
  async function syncPendingData() {
    if (!navigator.onLine) return;

    try {
      const pendingChanges = await crmDB.getOfflineChanges();
      if (pendingChanges.length > 0) {
        console.log(`Syncing ${pendingChanges.length} pending changes...`);
        
        for (const change of pendingChanges) {
          try {
            await syncChangeToServer(change);
            await crmDB.markSynced(change.id);
          } catch (error) {
            console.error('Failed to sync change:', error);
          }
        }

        await crmDB.clearSyncedItems();
        showSyncSuccessNotification();
      }
    } catch (error) {
      console.error('Sync failed:', error);
    }
  }

  async function syncChangeToServer(change) {
    // Gửi dữ liệu lên server Streamlit
    const response = await fetch('/_stcore/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        endpoint: 'sync_offline_data',
        data: change
      })
    });

    if (!response.ok) {
      throw new Error('Sync request failed');
    }

    return response.json();
  }

  // Load offline data
  async function loadOfflineData() {
    try {
      const customers = await crmDB.getAllCustomers();
      const houses = await crmDB.getAllHouses();
      const logs = await crmDB.getAllLogs();

      // Send to Streamlit app
      if (window.parent !== window) {
        window.parent.postMessage({
          type: 'streamlit:component',
          value: {
            offline_data: {
              customers,
              houses,
              logs
            }
          }
        }, '*');
      }

      showOfflineDataNotification(customers.length, houses.length);
    } catch (error) {
      console.error('Failed to load offline data:', error);
    }
  }

  // Notification Functions
  function showOfflineNotification() {
    showNotification('📱 Chế độ Offline - Đang sử dụng dữ liệu đã lưu', 'warning');
  }

  function hideOfflineNotification() {
    hideNotification();
  }

  function showUpdateNotification() {
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #FF4B4B;
      color: white;
      padding: 16px 24px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      font-family: sans-serif;
      animation: slideIn 0.3s ease-out;
    `;
    notification.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 8px;">📲 Cập nhật mới có sẵn!</div>
      <button onclick="location.reload()" style="
        background: white;
        color: #FF4B4B;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
      ">Cập nhật ngay</button>
    `;
    document.body.appendChild(notification);
  }

  function showSyncSuccessNotification() {
    showNotification('✅ Đồng bộ dữ liệu thành công!', 'success');
  }

  function showOfflineDataNotification(customersCount, housesCount) {
    showNotification(
      `📱 Offline: ${customersCount} khách, ${housesCount} nhà`, 
      'info'
    );
  }

  function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.querySelector('.pwa-notification');
    if (existing) existing.remove();

    const notification = document.createElement('div');
    notification.className = 'pwa-notification';
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${type === 'success' ? '#4CAF50' : type === 'warning' ? '#FF9800' : '#2196F3'};
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      font-family: sans-serif;
      animation: slideIn 0.3s ease-out;
      max-width: 300px;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => notification.remove(), 300);
    }, 5000);
  }

  function hideNotification() {
    const existing = document.querySelector('.pwa-notification');
    if (existing) existing.remove();
  }

  // Add CSS animations
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
      from { transform: translateX(0); opacity: 1; }
      to { transform: translateX(100%); opacity: 0; }
    }
    .offline {
      filter: grayscale(0.3);
    }
  `;
  document.head.appendChild(style);

  // Message listener for Streamlit communication
  window.addEventListener('message', (event) => {
    if (event.data.type === 'streamlit:render') {
      // Handle messages from Streamlit
      if (event.data.args?.action === 'sync_data') {
        syncPendingData();
      } else if (event.data.args?.action === 'cache_data') {
        cacheServerData(event.data.args.data);
      }
    }
  });

  // Cache server data when online
  async function cacheServerData(data) {
    if (!data) return;

    try {
      await crmDB.syncFromServer(data);
      console.log('Data cached successfully');
    } catch (error) {
      console.error('Failed to cache data:', error);
    }
  }

  // Initialize everything
  async function init() {
    console.log('Initializing PWA Integration...');
    
    // Register Service Worker
    await registerServiceWorker();
    
    // Setup connectivity listeners
    setupConnectivityListeners();
    
    // Setup IndexedDB
    await setupIndexedDB();
    
    // Add manifest link if not present
    if (!document.querySelector('link[rel="manifest"]')) {
      const manifestLink = document.createElement('link');
      manifestLink.rel = 'manifest';
      manifestLink.href = '/manifest.json';
      document.head.appendChild(manifestLink);
    }

    // Add theme color meta
    if (!document.querySelector('meta[name="theme-color"]')) {
      const themeColor = document.createElement('meta');
      themeColor.name = 'theme-color';
      themeColor.content = '#FF4B4B';
      document.head.appendChild(themeColor);
    }

    // Add apple-touch-icon
    if (!document.querySelector('link[rel="apple-touch-icon"]')) {
      const appleIcon = document.createElement('link');
      appleIcon.rel = 'apple-touch-icon';
      appleIcon.href = '/icon-192.png';
      document.head.appendChild(appleIcon);
    }

    console.log('PWA Integration initialized successfully');
  }

  // Start initialization when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export functions for Streamlit integration
  window.PWAIntegration = {
    syncData: syncPendingData,
    cacheData: cacheServerData,
    isOnline: () => navigator.onLine,
    getOfflineData: loadOfflineData
  };

})();
