import React from 'react';
import { Link } from 'react-router-dom';
import { FaCamera, FaHistory, FaUtensils, FaSearch, FaStar, FaShareAlt } from 'react-icons/fa';
import './HomePage.css';

function HomePage() {
  return (
    <div className="home-page">
      <div className="hero-section">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">
              <FaUtensils className="hero-icon" />
              Foody
            </h1>
            <p className="hero-subtitle">
              Transform Any Menu Into An Interactive Experience
            </p>
            <p className="hero-description">
              Point your camera at any restaurant menu and watch as AI instantly converts it into a beautiful, searchable digital menu.
            </p>

            <div className="hero-buttons">
              <Link to="/camera" className="btn btn-primary btn-large">
                <FaCamera /> Scan Menu Now
              </Link>
              <Link to="/history" className="btn btn-secondary btn-large">
                <FaHistory /> View History
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="features-section">
        <div className="container">
          <h2 className="section-title">How It Works</h2>

          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <FaCamera />
              </div>
              <h3>1. Snap a Photo</h3>
              <p>Take a picture of any restaurant menu with your camera or upload from your gallery</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <FaUtensils />
              </div>
              <h3>2. AI Processing</h3>
              <p>Our advanced AI extracts menu items, prices, and descriptions in seconds</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <FaSearch />
              </div>
              <h3>3. Explore & Filter</h3>
              <p>Search, filter by category, dietary preferences, and browse your digital menu</p>
            </div>
          </div>

          <h2 className="section-title">Features</h2>

          <div className="features-list">
            <div className="feature-item">
              <FaCamera className="feature-list-icon" />
              <div>
                <h4>Instant Scanning</h4>
                <p>Capture menus in real-time with your device camera</p>
              </div>
            </div>

            <div className="feature-item">
              <FaStar className="feature-list-icon" />
              <div>
                <h4>Smart Categorization</h4>
                <p>Automatically organizes items by appetizers, mains, desserts, and more</p>
              </div>
            </div>

            <div className="feature-item">
              <FaSearch className="feature-list-icon" />
              <div>
                <h4>Advanced Search</h4>
                <p>Find exactly what you're looking for with powerful search and filters</p>
              </div>
            </div>

            <div className="feature-item">
              <FaUtensils className="feature-list-icon" />
              <div>
                <h4>Dietary Filters</h4>
                <p>Easily identify vegan, vegetarian, gluten-free, and other dietary options</p>
              </div>
            </div>

            <div className="feature-item">
              <FaHistory className="feature-list-icon" />
              <div>
                <h4>Menu History</h4>
                <p>Save and revisit all your scanned menus anytime</p>
              </div>
            </div>

            <div className="feature-item">
              <FaShareAlt className="feature-list-icon" />
              <div>
                <h4>Share & Export</h4>
                <p>Share your favorite menus with friends and family</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="cta-section">
        <div className="container">
          <h2>Ready to Get Started?</h2>
          <p>Transform your dining experience today</p>
          <Link to="/camera" className="btn btn-primary btn-large">
            <FaCamera /> Start Scanning
          </Link>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
