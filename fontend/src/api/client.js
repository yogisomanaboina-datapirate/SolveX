// Centralized API Client for LifeLink AI Backend Gateway (Port 8001)

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001';

const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token') || 'firebase_id_token';
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export const apiClient = {
  async get(endpoint, headers = {}) {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...headers
      }
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  },

  async post(endpoint, body, headers = {}) {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...headers
      },
      body: JSON.stringify(body)
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(`POST ${endpoint} failed:`, {
        status: response.status,
        statusText: response.statusText,
        data: errorData
      });
      const message = errorData.error?.message || errorData.detail?.message || (typeof errorData.detail === 'string' ? errorData.detail : null) || `HTTP ${response.status}: ${response.statusText}`;
      const err = new Error(message);
      err.status = response.status;
      err.data = errorData;
      throw err;
    }
    return response.json();
  },

  async put(endpoint, body, headers = {}) {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...headers
      },
      body: JSON.stringify(body)
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }
};

