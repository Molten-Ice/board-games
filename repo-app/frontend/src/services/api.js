import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const menuAPI = {
  // Process a menu image
  processMenu: async (imageData, restaurantName) => {
    try {
      const response = await api.post('/process-menu', {
        imageData,
        restaurantName,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Process menu with file upload
  processMenuFile: async (file, restaurantName) => {
    try {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('restaurantName', restaurantName);

      const response = await api.post('/process-menu', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get all menus
  getMenus: async () => {
    try {
      const response = await api.get('/menus');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get a specific menu
  getMenu: async (menuId) => {
    try {
      const response = await api.get(`/menus/${menuId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Delete a menu
  deleteMenu: async (menuId) => {
    try {
      const response = await api.delete(`/menus/${menuId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Toggle favorite
  toggleFavorite: async (menuId) => {
    try {
      const response = await api.post(`/menus/${menuId}/favorite`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Search menu items
  searchMenus: async (query, category, dietary) => {
    try {
      const params = new URLSearchParams();
      if (query) params.append('q', query);
      if (category) params.append('category', category);
      if (dietary) params.append('dietary', dietary);

      const response = await api.get(`/search?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get categories
  getCategories: async () => {
    try {
      const response = await api.get('/categories');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

export default api;
