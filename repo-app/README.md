# Foody Menu App

A complete menu photo scanning application that transforms physical restaurant menus into interactive digital experiences using AI and OCR technology.

## Features

### Core Functionality
- **📸 Camera Integration**: Capture menu photos in real-time using device camera
- **📤 File Upload**: Upload menu photos from device gallery
- **🤖 AI-Powered OCR**: Extract text, prices, and descriptions from menu images
- **🎯 Smart Categorization**: Automatically organize items by category (appetizers, mains, desserts, etc.)
- **🔍 Advanced Search**: Search menu items by name or description
- **🎛️ Filtering**: Filter by category and dietary preferences
- **⭐ Favorites**: Mark and filter favorite menus
- **📜 History**: View all previously scanned menus
- **🔗 Sharing**: Share menus with friends and family
- **🏷️ Dietary Tags**: Automatic detection of vegan, vegetarian, gluten-free, and other dietary options

### User Experience
- Beautiful, modern UI with gradient backgrounds
- Responsive design for mobile and desktop
- Interactive menu display with category grouping
- Real-time camera preview with flip camera support
- Loading states and error handling
- Empty states with helpful guidance

## Tech Stack

### Backend
- **Framework**: Flask (Python)
- **OCR**: Tesseract with pytesseract
- **Image Processing**: OpenCV, Pillow
- **Database**: SQLAlchemy with SQLite
- **API**: RESTful API with CORS support

### Frontend
- **Framework**: React 18
- **Routing**: React Router v6
- **Styling**: CSS3 with custom components
- **Icons**: React Icons
- **HTTP Client**: Axios
- **Camera**: MediaDevices API

## Project Structure

```
repo-app/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── database.py            # Database models (Menu, MenuItem)
│   ├── menu_processor.py     # OCR and menu processing logic
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment variables template
│
├── frontend/
│   ├── public/
│   │   └── index.html        # HTML template
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── pages/            # Page components
│   │   │   ├── HomePage.js
│   │   │   ├── CameraPage.js
│   │   │   ├── MenuViewPage.js
│   │   │   └── HistoryPage.js
│   │   ├── services/
│   │   │   └── api.js        # API service layer
│   │   ├── styles/           # CSS files
│   │   ├── App.js            # Main app component
│   │   └── index.js          # Entry point
│   └── package.json          # Node dependencies
│
└── README.md                 # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- Tesseract OCR

### Validate Your Setup

Before installing, check if you have all prerequisites:

```bash
python check_setup.py
```

This will verify:
- ✅ Python 3.8+ is installed
- ✅ Node.js 14+ is installed
- ✅ Tesseract OCR is installed
- ✅ Directory structure is correct

### Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### Backend Setup

1. Navigate to backend directory:
```bash
cd repo-app/backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
```

5. Run the backend:
```bash
python app.py
```

Backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd repo-app/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

Frontend will run on `http://localhost:3000`

## Usage

### Scanning a Menu

1. Click "Scan Menu Now" on the home page
2. Choose to either:
   - Open camera and capture a photo in real-time
   - Upload an existing photo from your device
3. Enter restaurant name (optional)
4. Click "Process Menu"
5. Wait for AI to extract menu items
6. Browse your interactive digital menu!

### Browsing Menus

- **Search**: Type in the search bar to find specific items
- **Filter by Category**: Click category filters to view specific sections
- **Filter by Dietary**: Filter by vegan, vegetarian, gluten-free, etc.
- **Favorite Items**: Click the star icon to mark favorites
- **Share**: Click share icon to share the menu

### Managing History

1. Click "View History" to see all scanned menus
2. Search for specific restaurants
3. Toggle "Favorites Only" to see starred menus
4. Click a menu to view it
5. Delete menus by clicking trash icon (requires confirmation)

## Testing

### Automated Testing

Test the core functionality with our automated test script:

```bash
# Make sure backend is running first
cd backend
python app.py

# In another terminal, run the test
cd repo-app
python test_functionality.py
```

The test script will:
- ✅ Verify API is running
- ✅ Create a test menu image
- ✅ Upload and process it
- ✅ Verify extraction results
- ✅ Test menu retrieval

### Manual Testing

See [TESTING.md](TESTING.md) for comprehensive testing guide including:
- Manual test cases
- Browser compatibility testing
- OCR accuracy testing
- Performance testing
- Debugging tips

## API Endpoints

### Menu Processing
- `POST /api/process-menu` - Process a menu image
  - Body: `{ imageData: string, restaurantName: string }` or FormData with image file

### Menu Management
- `GET /api/menus` - Get all menus
- `GET /api/menus/:id` - Get specific menu with items
- `DELETE /api/menus/:id` - Delete a menu
- `POST /api/menus/:id/favorite` - Toggle favorite status

### Search & Filter
- `GET /api/search?q=query&category=...&dietary=...` - Search menu items
- `GET /api/categories` - Get all available categories

### Health Check
- `GET /api/health` - Check API status

## Database Schema

### Menu Table
- `id` - Primary key
- `restaurant_name` - Name of restaurant
- `image_path` - Path to uploaded image
- `raw_text` - Raw OCR text
- `processed_data` - JSON of processed menu data
- `is_favorite` - Boolean favorite status
- `created_at` - Creation timestamp
- `updated_at` - Update timestamp

### MenuItem Table
- `id` - Primary key
- `menu_id` - Foreign key to Menu
- `name` - Item name
- `description` - Item description
- `price` - Item price
- `category` - Item category
- `dietary_tags` - JSON array of dietary tags
- `created_at` - Creation timestamp

## Features in Detail

### OCR Processing
The menu processor uses advanced image preprocessing techniques:
- Grayscale conversion
- Noise reduction with denoising
- Adaptive thresholding
- Morphological operations
- Multiple OCR passes for accuracy

### Smart Parsing
- Price extraction with multiple currency support
- Category detection using keyword matching
- Dietary tag detection (vegan, vegetarian, gluten-free, etc.)
- Item name and description separation
- Multi-line item support

### Categorization
Automatic categorization supports:
- Appetizers & Starters
- Soups & Salads
- Main Courses
- Pasta
- Seafood
- Meat
- Pizza
- Burgers & Sandwiches
- Desserts
- Drinks
- Breakfast
- Sides

### Dietary Detection
Automatically detects and tags:
- Vegan
- Vegetarian
- Gluten-free
- Dairy-free
- Nut-free
- Halal
- Kosher
- Spicy

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Note**: Camera functionality requires HTTPS in production (except localhost)

## Development

### Running Tests
```bash
# Backend
cd backend
python -m pytest

# Frontend
cd frontend
npm test
```

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
```

**Backend:**
```bash
cd backend
gunicorn app:app
```

## Troubleshooting

### Camera Not Working
- Check browser permissions for camera access
- Ensure you're on HTTPS (or localhost)
- Try uploading a file instead

### OCR Not Accurate
- Ensure good lighting when capturing
- Menu should be flat and not wrinkled
- Text should be clear and in focus
- Try preprocessing the image before upload

### Database Issues
- Delete `menus.db` and restart backend to reset database
- Check file permissions in upload folder

## Future Enhancements

- Multiple language support
- Nutritional information estimation
- Price comparison across restaurants
- Menu recommendations
- Export to PDF
- Integration with delivery services
- Collaborative menu editing
- Reviews and ratings

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## Credits

Built with:
- Flask
- React
- Tesseract OCR
- OpenCV
- SQLAlchemy
- React Icons

---

**Enjoy your digital menu experience! 🍽️**
