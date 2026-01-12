import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FaUtensils, FaUser, FaSignOutAlt, FaHome } from 'react-icons/fa';
import './Navbar.css';

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <FaUtensils /> Restaurant Recommender
        </Link>

        <div className="navbar-menu">
          <Link to="/" className="nav-link">
            <FaHome /> Discover
          </Link>

          <Link to="/profile" className="nav-link">
            <FaUser /> {user?.display_name || user?.username}
          </Link>

          <button onClick={handleLogout} className="nav-link nav-button">
            <FaSignOutAlt /> Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
