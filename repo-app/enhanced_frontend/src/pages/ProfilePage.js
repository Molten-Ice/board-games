import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { userAPI, taxonomyAPI } from '../services/api';
import { FaUser, FaMapMarkerAlt, FaCog, FaHeart } from 'react-icons/fa';
import './ProfilePage.css';

function ProfilePage() {
  const { user, updateUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [cuisines, setCuisines] = useState([]);
  const [dietary, setDietary] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    display_name: '',
    location: '',
    cuisine_ids: [],
    dietary_ids: [],
    price_preference: 'moderate',
    spice_tolerance: 3,
    adventurousness: 3,
    health_consciousness: 3,
  });

  useEffect(() => {
    loadData();
  }, [user]);

  const loadData = async () => {
    try {
      const [cuisinesData, dietaryData] = await Promise.all([
        taxonomyAPI.getCuisines(),
        taxonomyAPI.getDietaryPreferences(),
      ]);

      setCuisines(cuisinesData.cuisines);
      setDietary(dietaryData.dietary_preferences);

      if (user) {
        const prefs = user.preferences || {};
        setFormData({
          display_name: user.display_name || '',
          location: user.location || '',
          cuisine_ids: cuisines.filter(c => prefs.cuisines?.includes(c.name)).map(c => c.id) || [],
          dietary_ids: dietary.filter(d => prefs.dietary?.includes(d.name)).map(d => d.id) || [],
          price_preference: prefs.price || 'moderate',
          spice_tolerance: prefs.spice_tolerance || 3,
          adventurousness: prefs.adventurousness || 3,
          health_consciousness: prefs.health_consciousness || 3,
        });
      }

      setLoading(false);
    } catch (err) {
      console.error('Failed to load data:', err);
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const toggleCuisine = (id) => {
    setFormData((prev) => ({
      ...prev,
      cuisine_ids: prev.cuisine_ids.includes(id)
        ? prev.cuisine_ids.filter((cid) => cid !== id)
        : [...prev.cuisine_ids, id],
    }));
  };

  const toggleDietary = (id) => {
    setFormData((prev) => ({
      ...prev,
      dietary_ids: prev.dietary_ids.includes(id)
        ? prev.dietary_ids.filter((did) => did !== id)
        : [...prev.dietary_ids, id],
    }));
  };

  const handleSave = async () => {
    setSaving(true);

    try {
      // Update profile
      await userAPI.updateProfile({
        display_name: formData.display_name,
        location: formData.location,
      });

      // Update preferences
      await userAPI.updatePreferences({
        cuisine_ids: formData.cuisine_ids,
        dietary_ids: formData.dietary_ids,
        price_preference: formData.price_preference,
        spice_tolerance: formData.spice_tolerance,
        adventurousness: formData.adventurousness,
        health_consciousness: formData.health_consciousness,
      });

      updateUser({
        display_name: formData.display_name,
        location: formData.location,
      });

      setEditing(false);
    } catch (err) {
      console.error('Failed to save profile:', err);
      alert('Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="profile-header">
        <FaUser size={64} />
        <h1>{user?.display_name || user?.username}</h1>
        <p>{user?.email}</p>
      </div>

      <div className="profile-content">
        <div className="profile-section">
          <div className="section-header">
            <h2><FaUser /> Profile Information</h2>
            {!editing && (
              <button className="btn btn-outline" onClick={() => setEditing(true)}>
                <FaCog /> Edit
              </button>
            )}
          </div>

          {editing ? (
            <div className="edit-form">
              <div className="form-group">
                <label>Display Name</label>
                <input
                  type="text"
                  name="display_name"
                  value={formData.display_name}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Location</label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  placeholder="e.g., Reading, UK"
                />
              </div>

              <div className="button-group">
                <button className="btn btn-secondary" onClick={() => setEditing(false)}>
                  Cancel
                </button>
                <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          ) : (
            <div className="profile-info">
              <div className="info-row">
                <strong>Display Name:</strong>
                <span>{user?.display_name || 'Not set'}</span>
              </div>
              <div className="info-row">
                <strong><FaMapMarkerAlt /> Location:</strong>
                <span>{user?.location || 'Not set'}</span>
              </div>
            </div>
          )}
        </div>

        <div className="profile-section">
          <div className="section-header">
            <h2><FaHeart /> Preferences</h2>
          </div>

          {editing ? (
            <div className="preferences-edit">
              <div className="pref-group">
                <h3>Favorite Cuisines</h3>
                <div className="options-grid">
                  {cuisines.map((cuisine) => (
                    <button
                      key={cuisine.id}
                      className={`option-btn ${formData.cuisine_ids.includes(cuisine.id) ? 'selected' : ''}`}
                      onClick={() => toggleCuisine(cuisine.id)}
                    >
                      {cuisine.name}
                    </button>
                  ))}
                </div>
              </div>

              <div className="pref-group">
                <h3>Dietary Preferences</h3>
                <div className="options-grid">
                  {dietary.map((diet) => (
                    <button
                      key={diet.id}
                      className={`option-btn ${formData.dietary_ids.includes(diet.id) ? 'selected' : ''}`}
                      onClick={() => toggleDietary(diet.id)}
                    >
                      {diet.name}
                    </button>
                  ))}
                </div>
              </div>

              <div className="pref-group">
                <h3>Price Preference</h3>
                <select name="price_preference" value={formData.price_preference} onChange={handleChange}>
                  <option value="budget">Budget</option>
                  <option value="moderate">Moderate</option>
                  <option value="expensive">Expensive</option>
                  <option value="luxury">Luxury</option>
                </select>
              </div>

              <div className="pref-group">
                <h3>Spice Tolerance (1-5): {formData.spice_tolerance}</h3>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={formData.spice_tolerance}
                  onChange={(e) => setFormData({ ...formData, spice_tolerance: parseInt(e.target.value) })}
                />
              </div>

              <div className="pref-group">
                <h3>Adventurousness (1-5): {formData.adventurousness}</h3>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={formData.adventurousness}
                  onChange={(e) => setFormData({ ...formData, adventurousness: parseInt(e.target.value) })}
                />
              </div>

              <div className="pref-group">
                <h3>Health Consciousness (1-5): {formData.health_consciousness}</h3>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={formData.health_consciousness}
                  onChange={(e) => setFormData({ ...formData, health_consciousness: parseInt(e.target.value) })}
                />
              </div>
            </div>
          ) : (
            <div className="preferences-view">
              <div className="pref-item">
                <strong>Price Preference:</strong>
                <span className="price-badge">{user?.preferences?.price || 'moderate'}</span>
              </div>

              <div className="pref-item">
                <strong>Favorite Cuisines:</strong>
                <div className="cuisines">
                  {user?.preferences?.cuisines?.map((cuisine, idx) => (
                    <span key={idx} className="cuisine-tag">{cuisine}</span>
                  ))}
                </div>
              </div>

              {user?.preferences?.dietary && user.preferences.dietary.length > 0 && (
                <div className="pref-item">
                  <strong>Dietary Preferences:</strong>
                  <div className="cuisines">
                    {user.preferences.dietary.map((diet, idx) => (
                      <span key={idx} className="dietary-tag">{diet}</span>
                    ))}
                  </div>
                </div>
              )}

              <div className="pref-item">
                <strong>Spice Tolerance:</strong>
                <span>{user?.preferences?.spice_tolerance || 3}/5</span>
              </div>

              <div className="pref-item">
                <strong>Adventurousness:</strong>
                <span>{user?.preferences?.adventurousness || 3}/5</span>
              </div>

              <div className="pref-item">
                <strong>Health Consciousness:</strong>
                <span>{user?.preferences?.health_consciousness || 3}/5</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;
