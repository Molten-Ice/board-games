import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { userAPI, taxonomyAPI } from '../services/api';
import { FaUtensils, FaFire, FaHeart, FaLeaf } from 'react-icons/fa';
import './OnboardingPage.css';

function OnboardingPage() {
  const [step, setStep] = useState(1);
  const [cuisines, setCuisines] = useState([]);
  const [dietary, setDietary] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [preferences, setPreferences] = useState({
    cuisine_ids: [],
    dietary_ids: [],
    price_preference: 'moderate',
    spice_tolerance: 3,
    adventurousness: 3,
    health_consciousness: 3,
  });

  const { updateUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadOptions();
  }, []);

  const loadOptions = async () => {
    try {
      const [cuisinesData, dietaryData] = await Promise.all([
        taxonomyAPI.getCuisines(),
        taxonomyAPI.getDietaryPreferences(),
      ]);

      setCuisines(cuisinesData.cuisines);
      setDietary(dietaryData.dietary_preferences);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load options:', err);
      setLoading(false);
    }
  };

  const toggleCuisine = (id) => {
    setPreferences((prev) => ({
      ...prev,
      cuisine_ids: prev.cuisine_ids.includes(id)
        ? prev.cuisine_ids.filter((cid) => cid !== id)
        : [...prev.cuisine_ids, id],
    }));
  };

  const toggleDietary = (id) => {
    setPreferences((prev) => ({
      ...prev,
      dietary_ids: prev.dietary_ids.includes(id)
        ? prev.dietary_ids.filter((did) => did !== id)
        : [...prev.dietary_ids, id],
    }));
  };

  const handleSubmit = async () => {
    setSubmitting(true);

    try {
      await userAPI.updatePreferences({
        ...preferences,
        onboarding_completed: true,
      });

      updateUser({ onboarding_completed: true });
      navigate('/');
    } catch (err) {
      console.error('Failed to save preferences:', err);
      alert('Failed to save preferences');
      setSubmitting(false);
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
    <div className="onboarding-page">
      <div className="onboarding-container">
        <div className="onboarding-header">
          <FaUtensils size={48} color="#667eea" />
          <h1>Let's personalize your experience</h1>
          <p>Help us understand your preferences to give you the best recommendations</p>
        </div>

        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${(step / 4) * 100}%` }}></div>
        </div>

        {step === 1 && (
          <div className="onboarding-step">
            <h2>What cuisines do you enjoy?</h2>
            <p>Select all that apply</p>

            <div className="options-grid">
              {cuisines.map((cuisine) => (
                <button
                  key={cuisine.id}
                  className={`option-btn ${preferences.cuisine_ids.includes(cuisine.id) ? 'selected' : ''}`}
                  onClick={() => toggleCuisine(cuisine.id)}
                >
                  {cuisine.name}
                </button>
              ))}
            </div>

            <div className="button-group">
              <button
                className="btn btn-primary"
                onClick={() => setStep(2)}
                disabled={preferences.cuisine_ids.length === 0}
              >
                Next
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="onboarding-step">
            <h2>Any dietary preferences?</h2>
            <p>Optional - select if applicable</p>

            <div className="options-grid">
              {dietary.map((diet) => (
                <button
                  key={diet.id}
                  className={`option-btn ${preferences.dietary_ids.includes(diet.id) ? 'selected' : ''}`}
                  onClick={() => toggleDietary(diet.id)}
                >
                  <FaLeaf /> {diet.name}
                </button>
              ))}
            </div>

            <div className="button-group">
              <button className="btn btn-secondary" onClick={() => setStep(1)}>
                Back
              </button>
              <button className="btn btn-primary" onClick={() => setStep(3)}>
                Next
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="onboarding-step">
            <h2>Price preference?</h2>

            <div className="options-grid">
              {['budget', 'moderate', 'expensive', 'luxury'].map((price) => (
                <button
                  key={price}
                  className={`option-btn ${preferences.price_preference === price ? 'selected' : ''}`}
                  onClick={() => setPreferences({ ...preferences, price_preference: price })}
                >
                  {price.charAt(0).toUpperCase() + price.slice(1)}
                </button>
              ))}
            </div>

            <div className="button-group">
              <button className="btn btn-secondary" onClick={() => setStep(2)}>
                Back
              </button>
              <button className="btn btn-primary" onClick={() => setStep(4)}>
                Next
              </button>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="onboarding-step">
            <h2>Final touches</h2>

            <div className="slider-group">
              <label>
                <FaFire /> Spice Tolerance (1-5)
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={preferences.spice_tolerance}
                onChange={(e) => setPreferences({ ...preferences, spice_tolerance: parseInt(e.target.value) })}
              />
              <span>{preferences.spice_tolerance}</span>
            </div>

            <div className="slider-group">
              <label>
                <FaHeart /> Adventurousness (1-5)
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={preferences.adventurousness}
                onChange={(e) => setPreferences({ ...preferences, adventurousness: parseInt(e.target.value) })}
              />
              <span>{preferences.adventurousness}</span>
            </div>

            <div className="slider-group">
              <label>
                <FaLeaf /> Health Consciousness (1-5)
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={preferences.health_consciousness}
                onChange={(e) => setPreferences({ ...preferences, health_consciousness: parseInt(e.target.value) })}
              />
              <span>{preferences.health_consciousness}</span>
            </div>

            <div className="button-group">
              <button className="btn btn-secondary" onClick={() => setStep(3)}>
                Back
              </button>
              <button className="btn btn-primary" onClick={handleSubmit} disabled={submitting}>
                {submitting ? 'Saving...' : 'Complete Setup'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default OnboardingPage;
