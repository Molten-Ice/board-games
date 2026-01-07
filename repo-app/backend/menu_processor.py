import cv2
import pytesseract
import numpy as np
from PIL import Image
import re
import os
from typing import Dict, List, Any

class MenuProcessor:
    """Process menu images and extract structured data"""

    def __init__(self):
        """Initialize the menu processor"""
        self.dietary_keywords = {
            'vegan': ['vegan', 'plant-based', 'plant based'],
            'vegetarian': ['vegetarian', 'veggie'],
            'gluten-free': ['gluten-free', 'gluten free', 'gf'],
            'dairy-free': ['dairy-free', 'dairy free', 'lactose-free'],
            'nut-free': ['nut-free', 'nut free'],
            'halal': ['halal'],
            'kosher': ['kosher'],
            'spicy': ['spicy', 'hot', '🌶']
        }

        self.category_keywords = {
            'Appetizers': ['appetizer', 'starter', 'app', 'apps', 'small plate'],
            'Soups & Salads': ['soup', 'salad', 'bisque', 'chowder'],
            'Main Courses': ['main', 'entree', 'entrée', 'main course'],
            'Pasta': ['pasta', 'spaghetti', 'linguine', 'penne', 'ravioli'],
            'Seafood': ['seafood', 'fish', 'salmon', 'tuna', 'shrimp', 'lobster', 'crab'],
            'Meat': ['beef', 'steak', 'chicken', 'pork', 'lamb', 'duck'],
            'Pizza': ['pizza', 'flatbread'],
            'Burgers & Sandwiches': ['burger', 'sandwich', 'wrap', 'panini'],
            'Desserts': ['dessert', 'cake', 'ice cream', 'pie', 'pudding', 'tiramisu'],
            'Drinks': ['drink', 'beverage', 'cocktail', 'beer', 'wine', 'soda', 'juice', 'coffee', 'tea'],
            'Breakfast': ['breakfast', 'pancake', 'waffle', 'omelette', 'omelet', 'eggs'],
            'Sides': ['side', 'fries', 'rice', 'vegetables', 'mashed potato']
        }

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Read image
        img = cv2.imread(image_path)

        if img is None:
            raise ValueError(f"Could not read image from {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Dilation and erosion to remove noise
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        return processed

    def extract_text(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)

            # Perform OCR
            text = pytesseract.image_to_string(processed_img, config='--psm 6')

            # Also try with original image
            original_text = pytesseract.image_to_string(Image.open(image_path), config='--psm 6')

            # Use whichever gives more text
            if len(original_text) > len(text):
                text = original_text

            return text

        except Exception as e:
            print(f"OCR error: {str(e)}")
            # Fallback to original image
            try:
                return pytesseract.image_to_string(Image.open(image_path))
            except:
                return ""

    def parse_price(self, text: str) -> str:
        """Extract price from text"""
        # Look for common price patterns
        price_patterns = [
            r'[$£€¥][\d,]+\.?\d*',  # $12.99, £10, €15.50
            r'[\d,]+\.?\d*\s*[$£€¥]',  # 12.99$, 10£
            r'\d+\.\d{2}',  # 12.99
            r'\d+,\d{2}',  # 12,99 (European format)
        ]

        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()

        return ""

    def detect_dietary_tags(self, text: str) -> List[str]:
        """Detect dietary tags in text"""
        tags = []
        text_lower = text.lower()

        for tag, keywords in self.dietary_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    tags.append(tag)
                    break

        return list(set(tags))

    def categorize_item(self, name: str, description: str) -> str:
        """Categorize a menu item"""
        combined_text = (name + ' ' + description).lower()

        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return category

        return 'Other'

    def parse_menu_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse raw text into structured menu items"""
        items = []

        # Split text into lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        current_item = None
        current_category = 'Other'

        for i, line in enumerate(lines):
            # Skip very short lines (likely noise)
            if len(line) < 3:
                continue

            # Check if line is a category header (usually all caps or has specific keywords)
            is_category = False
            for category, keywords in self.category_keywords.items():
                if any(keyword in line.lower() for keyword in keywords) and len(line) < 50:
                    # Check if it's a standalone category line
                    if line.isupper() or len(line.split()) <= 3:
                        current_category = category
                        is_category = True
                        break

            if is_category:
                continue

            # Try to identify menu items
            # Items typically have: name, possibly description, price

            # Check if line contains a price
            price = self.parse_price(line)

            # If we have a price, this is likely an item or end of item description
            if price:
                # Remove price from line to get name/description
                name_desc = re.sub(r'[$£€¥][\d,]+\.?\d*', '', line).strip()
                name_desc = re.sub(r'[\d,]+\.?\d*\s*[$£€¥]', '', name_desc).strip()
                name_desc = re.sub(r'\d+\.\d{2}', '', name_desc).strip()

                # Split name and description (description usually comes after ... or -)
                if '...' in name_desc:
                    parts = name_desc.split('...')
                    name = parts[0].strip()
                    description = parts[1].strip() if len(parts) > 1 else ''
                elif ' - ' in name_desc:
                    parts = name_desc.split(' - ', 1)
                    name = parts[0].strip()
                    description = parts[1].strip() if len(parts) > 1 else ''
                else:
                    # If no clear separator, first part is name
                    words = name_desc.split()
                    if len(words) > 5:
                        name = ' '.join(words[:3])
                        description = ' '.join(words[3:])
                    else:
                        name = name_desc
                        description = ''

                if name:
                    # Detect dietary tags
                    dietary_tags = self.detect_dietary_tags(line)

                    # Determine category
                    category = self.categorize_item(name, description)
                    if category == 'Other':
                        category = current_category

                    items.append({
                        'name': name,
                        'description': description,
                        'price': price,
                        'category': category,
                        'dietary_tags': dietary_tags
                    })

            # If no price but might be a dish name (starts with capital, reasonable length)
            elif len(line) < 100 and line[0].isupper() and not line.isupper():
                # This might be an item name, look ahead for description/price
                potential_name = line

                # Look at next line for description or price
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    next_price = self.parse_price(next_line)

                    if next_price:
                        # Next line has price, might have description too
                        description = re.sub(r'[$£€¥][\d,]+\.?\d*', '', next_line).strip()
                        description = re.sub(r'[\d,]+\.?\d*\s*[$£€¥]', '', description).strip()

                        dietary_tags = self.detect_dietary_tags(potential_name + ' ' + description)
                        category = self.categorize_item(potential_name, description)
                        if category == 'Other':
                            category = current_category

                        items.append({
                            'name': potential_name,
                            'description': description,
                            'price': next_price,
                            'category': category,
                            'dietary_tags': dietary_tags
                        })

        return items

    def process_menu_image(self, image_path: str, restaurant_name: str = '') -> Dict[str, Any]:
        """Process a menu image and return structured data"""
        try:
            # Extract text using OCR
            raw_text = self.extract_text(image_path)

            if not raw_text or len(raw_text.strip()) < 10:
                return {
                    'success': False,
                    'error': 'Could not extract text from image. Please ensure the image is clear and well-lit.'
                }

            # Parse text into structured menu items
            items = self.parse_menu_text(raw_text)

            # If no items found, create a simple structured version
            if not items:
                # Create basic items from lines with potential prices
                lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
                for line in lines:
                    price = self.parse_price(line)
                    if price and len(line) > 5:
                        name = re.sub(r'[$£€¥][\d,]+\.?\d*', '', line).strip()
                        name = re.sub(r'[\d,]+\.?\d*\s*[$£€¥]', '', name).strip()
                        if name:
                            items.append({
                                'name': name,
                                'description': '',
                                'price': price,
                                'category': 'Other',
                                'dietary_tags': []
                            })

            # Get all categories
            categories = list(set(item['category'] for item in items))

            return {
                'success': True,
                'raw_text': raw_text,
                'menu_data': {
                    'restaurant_name': restaurant_name,
                    'items': items,
                    'categories': categories,
                    'total_items': len(items)
                }
            }

        except Exception as e:
            print(f"Error processing menu: {str(e)}")
            return {
                'success': False,
                'error': f'Error processing menu: {str(e)}'
            }
