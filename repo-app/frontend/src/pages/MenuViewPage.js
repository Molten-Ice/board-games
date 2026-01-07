import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  FaArrowLeft,
  FaSearch,
  FaFilter,
  FaStar,
  FaRegStar,
  FaShareAlt,
  FaTimes,
  FaUtensils,
  FaLeaf,
  FaFire
} from 'react-icons/fa';
import { menuAPI } from '../services/api';
import './MenuViewPage.css';

function MenuViewPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [menu, setMenu] = useState(null);
  const [items, setItems] = useState([]);
  const [filteredItems, setFilteredItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedDietary, setSelectedDietary] = useState('All');
  const [showFilters, setShowFilters] = useState(false);

  const [categories, setCategories] = useState(['All']);
  const dietaryOptions = ['All', 'vegan', 'vegetarian', 'gluten-free', 'dairy-free', 'halal', 'kosher', 'spicy'];

  useEffect(() => {
    loadMenu();
  }, [id]);

  useEffect(() => {
    applyFilters();
  }, [items, searchQuery, selectedCategory, selectedDietary]);

  const loadMenu = async () => {
    try {
      setLoading(true);
      const result = await menuAPI.getMenu(id);

      setMenu(result.menu);
      setItems(result.items);

      // Extract unique categories
      const uniqueCategories = ['All', ...new Set(result.items.map(item => item.category))];
      setCategories(uniqueCategories);

      setLoading(false);
    } catch (err) {
      console.error('Error loading menu:', err);
      setError('Failed to load menu');
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...items];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        item =>
          item.name.toLowerCase().includes(query) ||
          item.description.toLowerCase().includes(query)
      );
    }

    // Category filter
    if (selectedCategory !== 'All') {
      filtered = filtered.filter(item => item.category === selectedCategory);
    }

    // Dietary filter
    if (selectedDietary !== 'All') {
      filtered = filtered.filter(item =>
        item.dietary_tags && item.dietary_tags.includes(selectedDietary)
      );
    }

    setFilteredItems(filtered);
  };

  const toggleFavorite = async () => {
    try {
      const result = await menuAPI.toggleFavorite(id);
      setMenu({ ...menu, is_favorite: result.is_favorite });
    } catch (err) {
      console.error('Error toggling favorite:', err);
    }
  };

  const shareMenu = async () => {
    const shareData = {
      title: menu.restaurant_name,
      text: `Check out the menu from ${menu.restaurant_name}!`,
      url: window.location.href,
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        // Fallback: copy to clipboard
        await navigator.clipboard.writeText(window.location.href);
        alert('Link copied to clipboard!');
      }
    } catch (err) {
      console.error('Error sharing:', err);
    }
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedCategory('All');
    setSelectedDietary('All');
  };

  if (loading) {
    return (
      <div className="menu-view-page">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="menu-view-page">
        <div className="error">{error}</div>
      </div>
    );
  }

  const groupedItems = filteredItems.reduce((acc, item) => {
    const category = item.category || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(item);
    return acc;
  }, {});

  return (
    <div className="menu-view-page">
      <div className="menu-header">
        <button className="back-btn" onClick={() => navigate('/history')}>
          <FaArrowLeft /> Back
        </button>

        <div className="header-actions">
          <button className="icon-btn" onClick={toggleFavorite}>
            {menu.is_favorite ? <FaStar className="favorite-active" /> : <FaRegStar />}
          </button>
          <button className="icon-btn" onClick={shareMenu}>
            <FaShareAlt />
          </button>
        </div>
      </div>

      <div className="menu-info">
        <h1>
          <FaUtensils /> {menu.restaurant_name}
        </h1>
        <p className="item-count">{items.length} items</p>
      </div>

      <div className="search-bar">
        <div className="search-input-wrapper">
          <FaSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search menu items..."
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
          className={`filter-btn ${showFilters ? 'active' : ''}`}
          onClick={() => setShowFilters(!showFilters)}
        >
          <FaFilter /> Filters
        </button>
      </div>

      {showFilters && (
        <div className="filters-panel">
          <div className="filter-group">
            <label>Category</label>
            <div className="filter-options">
              {categories.map(category => (
                <button
                  key={category}
                  className={`filter-option ${selectedCategory === category ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(category)}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          <div className="filter-group">
            <label>Dietary</label>
            <div className="filter-options">
              {dietaryOptions.map(option => (
                <button
                  key={option}
                  className={`filter-option ${selectedDietary === option ? 'active' : ''}`}
                  onClick={() => setSelectedDietary(option)}
                >
                  {option === 'vegan' && <FaLeaf />}
                  {option === 'spicy' && <FaFire />}
                  {option}
                </button>
              ))}
            </div>
          </div>

          <button className="clear-filters-btn" onClick={clearFilters}>
            Clear All Filters
          </button>
        </div>
      )}

      <div className="menu-content">
        {filteredItems.length === 0 ? (
          <div className="no-results">
            <p>No items found matching your criteria</p>
            <button className="btn btn-primary" onClick={clearFilters}>
              Clear Filters
            </button>
          </div>
        ) : (
          Object.entries(groupedItems).map(([category, categoryItems]) => (
            <div key={category} className="category-section">
              <h2 className="category-title">{category}</h2>
              <div className="items-list">
                {categoryItems.map(item => (
                  <div key={item.id} className="menu-item-card">
                    <div className="item-header">
                      <h3 className="item-name">{item.name}</h3>
                      {item.price && <span className="item-price">{item.price}</span>}
                    </div>

                    {item.description && (
                      <p className="item-description">{item.description}</p>
                    )}

                    {item.dietary_tags && item.dietary_tags.length > 0 && (
                      <div className="dietary-tags">
                        {item.dietary_tags.map(tag => (
                          <span key={tag} className={`tag tag-${tag}`}>
                            {tag === 'vegan' && <FaLeaf />}
                            {tag === 'spicy' && <FaFire />}
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default MenuViewPage;
