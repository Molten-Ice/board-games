from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
from datetime import datetime
import json
from menu_processor import MenuProcessor
from database import db, Menu, MenuItem
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///menus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
db.init_app(app)

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize menu processor
menu_processor = MenuProcessor()

with app.app_context():
    db.create_all()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/process-menu', methods=['POST'])
def process_menu():
    """Process a menu image and extract items"""
    try:
        filepath = None
        restaurant_name = 'Unknown Restaurant'

        # Check if it's a file upload (multipart/form-data)
        if request.files and 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            # Save file
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Get restaurant name from form
            restaurant_name = request.form.get('restaurantName', 'Unknown Restaurant')

        # Check if it's base64 image data (JSON)
        elif request.is_json and request.json and 'imageData' in request.json:
            image_data = request.json['imageData']

            # Remove data URL prefix if present
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]

            # Decode and save
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_camera.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(image_data))

            # Get restaurant name from JSON
            restaurant_name = request.json.get('restaurantName', 'Unknown Restaurant')

        else:
            return jsonify({'error': 'No image provided'}), 400

        if not filepath:
            return jsonify({'error': 'Failed to save image'}), 500

        # Process the menu image
        print(f"Processing menu image: {filepath} for restaurant: {restaurant_name}")
        result = menu_processor.process_menu_image(filepath, restaurant_name)

        if not result['success']:
            error_msg = result.get('error', 'Processing failed')
            print(f"Menu processing failed: {error_msg}")
            return jsonify({'error': error_msg}), 500

        print(f"Successfully extracted {len(result['menu_data'].get('items', []))} items from menu")

        # Save to database
        try:
            menu = Menu(
                restaurant_name=restaurant_name,
                image_path=filepath,
                raw_text=result.get('raw_text', ''),
                processed_data=json.dumps(result['menu_data'])
            )
            db.session.add(menu)
            db.session.flush()

            # Save menu items
            for item_data in result['menu_data'].get('items', []):
                menu_item = MenuItem(
                    menu_id=menu.id,
                    name=item_data['name'],
                    description=item_data.get('description', ''),
                    price=item_data.get('price', ''),
                    category=item_data.get('category', 'Other'),
                    dietary_tags=json.dumps(item_data.get('dietary_tags', []))
                )
                db.session.add(menu_item)

            db.session.commit()
            print(f"Successfully saved menu to database with ID: {menu.id}")

            # Return processed menu
            return jsonify({
                'success': True,
                'menu_id': menu.id,
                'menu_data': result['menu_data'],
                'raw_text': result.get('raw_text', '')
            })

        except Exception as db_error:
            db.session.rollback()
            print(f"Database error: {str(db_error)}")
            return jsonify({'error': f'Database error: {str(db_error)}'}), 500

    except Exception as e:
        print(f"Error processing menu: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/menus', methods=['GET'])
def get_menus():
    """Get all saved menus"""
    try:
        menus = Menu.query.order_by(Menu.created_at.desc()).all()
        return jsonify({
            'menus': [menu.to_dict() for menu in menus]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/menus/<int:menu_id>', methods=['GET'])
def get_menu(menu_id):
    """Get a specific menu with items"""
    try:
        menu = Menu.query.get_or_404(menu_id)
        items = MenuItem.query.filter_by(menu_id=menu_id).all()

        return jsonify({
            'menu': menu.to_dict(),
            'items': [item.to_dict() for item in items]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/menus/<int:menu_id>', methods=['DELETE'])
def delete_menu(menu_id):
    """Delete a menu"""
    try:
        menu = Menu.query.get_or_404(menu_id)

        # Delete associated items
        MenuItem.query.filter_by(menu_id=menu_id).delete()

        # Delete image file
        if os.path.exists(menu.image_path):
            os.remove(menu.image_path)

        db.session.delete(menu)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/menus/<int:menu_id>/favorite', methods=['POST'])
def toggle_favorite(menu_id):
    """Toggle favorite status of a menu"""
    try:
        menu = Menu.query.get_or_404(menu_id)
        menu.is_favorite = not menu.is_favorite
        db.session.commit()

        return jsonify({
            'success': True,
            'is_favorite': menu.is_favorite
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_menus():
    """Search menu items"""
    try:
        query = request.args.get('q', '').lower()
        category = request.args.get('category', '')
        dietary = request.args.get('dietary', '')

        # Build query
        items_query = MenuItem.query

        if query:
            items_query = items_query.filter(
                (MenuItem.name.ilike(f'%{query}%')) |
                (MenuItem.description.ilike(f'%{query}%'))
            )

        if category:
            items_query = items_query.filter_by(category=category)

        if dietary:
            items_query = items_query.filter(MenuItem.dietary_tags.like(f'%{dietary}%'))

        items = items_query.all()

        return jsonify({
            'items': [item.to_dict() for item in items]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all available categories"""
    try:
        categories = db.session.query(MenuItem.category).distinct().all()
        return jsonify({
            'categories': [cat[0] for cat in categories if cat[0]]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
