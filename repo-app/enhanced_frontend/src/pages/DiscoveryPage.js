import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { recommendationAPI, restaurantAPI } from '../services/api';
import { FaStar, FaMapMarkerAlt, FaHeart } from 'react-icons/fa';
import './DiscoveryPage.css';

function DiscoveryPage() {
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('personalized'); // personalized, all, favorites
  const navigate = useNavigate();

  useEffect(() => {
    loadRestaurants();
  }, [filter]);

  const loadRestaurants = async () => {
    setLoading(true);

    try {
      let data;
      if (filter === 'personalized') {
        data = await recommendationAPI.getRecommendations({ limit: 20 });
        setRestaurants(data.recommendations);
      } else if (filter === 'favorites') {
        data = await restaurantAPI.getFavorites();
        setRestaurants(data.favorites || []);
      } else {
        data = await restaurantAPI.getRestaurants({ limit: 20 });
        setRestaurants(data.restaurants);
      }
    } catch (err) {
      console.error('Failed to load restaurants:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRestaurantClick = (id) => {
    navigate(`/restaurant/${id}`);
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="discovery-page">
      <div className="discovery-header">
        <h1>Discover Restaurants</h1>
        <p>Like you have a friend in town who knows where you'll like eating</p>
      </div>

      <div className="filter-tabs">
        <button
          className={`filter-tab ${filter === 'personalized' ? 'active' : ''}`}
          onClick={() => setFilter('personalized')}
        >
          For You
        </button>
        <button
          className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All Restaurants
        </button>
        <button
          className={`filter-tab ${filter === 'favorites' ? 'active' : ''}`}
          onClick={() => setFilter('favorites')}
        >
          <FaHeart /> Favorites
        </button>
      </div>

      <div className="restaurants-grid">
        {restaurants.length === 0 ? (
          <div className="empty-state">
            <p>No restaurants found</p>
          </div>
        ) : (
          restaurants.map((restaurant) => (
            <div
              key={restaurant.id}
              className="restaurant-card"
              onClick={() => handleRestaurantClick(restaurant.id)}
            >
              {restaurant.recommendation_score && (
                <div className="recommendation-badge">
                  {Math.round(restaurant.recommendation_score * 100)}% Match
                </div>
              )}

              <div className="restaurant-card-header">
                <h3 className="restaurant-card-title">{restaurant.name}</h3>

                <div className="restaurant-card-info">
                  {restaurant.area && (
                    <span>
                      <FaMapMarkerAlt /> {restaurant.area}
                    </span>
                  )}
                  {restaurant.average_rating > 0 && (
                    <span className="rating">
                      <FaStar /> {restaurant.average_rating.toFixed(1)}
                    </span>
                  )}
                </div>

                <p className="restaurant-card-description">{restaurant.description}</p>

                <div className="restaurant-card-footer">
                  <div className="cuisines">
                    {restaurant.cuisines.slice(0, 3).map((cuisine, idx) => (
                      <span key={idx} className="cuisine-tag">
                        {cuisine}
                      </span>
                    ))}
                  </div>

                  {restaurant.price_range && (
                    <span className="price-badge">{restaurant.price_range}</span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default DiscoveryPage;
