import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retrying, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
            headers: { 'Authorization': `Bearer ${refreshToken}` }
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  refreshToken: async () => {
    const response = await api.post('/auth/refresh');
    return response.data;
  },
};

// User API
export const userAPI = {
  updateProfile: async (profileData) => {
    const response = await api.put('/user/profile', profileData);
    return response.data;
  },

  updatePreferences: async (preferences) => {
    const response = await api.put('/user/preferences', preferences);
    return response.data;
  },

  getFavorites: async () => {
    const response = await api.get('/user/favorites');
    return response.data;
  },
};

// Restaurant API
export const restaurantAPI = {
  getRestaurants: async (params = {}) => {
    const response = await api.get('/restaurants', { params });
    return response.data;
  },

  getRestaurant: async (id) => {
    const response = await api.get(`/restaurants/${id}`);
    return response.data;
  },

  getRestaurantMenu: async (id) => {
    const response = await api.get(`/restaurants/${id}/menu`);
    return response.data;
  },

  rateRestaurant: async (id, rating) => {
    const response = await api.post(`/restaurants/${id}/rate`, rating);
    return response.data;
  },

  toggleFavorite: async (id) => {
    const response = await api.post(`/restaurants/${id}/favorite`);
    return response.data;
  },

  addFavorite: async (id) => {
    const response = await api.post(`/restaurants/${id}/favorite`);
    return response.data;
  },

  removeFavorite: async (id) => {
    const response = await api.post(`/restaurants/${id}/favorite`);
    return response.data;
  },

  markVisited: async (id) => {
    const response = await api.post(`/restaurants/${id}/visit`);
    return response.data;
  },

  getFavorites: async () => {
    const response = await api.get('/user/favorites');
    return response.data;
  },

  getSimilarRestaurants: async (id, limit = 5) => {
    const response = await api.get(`/restaurants/${id}/similar`, { params: { limit } });
    return response.data;
  },
};

// Recommendation API
export const recommendationAPI = {
  getRecommendations: async (params = {}) => {
    const response = await api.get('/recommendations', { params });
    return response.data;
  },
};

// Cuisine & Dietary API
export const taxonomyAPI = {
  getCuisines: async () => {
    const response = await api.get('/cuisines');
    return response.data;
  },

  getDietaryPreferences: async () => {
    const response = await api.get('/dietary-preferences');
    return response.data;
  },
};

// Menu API
export const menuAPI = {
  uploadMenu: async (formData) => {
    const response = await api.post('/menu/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getMenu: async (restaurantId) => {
    const response = await api.get(`/restaurants/${restaurantId}/menu`);
    return response.data;
  },
};

// Rating API
export const ratingAPI = {
  submitRating: async (ratingData) => {
    const { restaurant_id, rating, review } = ratingData;
    const response = await api.post(`/restaurants/${restaurant_id}/rate`, {
      rating: rating,
      review_text: review,
    });
    return response.data;
  },
};

// Stats API
export const statsAPI = {
  getStats: async () => {
    const response = await api.get('/stats');
    return response.data;
  },
};

export default api;
