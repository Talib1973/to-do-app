/**
 * Centralized API client with JWT authentication
 */

// Local development API URL
const API_BASE_URL = 'http://localhost:8000';

interface FetchOptions extends RequestInit {
  requiresAuth?: boolean;
}

async function fetchWithAuth(endpoint: string, options: FetchOptions = {}) {
  const { requiresAuth = true, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers as Record<string, string>),
  };

  // Add Authorization header if authentication is required
  if (requiresAuth) {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('Not authenticated');
    }
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  // Handle 401 Unauthorized
  if (response.status === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const tasksApi = {
  list: async (completed?: boolean) => {
    const query = completed !== undefined ? `?completed=${completed}` : '';
    return fetchWithAuth(`/api/tasks/${query}`);
  },

  get: async (taskId: string) => {
    return fetchWithAuth(`/api/tasks/${taskId}/`);
  },

  create: async (data: { title: string; description?: string; completed?: boolean }) => {
    return fetchWithAuth('/api/tasks/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  update: async (taskId: string, data: { title: string; description?: string; completed?: boolean }) => {
    return fetchWithAuth(`/api/tasks/${taskId}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  patch: async (taskId: string, data: Partial<{ title: string; description: string; completed: boolean }>) => {
    return fetchWithAuth(`/api/tasks/${taskId}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  delete: async (taskId: string) => {
    return fetchWithAuth(`/api/tasks/${taskId}/`, {
      method: 'DELETE',
    });
  },
};
