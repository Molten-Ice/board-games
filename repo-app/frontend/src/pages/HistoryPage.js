import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  FaArrowLeft,
  FaStar,
  FaRegStar,
  FaTrash,
  FaUtensils,
  FaCamera,
  FaSearch,
  FaTimes
} from 'react-icons/fa';
import { menuAPI } from '../services/api';
import './HistoryPage.css';

function HistoryPage() {
  const navigate = useNavigate();

  const [menus, setMenus] = useState([]);
  const [filteredMenus, setFilteredMenus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  useEffect(() => {
    loadMenus();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [menus, searchQuery, showFavoritesOnly]);

  const loadMenus = async () => {
    try {
      setLoading(true);
      const result = await menuAPI.getMenus();
      setMenus(result.menus);
      setLoading(false);
    } catch (err) {
      console.error('Error loading menus:', err);
      setError('Failed to load menu history');
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...menus];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(menu =>
        menu.restaurant_name.toLowerCase().includes(query)
      );
    }

    // Favorites filter
    if (showFavoritesOnly) {
      filtered = filtered.filter(menu => menu.is_favorite);
    }

    setFilteredMenus(filtered);
  };

  const toggleFavorite = async (menuId, event) => {
    event.preventDefault();
    event.stopPropagation();

    try {
      const result = await menuAPI.toggleFavorite(menuId);

      // Update menu in state
      setMenus(menus.map(menu =>
        menu.id === menuId
          ? { ...menu, is_favorite: result.is_favorite }
          : menu
      ));
    } catch (err) {
      console.error('Error toggling favorite:', err);
    }
  };

  const handleDelete = async (menuId, event) => {
    event.preventDefault();
    event.stopPropagation();

    if (deleteConfirm !== menuId) {
      setDeleteConfirm(menuId);
      return;
    }

    try {
      await menuAPI.deleteMenu(menuId);
      setMenus(menus.filter(menu => menu.id !== menuId));
      setDeleteConfirm(null);
    } catch (err) {
      console.error('Error deleting menu:', err);
      alert('Failed to delete menu');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="history-page">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="history-page">
      <div className="history-header">
        <button className="back-btn" onClick={() => navigate('/')}>
          <FaArrowLeft /> Back
        </button>
        <h1>Menu History</h1>
        <div></div>
      </div>

      <div className="history-controls">
        <div className="search-input-wrapper">
          <FaSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search restaurants..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          {searchQuery && (
            <button className="clear-search" onClick={() => setSearchQuery('')}>
              <FaTimes />
            </button>
          )}
        </div>

        <button
          className={`filter-toggle ${showFavoritesOnly ? 'active' : ''}`}
          onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
        >
          <FaStar /> Favorites Only
        </button>
      </div>

      <div className="history-content">
        {error && <div className="error">{error}</div>}

        {filteredMenus.length === 0 && !loading && (
          <div className="empty-state">
            {showFavoritesOnly ? (
              <>
                <FaStar className="empty-icon" />
                <h2>No Favorite Menus</h2>
                <p>Star your favorite menus to see them here</p>
              </>
            ) : searchQuery ? (
              <>
                <FaSearch className="empty-icon" />
                <h2>No Results Found</h2>
                <p>Try a different search term</p>
              </>
            ) : (
              <>
                <FaCamera className="empty-icon" />
                <h2>No Menus Yet</h2>
                <p>Start by scanning your first menu</p>
                <Link to="/camera" className="btn btn-primary">
                  <FaCamera /> Scan Menu
                </Link>
              </>
            )}
          </div>
        )}

        <div className="menus-grid">
          {filteredMenus.map(menu => (
            <Link
              key={menu.id}
              to={`/menu/${menu.id}`}
              className="menu-card"
              onClick={(e) => {
                if (deleteConfirm === menu.id) {
                  e.preventDefault();
                }
              }}
            >
              <div className="menu-card-header">
                <h3 className="restaurant-name">
                  <FaUtensils /> {menu.restaurant_name}
                </h3>
                <div className="card-actions">
                  <button
                    className="action-btn favorite-btn"
                    onClick={(e) => toggleFavorite(menu.id, e)}
                  >
                    {menu.is_favorite ? (
                      <FaStar className="favorite-active" />
                    ) : (
                      <FaRegStar />
                    )}
                  </button>
                  <button
                    className={`action-btn delete-btn ${deleteConfirm === menu.id ? 'confirm' : ''}`}
                    onClick={(e) => handleDelete(menu.id, e)}
                  >
                    <FaTrash />
                  </button>
                </div>
              </div>

              {deleteConfirm === menu.id && (
                <div
                  className="delete-confirm"
                  onClick={(e) => e.preventDefault()}
                >
                  <p>Click delete again to confirm</p>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setDeleteConfirm(null);
                    }}
                  >
                    Cancel
                  </button>
                </div>
              )}

              <div className="menu-card-info">
                <span className="item-count">{menu.item_count} items</span>
                <span className="menu-date">{formatDate(menu.created_at)}</span>
              </div>
            </Link>
          ))}
        </div>
      </div>

      <div className="floating-action">
        <Link to="/camera" className="fab">
          <FaCamera />
        </Link>
      </div>
    </div>
  );
}

export default HistoryPage;
