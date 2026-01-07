# Testing Guide for Foody Menu App

This guide will help you test the menu photo processing functionality.

## Quick Test

The easiest way to test is to use our automated test script:

```bash
# 1. Start the backend first
cd repo-app/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

# 2. In a new terminal, run the test script
cd repo-app
python test_functionality.py
```

The test script will:
- ✅ Check if the backend is running
- ✅ Create a test menu image
- ✅ Upload and process it
- ✅ Verify the results
- ✅ Test menu retrieval

## Manual Testing

### 1. Backend Testing

**Test the API health:**
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-07T..."
}
```

**Test menu processing with a file:**

First, download or create a menu image, then:

```bash
curl -X POST http://localhost:5000/api/process-menu \
  -F "image=@path/to/menu.jpg" \
  -F "restaurantName=Test Restaurant"
```

**Test menu retrieval:**
```bash
curl http://localhost:5000/api/menus
```

### 2. Frontend Testing

**Start the frontend:**
```bash
cd repo-app/frontend
npm install
npm start
```

**Test flow:**

1. **Home Page** (http://localhost:3000)
   - ✅ Verify hero section displays
   - ✅ Click "Scan Menu Now" button
   - ✅ Click "View History" button

2. **Camera Page** (/camera)
   - ✅ Click "Open Camera" - should request camera permission
   - ✅ If camera works, capture a photo
   - ✅ Try "Choose File" to upload from computer
   - ✅ Enter restaurant name
   - ✅ Click "Process Menu"
   - ✅ Verify loading state shows
   - ✅ Verify redirect to menu view

3. **Menu View Page** (/menu/:id)
   - ✅ Verify menu items display
   - ✅ Test search functionality
   - ✅ Test category filters
   - ✅ Test dietary filters
   - ✅ Click star to favorite
   - ✅ Test share button
   - ✅ Verify items grouped by category

4. **History Page** (/history)
   - ✅ Verify all menus display
   - ✅ Test search
   - ✅ Toggle favorites filter
   - ✅ Click a menu to view it
   - ✅ Delete a menu (requires confirmation)
   - ✅ Test floating action button

## Test Cases

### Test Case 1: Camera Capture
**Objective:** Verify camera integration works

**Steps:**
1. Navigate to /camera
2. Click "Open Camera"
3. Allow camera permissions
4. Point camera at a menu (or any text)
5. Click capture button
6. Enter restaurant name
7. Click "Process Menu"

**Expected:** Should successfully capture, process, and display menu

### Test Case 2: File Upload
**Objective:** Verify file upload works

**Steps:**
1. Navigate to /camera
2. Click "Choose File"
3. Select a menu image
4. Verify preview shows
5. Enter restaurant name
6. Click "Process Menu"

**Expected:** Should successfully process and display menu

### Test Case 3: Search and Filter
**Objective:** Verify search and filtering work

**Steps:**
1. Process a menu with multiple items
2. Navigate to menu view
3. Type in search box
4. Verify matching items display
5. Clear search
6. Select a category filter
7. Verify only items in that category show
8. Select a dietary filter
9. Verify only matching items show

**Expected:** All filters should work correctly

### Test Case 4: Favorites
**Objective:** Verify favorite functionality

**Steps:**
1. View a menu
2. Click star icon to favorite
3. Navigate to history
4. Toggle "Favorites Only"
5. Verify favorited menu shows

**Expected:** Favorite status persists and filtering works

### Test Case 5: Delete Menu
**Objective:** Verify delete functionality

**Steps:**
1. Go to history
2. Click trash icon on a menu
3. Should show confirmation message
4. Click trash again to confirm
5. Verify menu is deleted

**Expected:** Menu should be removed from list

## Testing with Real Menu Photos

For best results, test with actual restaurant menu photos:

**Good test images:**
- ✅ Well-lit menu photos
- ✅ Clear, readable text
- ✅ Flat menu (not folded)
- ✅ Direct overhead shot

**Where to find test images:**
- Take a photo of a physical menu
- Download menu images from restaurant websites
- Search "restaurant menu" on image search
- Use sample menus from this repository (if available)

## OCR Accuracy Testing

The OCR accuracy depends on:

1. **Image Quality**
   - Resolution: Higher is better
   - Lighting: Even, bright lighting
   - Focus: Sharp, in-focus text
   - Angle: Straight-on, not skewed

2. **Menu Design**
   - Font size: Larger fonts work better
   - Font style: Simple fonts work better
   - Contrast: Dark text on light background
   - Layout: Clean, organized layout

**Tips for better results:**
- Ensure good lighting when capturing
- Hold camera steady
- Get close enough for text to be readable
- Avoid shadows and glare
- Menu should be flat and straight

## Common Issues and Solutions

### Issue: "Camera not working"
**Solution:**
- Check browser permissions
- Use HTTPS (localhost works on HTTP)
- Try a different browser
- Use file upload instead

### Issue: "No items extracted"
**Solution:**
- Verify image has clear, readable text
- Try different lighting
- Use higher resolution image
- Ensure menu has visible prices

### Issue: "Backend not responding"
**Solution:**
- Verify backend is running: `curl http://localhost:5000/api/health`
- Check backend logs for errors
- Ensure Tesseract is installed: `tesseract --version`
- Check uploads folder permissions

### Issue: "Poor parsing results"
**Solution:**
- This is normal - OCR isn't perfect
- Try a clearer photo
- Manually check what OCR extracted (raw_text in response)
- Consider preprocessing the image

## Performance Testing

**Test upload limits:**
- Maximum file size: 16MB
- Recommended: Under 5MB
- Large images take longer to process

**Expected processing times:**
- Small menu (< 1MB): 2-5 seconds
- Medium menu (1-3MB): 5-10 seconds
- Large menu (3-5MB): 10-20 seconds

## Integration Testing

**Full workflow test:**
1. Start backend
2. Start frontend
3. Open browser to http://localhost:3000
4. Navigate through all pages
5. Process a menu
6. Search and filter
7. Favorite a menu
8. View history
9. Delete a menu
10. Process another menu

## Browser Compatibility

Test in multiple browsers:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

**Mobile testing:**
- Test on actual mobile devices if possible
- Use browser dev tools device emulation
- Verify camera works on mobile
- Check responsive design

## Debugging

**Enable verbose logging:**

Backend:
```python
# In app.py, set debug=True
app.run(debug=True, host='0.0.0.0', port=5000)
```

Frontend:
```javascript
// Check browser console for errors
// Check Network tab for API calls
```

**Check logs:**
- Backend prints to console
- Frontend errors in browser console
- Network errors in browser DevTools

## Automated Testing

For automated tests, check:
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Report Issues

If you find bugs:
1. Note the steps to reproduce
2. Capture screenshots
3. Check browser console for errors
4. Check backend logs
5. Create an issue on GitHub

---

**Happy Testing! 🧪📸**
