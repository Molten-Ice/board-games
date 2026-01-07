# Foody Menu App - Quick Start Guide

Get up and running with Foody Menu App in just a few minutes!

## Prerequisites Check

Before starting, make sure you have:

- [ ] Python 3.8 or higher installed
- [ ] Node.js 14 or higher installed
- [ ] Tesseract OCR installed
- [ ] Git installed (optional, for cloning)

### Quick Install Commands

**Tesseract OCR:**
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

**Verify installations:**
```bash
python --version   # Should be 3.8+
node --version     # Should be 14+
tesseract --version # Should show Tesseract version
```

## Option 1: Automated Start (Recommended)

### macOS/Linux:
```bash
cd repo-app
./start.sh
```

### Windows:
```bash
cd repo-app
start.bat
```

The script will:
- ✅ Check for Tesseract installation
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Start both backend and frontend
- ✅ Open browser to http://localhost:3000

## Option 2: Manual Start

### Step 1: Start Backend

```bash
cd repo-app/backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start server
python app.py
```

Backend will run on `http://localhost:5000`

### Step 2: Start Frontend (in new terminal)

```bash
cd repo-app/frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will open automatically at `http://localhost:3000`

## Option 3: Docker (Advanced)

```bash
cd repo-app
docker-compose up
```

Both services will start in containers.

## First Use

1. **Open browser** to http://localhost:3000
2. **Click "Scan Menu Now"**
3. **Choose an option:**
   - "Open Camera" to capture live
   - "Choose File" to upload existing photo
4. **Take/select a photo** of a menu
5. **Enter restaurant name** (optional)
6. **Click "Process Menu"**
7. **Browse your digital menu!**

## Testing the App

### Test with Sample Menu

Don't have a menu photo? Try:
1. Google "restaurant menu" and download any clear menu image
2. Or use the file upload to test with any menu photo
3. Take a photo of a menu from a physical restaurant

### What Makes a Good Menu Photo?

✅ **Good:**
- Well-lit
- Clear text
- Flat surface
- In focus
- Minimal glare

❌ **Avoid:**
- Dark/shadowy
- Blurry text
- Wrinkled/folded
- Too far away
- Excessive glare

## Common Issues & Solutions

### "Camera not working"
- **Solution**: Allow camera permissions in browser settings
- **Alternative**: Use file upload instead

### "Tesseract not found"
- **Solution**: Install Tesseract OCR (see prerequisites)
- **Verify**: Run `tesseract --version` in terminal

### "Port already in use"
- **Backend (5000)**: Stop other Flask apps or change port in `app.py`
- **Frontend (3000)**: Stop other React apps or set `PORT=3001` before `npm start`

### "Dependencies won't install"
- **Python**: Ensure virtual environment is activated
- **Node**: Try deleting `node_modules` and running `npm install` again
- **macOS**: May need to install Xcode Command Line Tools

### "Poor OCR results"
- **Solution**:
  - Take a clearer photo
  - Ensure good lighting
  - Menu should be flat
  - Text should be in focus

## Quick Tips

💡 **Better Results:**
- Use good lighting when capturing
- Keep menu flat and straight
- Get close enough to read text clearly
- Avoid shadows and glare

💡 **Organizing Menus:**
- Star your favorites for quick access
- Use descriptive restaurant names
- Delete old/test menus to keep things tidy

💡 **Searching:**
- Search works across all item names and descriptions
- Filter by category to narrow results
- Use dietary filters to find specific options

## Next Steps

Now that you're set up:

1. **Scan some menus** - Try different restaurants
2. **Explore features** - Search, filter, favorites
3. **Check history** - View all your scanned menus
4. **Share menus** - Send to friends and family

## Need Help?

- 📖 Read the full [README.md](README.md)
- 🐛 Found a bug? Create an issue
- 💡 Have an idea? Check [CONTRIBUTING.md](CONTRIBUTING.md)
- ❓ Questions? Check existing issues first

## Development Mode

Want to modify the code?

**Backend Hot Reload:**
```bash
# Install flask in dev mode
export FLASK_ENV=development  # macOS/Linux
set FLASK_ENV=development     # Windows
python app.py
```

**Frontend Hot Reload:**
- Already enabled by default with `npm start`
- Changes auto-reload in browser

## Production Build

### Frontend:
```bash
cd frontend
npm run build
```

Creates optimized production build in `frontend/build/`

### Backend:
```bash
cd backend
gunicorn app:app
```

Runs production server with Gunicorn

## Shutting Down

**Automated scripts:**
- Press `Ctrl+C` to stop both servers

**Manual:**
- Press `Ctrl+C` in each terminal window
- Deactivate Python venv: `deactivate`

---

**Happy menu scanning! 🍽️📸**

Need more details? Check out the comprehensive [README.md](README.md)
