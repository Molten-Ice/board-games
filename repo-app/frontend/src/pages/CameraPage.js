import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaCamera, FaUpload, FaTimes, FaArrowLeft, FaSync } from 'react-icons/fa';
import { menuAPI } from '../services/api';
import './CameraPage.css';

function CameraPage() {
  const [cameraActive, setCameraActive] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const [restaurantName, setRestaurantName] = useState('');
  const [facingMode, setFacingMode] = useState('environment');

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const streamRef = useRef(null);

  const navigate = useNavigate();

  useEffect(() => {
    return () => {
      // Cleanup camera stream on unmount
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startCamera = async () => {
    try {
      setError('');
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: facingMode },
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraActive(true);
      }
    } catch (err) {
      console.error('Camera error:', err);
      setError('Could not access camera. Please check permissions or use file upload.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

  const switchCamera = async () => {
    stopCamera();
    setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
    setTimeout(() => startCamera(), 100);
  };

  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (video && canvas) {
      const context = canvas.getContext('2d');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      const imageData = canvas.toDataURL('image/jpeg');
      setCapturedImage(imageData);
      stopCamera();
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCapturedImage(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const retakePhoto = () => {
    setCapturedImage(null);
    setError('');
    startCamera();
  };

  const processMenu = async () => {
    if (!capturedImage) {
      setError('Please capture or upload a photo first');
      return;
    }

    setProcessing(true);
    setError('');

    try {
      const result = await menuAPI.processMenu(
        capturedImage,
        restaurantName || 'Unknown Restaurant'
      );

      if (result.success) {
        // Navigate to menu view page
        navigate(`/menu/${result.menu_id}`);
      } else {
        setError(result.error || 'Failed to process menu');
      }
    } catch (err) {
      console.error('Processing error:', err);
      setError(err.error || 'Failed to process menu. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="camera-page">
      <div className="camera-header">
        <button className="back-btn" onClick={() => navigate('/')}>
          <FaArrowLeft /> Back
        </button>
        <h1>Scan Menu</h1>
        <div></div>
      </div>

      <div className="camera-container">
        {!cameraActive && !capturedImage && (
          <div className="camera-options">
            <div className="option-card">
              <h2>Capture Menu Photo</h2>
              <p>Use your device camera to scan a menu in real-time</p>
              <button className="btn btn-primary" onClick={startCamera}>
                <FaCamera /> Open Camera
              </button>
            </div>

            <div className="divider">OR</div>

            <div className="option-card">
              <h2>Upload from Gallery</h2>
              <p>Select a menu photo from your device</p>
              <button
                className="btn btn-secondary"
                onClick={() => fileInputRef.current.click()}
              >
                <FaUpload /> Choose File
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
            </div>
          </div>
        )}

        {cameraActive && (
          <div className="camera-view">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="video-feed"
            />
            <canvas ref={canvasRef} style={{ display: 'none' }} />

            <div className="camera-controls">
              <button className="control-btn" onClick={stopCamera}>
                <FaTimes /> Cancel
              </button>
              <button className="control-btn capture-btn" onClick={capturePhoto}>
                <div className="capture-circle"></div>
              </button>
              <button className="control-btn" onClick={switchCamera}>
                <FaSync /> Flip
              </button>
            </div>
          </div>
        )}

        {capturedImage && !processing && (
          <div className="image-preview">
            <img src={capturedImage} alt="Captured menu" className="preview-image" />

            <div className="preview-form">
              <label htmlFor="restaurant-name">
                Restaurant Name (Optional)
              </label>
              <input
                id="restaurant-name"
                type="text"
                placeholder="Enter restaurant name..."
                value={restaurantName}
                onChange={(e) => setRestaurantName(e.target.value)}
                className="input-field"
              />

              <div className="preview-controls">
                <button className="btn btn-secondary" onClick={retakePhoto}>
                  <FaCamera /> Retake
                </button>
                <button className="btn btn-primary" onClick={processMenu}>
                  <FaUpload /> Process Menu
                </button>
              </div>
            </div>
          </div>
        )}

        {processing && (
          <div className="processing-view">
            <div className="spinner"></div>
            <h2>Processing Menu...</h2>
            <p>Our AI is extracting menu items, prices, and categories</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}

export default CameraPage;
