# Restaurant Recommender - Enhanced Application

**Tagline:** "Like you have a friend in town who knows where you'll like eating"

A personalized restaurant recommendation system with menu digitization at its core, focused on Reading, UK (RG5) area restaurants, particularly the Oracle/Riverside district.

## 🌟 Key Features

- **Strong Personalization**: Hybrid recommendation engine combining collaborative filtering, content-based filtering, and preference matching
- **Menu Digitizer**: OCR-powered menu scanning and digitization (inherited from original app)
- **Smart Onboarding**: 4-step preference collection for immediate personalization
- **Restaurant Discovery**: Browse personalized recommendations, all restaurants, or favorites
- **Detailed Restaurant Pages**: View menus, ratings, and restaurant information
- **User Profiles**: Manage preferences and view dining history
- **Reading UK Focus**: Curated list of 15+ Oracle/Riverside restaurants with complete data

## 🏗️ Architecture

### Backend (`enhanced_backend/`)
- **Framework**: Flask with SQLAlchemy ORM
- **Authentication**: JWT tokens with refresh mechanism
- **Database**: SQLite (dev) / PostgreSQL (production ready)
- **OCR**: Tesseract for menu image processing
- **Recommendation Engine**: Hybrid algorithm with weighted scoring

### Frontend (`enhanced_frontend/`)
- **Framework**: React 18 with React Router v6
- **State Management**: Context API for authentication
- **API Communication**: Axios with interceptors
- **Styling**: Custom CSS with responsive design
- **Icons**: React Icons

## 📋 Prerequisites

### Backend Requirements
- Python 3.8+
- Tesseract OCR
- pip (Python package manager)

### Frontend Requirements
- Node.js 16+
- npm or yarn

### System Setup
Install Tesseract OCR:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

## 🚀 Installation & Setup

### 1. Backend Setup

```bash
cd repo-app/enhanced_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Initialize database with Reading restaurants
python init_db.py

# Run development server
python app_enhanced.py
```

Backend will be available at `http://localhost:5001`

### 2. Frontend Setup

```bash
cd repo-app/enhanced_frontend

# Install dependencies
npm install

# Copy environment file and configure
cp .env.example .env
# Edit .env with your API URL

# Run development server
npm start
```

Frontend will be available at `http://localhost:3000`

## 🗄️ Database Models

### Core Models
- **User**: Authentication, preferences, onboarding status
- **Restaurant**: Complete restaurant information with location, cuisines, ratings
- **Menu**: Menu metadata linked to restaurants
- **MenuItem**: Individual menu items with prices, descriptions, dietary tags
- **Rating**: User ratings and reviews for restaurants
- **Cuisine**: Cuisine types (many-to-many with restaurants and users)
- **DietaryPreference**: Dietary requirements (vegan, vegetarian, gluten-free, etc.)
- **RestaurantVisit**: Track user visits for recommendation engine
- **Favorite**: User favorite restaurants

## 🎯 Recommendation Algorithm

The hybrid recommendation engine uses weighted scoring:

1. **Collaborative Filtering (30%)**: Find similar users and their preferences
2. **Content-Based Filtering (40%)**: Match restaurant attributes to user preferences
3. **Preference Matching (30%)**: Direct cuisine and dietary requirement matches
4. **Recency Boost (10%)**: Bonus for newly added restaurants

### Scoring Factors
- Price range match
- Cuisine preferences
- Dietary requirements
- Ambiance preferences
- Average ratings
- User adventurousness level
- Spice tolerance
- Health consciousness

## 🔐 Security Features

### Authentication
- JWT access tokens (1 hour expiry)
- JWT refresh tokens (30 day expiry)
- Token blocklist for logout
- Secure password hashing (werkzeug)

### Input Validation
- Email format validation
- Strong password requirements (8+ chars, uppercase, lowercase, number)
- Username validation (alphanumeric, hyphens, underscores only)
- File upload restrictions (images only: png, jpg, jpeg, gif, webp)
- Sanitized filenames for safe storage
- Rating bounds checking (1-5)
- Review text length limits (2000 chars max)

### Protection
- CORS configuration for specific origins
- SQL injection prevention (SQLAlchemy parameterized queries)
- XSS protection through input sanitization
- File upload size limits (16MB max)
- Secure filename handling

## 📁 Project Structure

```
repo-app/
├── enhanced_backend/
│   ├── app_enhanced.py          # Main Flask application
│   ├── models.py                # Database models
│   ├── recommender.py           # Recommendation engine
│   ├── scraper.py               # Reading restaurant data
│   ├── init_db.py               # Database initialization
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Environment template
├── enhanced_frontend/
│   ├── src/
│   │   ├── components/          # Reusable components (Navbar)
│   │   ├── context/             # AuthContext for state
│   │   ├── pages/               # Main page components
│   │   │   ├── LoginPage.js
│   │   │   ├── RegisterPage.js
│   │   │   ├── OnboardingPage.js
│   │   │   ├── DiscoveryPage.js
│   │   │   ├── RestaurantDetailPage.js
│   │   │   └── ProfilePage.js
│   │   ├── services/
│   │   │   └── api.js           # API service layer
│   │   ├── App.js               # Main app with routing
│   │   └── index.js             # Entry point
│   ├── package.json             # Node dependencies
│   └── .env.example             # Environment template
└── backend/                     # Original menu digitizer code
    └── menu_processor.py        # OCR processing logic
```

## 🔄 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout (revoke token)
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user

### Users
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update profile
- `PUT /api/user/preferences` - Update preferences
- `GET /api/user/favorites` - Get favorite restaurants

### Restaurants
- `GET /api/restaurants` - List all restaurants
- `GET /api/restaurants/:id` - Get restaurant details
- `GET /api/restaurants/:id/menu` - Get restaurant menu
- `POST /api/restaurants/:id/rate` - Rate restaurant
- `POST /api/restaurants/:id/favorite` - Toggle favorite
- `POST /api/restaurants/:id/visit` - Mark as visited
- `GET /api/restaurants/:id/similar` - Get similar restaurants

### Recommendations
- `GET /api/recommendations` - Get personalized recommendations

### Taxonomies
- `GET /api/cuisines` - List all cuisines
- `GET /api/dietary-preferences` - List dietary preferences

### Menu Processing
- `POST /api/menu/upload` - Upload menu image for OCR processing

## 🧪 Development Workflow

### Testing the Application

1. **Initialize with Sample Data**
```bash
cd enhanced_backend
python init_db.py
```

2. **Create Test User**
- Navigate to `http://localhost:3000/register`
- Create account with valid email and strong password

3. **Complete Onboarding**
- Select favorite cuisines (e.g., Italian, Japanese, British)
- Set dietary preferences if applicable
- Choose price range
- Adjust personality sliders

4. **Browse Recommendations**
- View personalized "For You" tab
- Click on restaurants to see details
- Rate restaurants to improve recommendations

### Database Management

Reset database:
```bash
cd enhanced_backend
rm restaurant_recommender.db
python init_db.py
```

## 📊 Curated Restaurants

The app includes 15+ Reading Oracle/Riverside restaurants:

1. **Bill's Reading** - British, Breakfast
2. **Côte Brasserie** - French
3. **Nando's Reading Oracle** - Portuguese, Chicken
4. **Las Iguanas** - Latin American
5. **Wagamama Reading** - Japanese, Asian
6. **Zizzi** - Italian, Pizza
7. **Pho** - Vietnamese
8. **Turtle Bay** - Caribbean
9. **Miller & Carter** - Steakhouse
10. **The Real Greek** - Greek
11. **Tampopo** - Asian, Noodles
12. **Byron Burgers** - American, Burgers
13. **Carluccio's** - Italian
14. **Jamie's Italian** - Italian
15. **Robata Bar & Grill** - Japanese, Asian Fusion

Each restaurant includes:
- Complete address and contact information
- Cuisine types
- Price range
- Sample menu items (where available)
- Ambiance description
- Features (parking, outdoor seating, reservations, delivery)

## 🚀 Production Deployment

### Backend Production Checklist

1. **Environment Variables**
   - Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
   - Configure PostgreSQL `DATABASE_URL`
   - Set `FLASK_ENV=production`
   - Enable `JWT_COOKIE_SECURE=True`

2. **Database**
   - Use PostgreSQL instead of SQLite
   - Run migrations
   - Set up regular backups

3. **Security**
   - Enable HTTPS
   - Configure proper CORS origins
   - Set up rate limiting
   - Use Redis for token blocklist
   - Enable security headers

4. **Server**
   - Use production WSGI server (Gunicorn/uWSGI)
   - Set up reverse proxy (Nginx)
   - Configure SSL certificates
   - Enable gzip compression

### Frontend Production Checklist

1. **Build**
```bash
npm run build
```

2. **Environment**
   - Set production `REACT_APP_API_URL`
   - Configure CDN if using

3. **Deployment**
   - Deploy build folder to hosting service
   - Configure routing for SPA
   - Enable caching headers

### Recommended Stack
- **Backend**: Gunicorn + Nginx on Ubuntu/Debian VPS
- **Database**: PostgreSQL 12+
- **Frontend**: Netlify, Vercel, or S3 + CloudFront
- **File Storage**: S3 or similar for menu images
- **Caching**: Redis for tokens and recommendations

## 🐛 Troubleshooting

### Backend Issues

**Database errors:**
```bash
# Reset database
rm restaurant_recommender.db
python init_db.py
```

**Import errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Tesseract not found:**
- Install Tesseract OCR system-wide
- Add to PATH if on Windows

### Frontend Issues

**API connection refused:**
- Check backend is running on port 5001
- Verify `REACT_APP_API_URL` in `.env`
- Check CORS configuration in backend

**Build errors:**
```bash
rm -rf node_modules package-lock.json
npm install
```

## 📝 Future Enhancements

- [ ] Real-time restaurant availability checking
- [ ] Geolocation-based distance filtering
- [ ] Social features (friend recommendations, dining groups)
- [ ] Advanced filters (cuisine combos, specific dietary needs)
- [ ] Reservation integration
- [ ] Email notifications for new restaurants matching preferences
- [ ] Mobile app (React Native)
- [ ] Admin dashboard for restaurant management
- [ ] Review moderation and flagging
- [ ] Integration with Google Maps/Places API
- [ ] Multi-city expansion beyond Reading

## 📄 License

This project is part of the board-games repository and follows its licensing terms.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Test thoroughly with the Reading restaurant dataset
2. Ensure security validations are maintained
3. Update documentation for new features
4. Follow existing code style

## 📧 Support

For issues or questions:
- Check the troubleshooting section
- Review API endpoint documentation
- Verify environment configuration

---

Built with ❤️ for the Reading, UK food community
