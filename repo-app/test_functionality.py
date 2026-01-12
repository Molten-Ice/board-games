#!/usr/bin/env python3
"""
Test script to verify menu processing functionality
"""
import requests
import base64
from PIL import Image, ImageDraw, ImageFont
import os
import sys

def create_test_menu_image():
    """Create a simple test menu image"""
    # Create a white background image
    width, height = 800, 1000
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Try to use a default font
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        font_item = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_price = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        # Fallback to default font
        font_title = ImageFont.load_default()
        font_item = ImageFont.load_default()
        font_price = ImageFont.load_default()

    # Draw menu content
    y = 50

    # Title
    draw.text((50, y), "Test Restaurant Menu", fill='black', font=font_title)
    y += 80

    # Appetizers
    draw.text((50, y), "APPETIZERS", fill='black', font=font_title)
    y += 60

    menu_items = [
        ("Spring Rolls (Vegan)", "Fresh vegetables wrapped in rice paper", "$6.99"),
        ("Chicken Wings (Spicy)", "Buffalo style with blue cheese", "$9.99"),
        ("Caesar Salad (Vegetarian)", "Romaine lettuce with parmesan", "$7.99"),
    ]

    for name, desc, price in menu_items:
        draw.text((50, y), name, fill='black', font=font_item)
        y += 30
        draw.text((70, y), desc, fill='gray', font=font_item)
        y += 30
        draw.text((50, y), price, fill='black', font=font_price)
        y += 50

    # Main Courses
    y += 30
    draw.text((50, y), "MAIN COURSES", fill='black', font=font_title)
    y += 60

    main_items = [
        ("Grilled Salmon", "With seasonal vegetables", "$18.99"),
        ("Beef Steak", "8oz ribeye with mashed potatoes", "$24.99"),
        ("Pasta Primavera (Vegetarian)", "Fresh vegetables in olive oil", "$14.99"),
    ]

    for name, desc, price in main_items:
        draw.text((50, y), name, fill='black', font=font_item)
        y += 30
        draw.text((70, y), desc, fill='gray', font=font_item)
        y += 30
        draw.text((50, y), price, fill='black', font=font_price)
        y += 50

    # Save image
    image_path = 'test_menu.jpg'
    image.save(image_path, 'JPEG', quality=95)
    print(f"✅ Created test menu image: {image_path}")
    return image_path

def test_api_health():
    """Test if API is running"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ API health check passed")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to API: {e}")
        print("   Make sure the backend is running on http://localhost:5000")
        return False

def test_menu_processing():
    """Test menu processing with a test image"""
    print("\n🔍 Testing menu processing...")

    # Create test image
    image_path = create_test_menu_image()

    # Convert to base64
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # Add data URL prefix
    image_data_url = f"data:image/jpeg;base64,{image_data}"

    # Send to API
    payload = {
        'imageData': image_data_url,
        'restaurantName': 'Test Restaurant'
    }

    try:
        print("📤 Sending request to API...")
        response = requests.post(
            'http://localhost:5000/api/process-menu',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Menu processing successful!")
            print(f"\n📊 Results:")
            print(f"   Menu ID: {result.get('menu_id')}")
            print(f"   Items found: {len(result.get('menu_data', {}).get('items', []))}")
            print(f"   Categories: {', '.join(result.get('menu_data', {}).get('categories', []))}")

            print(f"\n📝 Menu Items:")
            for item in result.get('menu_data', {}).get('items', [])[:5]:  # Show first 5
                print(f"   - {item.get('name')} ({item.get('category')}): {item.get('price')}")
                if item.get('dietary_tags'):
                    print(f"     Tags: {', '.join(item.get('dietary_tags'))}")

            # Test retrieving the menu
            menu_id = result.get('menu_id')
            if menu_id:
                print(f"\n🔄 Testing menu retrieval...")
                get_response = requests.get(f'http://localhost:5000/api/menus/{menu_id}')
                if get_response.status_code == 200:
                    print("✅ Menu retrieval successful!")
                else:
                    print(f"❌ Menu retrieval failed: {get_response.status_code}")

            # Cleanup
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"\n🧹 Cleaned up test image")

            return True
        else:
            print(f"❌ Menu processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out (processing takes too long)")
        return False
    except Exception as e:
        print(f"❌ Error during menu processing: {e}")
        return False

def test_menu_list():
    """Test getting list of menus"""
    print("\n📋 Testing menu list...")
    try:
        response = requests.get('http://localhost:5000/api/menus')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {len(result.get('menus', []))} menus in database")
            return True
        else:
            print(f"❌ Failed to get menu list: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting menu list: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Foody Menu App Tests\n")
    print("=" * 60)

    # Test 1: API Health
    if not test_api_health():
        print("\n❌ Cannot proceed with tests - API is not running")
        print("   Start the backend with: cd backend && python app.py")
        sys.exit(1)

    # Test 2: Menu Processing
    print("\n" + "=" * 60)
    success = test_menu_processing()

    # Test 3: Menu List
    print("\n" + "=" * 60)
    test_menu_list()

    # Summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed!")
        print("\nYou can now:")
        print("  1. Start the frontend: cd frontend && npm start")
        print("  2. Open http://localhost:3000 in your browser")
        print("  3. Test the full application flow")
    else:
        print("⚠️  Some tests failed - check the output above")

    print("=" * 60)

if __name__ == '__main__':
    main()
