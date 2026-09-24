// IndexedDB Manager cho CRM Offline Storage
class CRMOfflineDB {
  constructor() {
    this.dbName = 'DTK_CRM_Offline';
    this.dbVersion = 1;
    this.db = null;
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Tạo các object stores
        if (!db.objectStoreNames.contains('customers')) {
          const customerStore = db.createObjectStore('customers', { keyPath: 'KID' });
          customerStore.createIndex('name', 'name', { unique: false });
          customerStore.createIndex('status', 'status', { unique: false });
        }

        if (!db.objectStoreNames.contains('houses')) {
          const houseStore = db.createObjectStore('houses', { keyPath: 'UID' });
          houseStore.createIndex('address', 'address', { unique: false });
          houseStore.createIndex('price', 'price', { unique: false });
        }

        if (!db.objectStoreNames.contains('logs')) {
          const logStore = db.createObjectStore('logs', { keyPath: 'id', autoIncrement: true });
          logStore.createIndex('KID', 'KID', { unique: false });
          logStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        if (!db.objectStoreNames.contains('pending_sync')) {
          const syncStore = db.createObjectStore('pending_sync', { keyPath: 'id', autoIncrement: true });
          syncStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        if (!db.objectStoreNames.contains('settings')) {
          db.createObjectStore('settings', { keyPath: 'key' });
        }
      };
    });
  }

  // CRUD Operations cho Customers
  async addCustomer(customer) {
    return this._add('customers', customer);
  }

  async getCustomer(KID) {
    return this._get('customers', KID);
  }

  async getAllCustomers() {
    return this._getAll('customers');
  }

  async updateCustomer(customer) {
    return this._update('customers', customer);
  }

  async deleteCustomer(KID) {
    return this._delete('customers', KID);
  }

  // CRUD Operations cho Houses
  async addHouse(house) {
    return this._add('houses', house);
  }

  async getHouse(UID) {
    return this._get('houses', UID);
  }

  async getAllHouses() {
    return this._getAll('houses');
  }

  async updateHouse(house) {
    return this._update('houses', house);
  }

  async deleteHouse(UID) {
    return this._delete('houses', UID);
  }

  // CRUD Operations cho Logs
  async addLog(log) {
    return this._add('logs', log);
  }

  async getLogsByKID(KID) {
    return this._getAllByIndex('logs', 'KID', KID);
  }

  async getAllLogs() {
    return this._getAll('logs');
  }

  async updateLog(log) {
    return this._update('logs', log);
  }

  async deleteLog(id) {
    return this._delete('logs', id);
  }

  // Pending Sync Operations
  async addPendingSync(data) {
    const syncData = {
      ...data,
      timestamp: new Date().toISOString(),
      synced: false
    };
    return this._add('pending_sync', syncData);
  }

  async getPendingSyncs() {
    return this._getAll('pending_sync');
  }

  async markSynced(id) {
    const syncData = await this._get('pending_sync', id);
    if (syncData) {
      syncData.synced = true;
      await this._update('pending_sync', syncData);
    }
  }

  async clearSyncedItems() {
    const allSyncs = await this._getAll('pending_sync');
    const syncedItems = allSyncs.filter(item => item.synced);
    
    for (const item of syncedItems) {
      await this._delete('pending_sync', item.id);
    }
  }

  // Settings Operations
  async setSetting(key, value) {
    return this._put('settings', { key, value });
  }

  async getSetting(key) {
    const setting = await this._get('settings', key);
    return setting ? setting.value : null;
  }

  // Batch Operations
  async syncFromServer(serverData) {
    if (!serverData) return;

    // Sync customers
    if (serverData.customers) {
      for (const customer of serverData.customers) {
        await this._put('customers', customer);
      }
    }

    // Sync houses
    if (serverData.houses) {
      for (const house of serverData.houses) {
        await this._put('houses', house);
      }
    }

    // Sync logs
    if (serverData.logs) {
      for (const log of serverData.logs) {
        await this._put('logs', log);
      }
    }
  }

  async getOfflineChanges() {
    const pendingSyncs = await this.getPendingSyncs();
    return pendingSyncs.filter(item => !item.synced);
  }

  // Helper methods
  _add(storeName, data) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.add(data);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  _get(storeName, key) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.get(key);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  _getAll(storeName) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.getAll();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  _getAllByIndex(storeName, indexName, value) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const index = store.index(indexName);
      const request = index.getAll(value);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  _update(storeName, data) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(data);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  _put(storeName, data) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(data);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  _delete(storeName, key) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.delete(key);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async clearAll() {
    const stores = ['customers', 'houses', 'logs', 'pending_sync', 'settings'];
    for (const storeName of stores) {
      await new Promise((resolve, reject) => {
        const transaction = this.db.transaction([storeName], 'readwrite');
        const store = transaction.objectStore(storeName);
        const request = store.clear();

        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
    }
  }
}

// Export singleton instance
const crmDB = new CRMOfflineDB();
