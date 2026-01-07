import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { restaurantAPI, ratingAPI, menuAPI } from '../services/api';
import {
  FaStar,
  FaMapMarkerAlt,
  FaPhone,
  FaGlobe,
  FaHeart,
  FaRegHeart,
  FaCheck,
  FaArrowLeft,
} from 'react-icons/fa';
import './RestaurantDetailPage.css';

function RestaurantDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [restaurant, setRestaurant] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isFavorite, setIsFavorite] = useState(false);
  const [hasVisited, setHasVisited] = useState(false);

  // Rating form state
  const [showRatingForm, setShowRatingForm] = useState(false);
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [review, setReview] = useState('');
  const [submittingRating, setSubmittingRating] = useState(false);

  useEffect(() => {
    loadRestaurantData();
  }, [id]);

  const loadRestaurantData = async () => {
    setLoading(true);
    try {
      // Load restaurant details
      const restaurantData = await restaurantAPI.getRestaurant(id);
      setRestaurant(restaurantData.restaurant);
      setIsFavorite(restaurantData.is_favorite || false);
      setHasVisited(restaurantData.has_visited || false);

      // Load menu
      try {
        const menuData = await menuAPI.getMenu(id);
        setMenuItems(menuData.items || []);
      } catch (menuErr) {
        console.log('No menu available for this restaurant');
        setMenuItems([]);
      }
    } catch (err) {
      console.error('Failed to load restaurant:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFavoriteToggle = async () => {
    try {
      if (isFavorite) {
        await restaurantAPI.removeFavorite(id);
        setIsFavorite(false);
      } else {
        await restaurantAPI.addFavorite(id);
        setIsFavorite(true);
      }
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  const handleMarkVisited = async () => {
    try {
      await restaurantAPI.markVisited(id);
      setHasVisited(true);
    } catch (err) {
      console.error('Failed to mark as visited:', err);
    }
  };

  const handleSubmitRating = async () => {
    if (rating === 0) {
      alert('Please select a rating');
      return;
    }

    setSubmittingRating(true);
    try {
      await ratingAPI.submitRating({
        restaurant_id: parseInt(id),
        rating: rating,
        review: review,
      });

      alert('Rating submitted successfully!');
      setShowRatingForm(false);
      setRating(0);
      setReview('');

      // Reload restaurant to get updated average rating
      loadRestaurantData();
    } catch (err) {
      console.error('Failed to submit rating:', err);
      alert('Failed to submit rating. Please try again.');
    } finally {
      setSubmittingRating(false);
    }
  };

  // Group menu items by category
  const groupedMenuItems = menuItems.reduce((acc, item) => {
    const category = item.category || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(item);
    return acc;
  }, {});

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!restaurant) {
    return (
      <div className="restaurant-detail-page">
        <div className="error-message">Restaurant not found</div>
      </div>
    );
  }

  return (
    <div className="restaurant-detail-page">
      <button className="back-btn" onClick={() => navigate(-1)}>
        <FaArrowLeft /> Back
      </button>

      <div className="restaurant-hero">
        <div className="restaurant-hero-content">
          <h1>{restaurant.name}</h1>

          <div className="restaurant-meta">
            {restaurant.area && (
              <span>
                <FaMapMarkerAlt /> {restaurant.area}
              </span>
            )}
            {restaurant.average_rating > 0 && (
              <span>
                <FaStar /> {restaurant.average_rating.toFixed(1)} ({restaurant.total_ratings}{' '}
                ratings)
              </span>
            )}
            {restaurant.phone && (
              <a href={`tel:${restaurant.phone}`}>
                <FaPhone /> {restaurant.phone}
              </a>
            )}
            {restaurant.website && (
              <a href={restaurant.website} target="_blank" rel="noopener noreferrer">
                <FaGlobe /> Website
              </a>
            )}
          </div>

          <div className="restaurant-actions">
            <button
              className={`btn ${isFavorite ? 'btn-primary' : 'btn-secondary'}`}
              onClick={handleFavoriteToggle}
            >
              {isFavorite ? <FaHeart /> : <FaRegHeart />}
              {isFavorite ? 'Favorited' : 'Add to Favorites'}
            </button>

            {!hasVisited && (
              <button className="btn btn-secondary" onClick={handleMarkVisited}>
                <FaCheck /> Mark as Visited
              </button>
            )}

            <button className="btn btn-primary" onClick={() => setShowRatingForm(!showRatingForm)}>
              <FaStar /> Rate Restaurant
            </button>
          </div>
        </div>
      </div>

      <div className="restaurant-content">
        {/* Restaurant Info */}
        <div className="info-section">
          <h2>About</h2>
          <p>{restaurant.description}</p>

          <div className="info-grid">
            {restaurant.address && (
              <div className="info-item">
                <strong>
                  <FaMapMarkerAlt /> Address:
                </strong>
                <span>{restaurant.address}</span>
              </div>
            )}

            {restaurant.cuisines && restaurant.cuisines.length > 0 && (
              <div className="info-item">
                <strong>Cuisines:</strong>
                <span>{restaurant.cuisines.join(', ')}</span>
              </div>
            )}

            {restaurant.price_range && (
              <div className="info-item">
                <strong>Price Range:</strong>
                <span className="price-badge">{restaurant.price_range}</span>
              </div>
            )}

            {restaurant.ambiance && (
              <div className="info-item">
                <strong>Ambiance:</strong>
                <span>{restaurant.ambiance}</span>
              </div>
            )}
          </div>
        </div>

        {/* Rating Form */}
        {showRatingForm && (
          <div className="rating-form">
            <h3>Rate Your Experience</h3>

            <div className="star-rating">
              {[1, 2, 3, 4, 5].map((star) => (
                <FaStar
                  key={star}
                  size={32}
                  className={star <= (hoverRating || rating) ? 'star-filled' : 'star-empty'}
                  onClick={() => setRating(star)}
                  onMouseEnter={() => setHoverRating(star)}
                  onMouseLeave={() => setHoverRating(0)}
                />
              ))}
            </div>

            <textarea
              placeholder="Share your experience (optional)"
              value={review}
              onChange={(e) => setReview(e.target.value)}
              rows={4}
            />

            <div className="button-group">
              <button
                className="btn btn-secondary"
                onClick={() => setShowRatingForm(false)}
                disabled={submittingRating}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleSubmitRating}
                disabled={submittingRating || rating === 0}
              >
                {submittingRating ? 'Submitting...' : 'Submit Rating'}
              </button>
            </div>
          </div>
        )}

        {/* Menu */}
        {menuItems.length > 0 && (
          <div className="menu-section">
            <h2>Menu</h2>

            {Object.entries(groupedMenuItems).map(([category, items]) => (
              <div key={category} className="menu-category">
                <h3>{category}</h3>
                <div className="menu-items">
                  {items.map((item, idx) => (
                    <div key={idx} className="menu-item">
                      <div className="menu-item-header">
                        <h4>{item.name}</h4>
                        <span className="menu-item-price">£{item.price.toFixed(2)}</span>
                      </div>

                      {item.description && (
                        <p className="menu-item-description">{item.description}</p>
                      )}

                      {item.dietary_tags && JSON.parse(item.dietary_tags).length > 0 && (
                        <div className="dietary-tags">
                          {JSON.parse(item.dietary_tags).map((tag, tagIdx) => (
                            <span key={tagIdx} className="dietary-tag">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {menuItems.length === 0 && (
          <div className="info-section">
            <p>Menu information is not available for this restaurant yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default RestaurantDetailPage;
