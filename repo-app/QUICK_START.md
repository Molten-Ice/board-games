# Quick Start Guide - Restaurant Recommender

Get the app running in 5 minutes!

## Prerequisites Check
```bash
# Check Python
python --version  # Should be 3.8+

# Check Node
node --version    # Should be 16+

# Check Tesseract
tesseract --version  # If not installed, see main README
```

## Step 1: Backend Setup (2 minutes)

```bash
# Navigate to backend
cd repo-app/enhanced_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database with Reading restaurants
python init_db.py

# Start backend server
python app_enhanced.py
```

✅ Backend running at http://localhost:5001

## Step 2: Frontend Setup (2 minutes)

Open a new terminal:

```bash
# Navigate to frontend
cd repo-app/enhanced_frontend

# Install dependencies
npm install

# Start frontend server
npm start
```

✅ Frontend running at http://localhost:3000

## Step 3: Try It Out! (1 minute)

1. **Register** at http://localhost:3000/register
   - Email: test@example.com
   - Username: testuser
   - Password: Test1234 (must have uppercase, lowercase, number)

2. **Complete Onboarding**
   - Select cuisines you like (e.g., Italian, Japanese)
   - Choose dietary preferences if applicable
   - Set price range
   - Adjust personality sliders

3. **Explore Restaurants**
   - View personalized recommendations on "For You" tab
   - Browse all 15+ Reading Oracle/Riverside restaurants
   - Click any restaurant to see menu and details
   - Rate restaurants to improve your recommendations

## Common Issues

### Backend won't start
- Activate virtual environment: `source venv/bin/activate`
- Check port 5001 isn't in use: `lsof -i :5001` (Mac/Linux)

### Frontend can't connect
- Verify backend is running on port 5001
- Check console for errors
- Clear browser cache

### Database errors
```bash
cd enhanced_backend
rm restaurant_recommender.db
python init_db.py
```

## What's Included

The initialized database contains:
- ✅ 15+ Oracle/Riverside Reading restaurants
- ✅ 25+ cuisine types
- ✅ 11 dietary preference options
- ✅ Sample menus for major restaurants
- ✅ Complete restaurant details (address, phone, website)

## Next Steps

- Rate some restaurants to see better recommendations
- Try the "Favorites" feature
- Upload a menu image to test OCR (coming soon)
- Adjust your preferences in the Profile page

## Need Help?

See the full [ENHANCED_APP_README.md](./ENHANCED_APP_README.md) for:
- Complete API documentation
- Security features
- Production deployment guide
- Architecture details
- Troubleshooting guide

---

**Ready for production?** See deployment checklist in main README.
