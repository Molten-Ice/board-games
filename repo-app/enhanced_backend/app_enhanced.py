"""
Main Flask application for Restaurant Recommender System
Includes JWT authentication, user management, and recommendations
"""
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
import base64
import re

# Import models and utilities
import sys
# Add parent directory to import from backend folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models import (
    db, User, Restaurant, Menu, MenuItem, Cuisine, DietaryPreference,
    Rating, RestaurantVisit, Favorite
)
from recommender import RestaurantRecommender
from scraper import ReadingRestaurantScraper

# Import menu processor from original backend
from backend.menu_processor import MenuProcessor

# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def validate_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_password_strength(password):
    """
    Validate password strength
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, None

def validate_username(username):
    """Validate username format"""
    if len(username) < 3 or len(username) > 50:
        return False, "Username must be between 3 and 50 characters"
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    return True, None

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    # Use werkzeug's secure_filename and add timestamp
    base = secure_filename(filename)
    name, ext = os.path.splitext(base)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{timestamp}_{name}{ext}"

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///restaurant_recommender.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Security headers
app.config['JWT_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['JWT_COOKIE_CSRF_PROTECT'] = True

# Initialize extensions
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
jwt = JWTManager(app)
db.init_app(app)

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize utilities
recommender = RestaurantRecommender()
scraper = ReadingRestaurantScraper()
menu_processor = MenuProcessor()

# Token blocklist for logout (in production, use Redis)
token_blocklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if token has been revoked"""
    jti = jwt_payload['jti']
    return jti in token_blocklist

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'username', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Validate email format
        email = data['email'].strip().lower()
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Validate username
        username = data['username'].strip()
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 400

        # Validate password strength
        password = data['password']
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        # Create new user
        user = User(
            email=email,
            username=username,
            display_name=data.get('display_name', username)
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()

        email_or_username = data.get('email', '').strip()
        password = data.get('password', '')

        if not email_or_username or not password:
            return jsonify({'error': 'Email/username and password required'}), 400

        # Find user by email or username
        user = User.query.filter(
            (User.email == email_or_username.lower()) |
            (User.username == email_or_username)
        ).first()

        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': access_token}), 200

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user and revoke token"""
    jti = get_jwt()['jti']
    token_blocklist.add(jti)
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': user.to_dict(include_private=True)}), 200

    except Exception as e:
        print(f"Get user error: {str(e)}")
        return jsonify({'error': 'Failed to get user'}), 500

# ============================================================================
# USER PROFILE & PREFERENCES
# ============================================================================

@app.route('/api/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Update allowed fields
        if 'display_name' in data:
            user.display_name = data['display_name']
        if 'location' in data:
            user.location = data['location']

        db.session.commit()

        return jsonify({
            'message': 'Profile updated',
            'user': user.to_dict(include_private=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Profile update error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500

@app.route('/api/user/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """Update user preferences"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Update preference fields
        if 'price_preference' in data:
            user.price_preference = data['price_preference']
        if 'preferred_distance_km' in data:
            user.preferred_distance_km = float(data['preferred_distance_km'])
        if 'preferred_ambiance' in data:
            user.preferred_ambiance = data['preferred_ambiance']
        if 'spice_tolerance' in data:
            user.spice_tolerance = int(data['spice_tolerance'])
        if 'adventurousness' in data:
            user.adventurousness = int(data['adventurousness'])
        if 'health_consciousness' in data:
            user.health_consciousness = int(data['health_consciousness'])

        # Update cuisines
        if 'cuisine_ids' in data:
            user.favorite_cuisines = Cuisine.query.filter(
                Cuisine.id.in_(data['cuisine_ids'])
            ).all()

        # Update dietary preferences
        if 'dietary_ids' in data:
            user.dietary_preferences = DietaryPreference.query.filter(
                DietaryPreference.id.in_(data['dietary_ids'])
            ).all()

        # Mark onboarding as complete
        if 'onboarding_completed' in data:
            user.onboarding_completed = bool(data['onboarding_completed'])

        db.session.commit()

        return jsonify({
            'message': 'Preferences updated',
            'user': user.to_dict(include_private=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Preferences update error: {str(e)}")
        return jsonify({'error': 'Failed to update preferences'}), 500

# ============================================================================
# RESTAURANT ENDPOINTS
# ============================================================================

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    """Get all restaurants with optional filters"""
    try:
        # Get query parameters
        cuisine = request.args.get('cuisine')
        price_range = request.args.get('price_range')
        area = request.args.get('area')
        search = request.args.get('search')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        # Build query
        query = Restaurant.query.filter_by(is_active=True)

        if cuisine:
            query = query.join(Restaurant.cuisines).filter(Cuisine.name == cuisine)

        if price_range:
            query = query.filter_by(price_range=price_range)

        if area:
            query = query.filter_by(area=area)

        if search:
            search_term = f'%{search}%'
            query = query.filter(
                (Restaurant.name.ilike(search_term)) |
                (Restaurant.description.ilike(search_term))
            )

        # Get total count
        total = query.count()

        # Get paginated results
        restaurants = query.order_by(
            Restaurant.average_rating.desc()
        ).limit(limit).offset(offset).all()

        return jsonify({
            'restaurants': [r.to_dict() for r in restaurants],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        print(f"Get restaurants error: {str(e)}")
        return jsonify({'error': 'Failed to get restaurants'}), 500

@app.route('/api/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    """Get restaurant details"""
    try:
        restaurant = Restaurant.query.get(restaurant_id)

        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404

        return jsonify({
            'restaurant': restaurant.to_dict(include_menu=True)
        }), 200

    except Exception as e:
        print(f"Get restaurant error: {str(e)}")
        return jsonify({'error': 'Failed to get restaurant'}), 500

@app.route('/api/restaurants/<int:restaurant_id>/menu', methods=['GET'])
def get_restaurant_menu(restaurant_id):
    """Get restaurant menu with items"""
    try:
        restaurant = Restaurant.query.get(restaurant_id)

        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404

        # Get current menu
        menu = restaurant.menus.filter_by(is_current=True).first()

        if not menu:
            return jsonify({'error': 'No menu available'}), 404

        # Get menu items
        items = menu.items.all()

        return jsonify({
            'menu': menu.to_dict(),
            'items': [item.to_dict() for item in items]
        }), 200

    except Exception as e:
        print(f"Get menu error: {str(e)}")
        return jsonify({'error': 'Failed to get menu'}), 500

# ============================================================================
# RECOMMENDATION ENDPOINTS
# ============================================================================

@app.route('/api/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get personalized restaurant recommendations"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        limit = int(request.args.get('limit', 20))
        exclude_visited = request.args.get('exclude_visited', 'false').lower() == 'true'

        # Get recommendations
        recommendations = recommender.get_recommendations(
            user,
            limit=limit,
            exclude_visited=exclude_visited
        )

        # Format results
        results = []
        for restaurant, score in recommendations:
            data = restaurant.to_dict()
            data['recommendation_score'] = round(score, 3)
            results.append(data)

        return jsonify({
            'recommendations': results,
            'personalized': user.onboarding_completed
        }), 200

    except Exception as e:
        print(f"Recommendations error: {str(e)}")
        return jsonify({'error': 'Failed to get recommendations'}), 500

@app.route('/api/restaurants/<int:restaurant_id>/similar', methods=['GET'])
def get_similar_restaurants(restaurant_id):
    """Get restaurants similar to the given one"""
    try:
        restaurant = Restaurant.query.get(restaurant_id)

        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404

        limit = int(request.args.get('limit', 5))

        # Get similar restaurants
        similar = recommender.get_similar_restaurants(restaurant, limit=limit)

        results = []
        for sim_restaurant, score in similar:
            data = sim_restaurant.to_dict()
            data['similarity_score'] = round(score, 3)
            results.append(data)

        return jsonify({'similar_restaurants': results}), 200

    except Exception as e:
        print(f"Similar restaurants error: {str(e)}")
        return jsonify({'error': 'Failed to get similar restaurants'}), 500

# ============================================================================
# RATING & FEEDBACK ENDPOINTS
# ============================================================================

@app.route('/api/restaurants/<int:restaurant_id>/rate', methods=['POST'])
@jwt_required()
def rate_restaurant(restaurant_id):
    """Rate a restaurant"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not user or not restaurant:
            return jsonify({'error': 'User or restaurant not found'}), 404

        data = request.get_json()

        # Validate rating value
        try:
            rating_value = float(data.get('rating', 0))
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid rating value'}), 400

        if rating_value < 1 or rating_value > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400

        # Validate optional sub-ratings
        for field in ['food_rating', 'service_rating', 'ambiance_rating', 'value_rating']:
            if field in data and data[field] is not None:
                try:
                    val = float(data[field])
                    if val < 1 or val > 5:
                        return jsonify({'error': f'{field} must be between 1 and 5'}), 400
                except (TypeError, ValueError):
                    return jsonify({'error': f'Invalid {field} value'}), 400

        # Validate review text length
        review_text = data.get('review_text', '')
        if review_text and len(review_text) > 2000:
            return jsonify({'error': 'Review text must be less than 2000 characters'}), 400

        # Check if user already rated
        existing_rating = Rating.query.filter_by(
            user_id=user.id,
            restaurant_id=restaurant.id
        ).first()

        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating_value
            existing_rating.review_text = data.get('review_text')
            existing_rating.food_rating = data.get('food_rating')
            existing_rating.service_rating = data.get('service_rating')
            existing_rating.ambiance_rating = data.get('ambiance_rating')
            existing_rating.value_rating = data.get('value_rating')
            existing_rating.updated_at = datetime.utcnow()
        else:
            # Create new rating
            rating = Rating(
                user_id=user.id,
                restaurant_id=restaurant.id,
                rating=rating_value,
                review_text=data.get('review_text'),
                food_rating=data.get('food_rating'),
                service_rating=data.get('service_rating'),
                ambiance_rating=data.get('ambiance_rating'),
                value_rating=data.get('value_rating')
            )
            db.session.add(rating)

        # Update restaurant average rating
        restaurant.calculate_average_rating()

        db.session.commit()

        return jsonify({
            'message': 'Rating saved',
            'rating': existing_rating.to_dict() if existing_rating else rating.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Rating error: {str(e)}")
        return jsonify({'error': 'Failed to save rating'}), 500

@app.route('/api/restaurants/<int:restaurant_id>/favorite', methods=['POST'])
@jwt_required()
def toggle_favorite(restaurant_id):
    """Toggle favorite status for a restaurant"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not user or not restaurant:
            return jsonify({'error': 'User or restaurant not found'}), 404

        # Check if already favorited
        favorite = Favorite.query.filter_by(
            user_id=user.id,
            restaurant_id=restaurant.id
        ).first()

        if favorite:
            # Remove favorite
            db.session.delete(favorite)
            is_favorite = False
        else:
            # Add favorite
            favorite = Favorite(user_id=user.id, restaurant_id=restaurant.id)
            db.session.add(favorite)
            is_favorite = True

        db.session.commit()

        return jsonify({
            'is_favorite': is_favorite,
            'message': 'Favorite updated'
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Favorite error: {str(e)}")
        return jsonify({'error': 'Failed to update favorite'}), 500

@app.route('/api/user/favorites', methods=['GET'])
@jwt_required()
def get_user_favorites():
    """Get user's favorite restaurants"""
    try:
        current_user_id = get_jwt_identity()
        favorites = Favorite.query.filter_by(user_id=current_user_id).all()

        restaurant_ids = [f.restaurant_id for f in favorites]
        restaurants = Restaurant.query.filter(Restaurant.id.in_(restaurant_ids)).all()

        return jsonify({
            'favorites': [r.to_dict() for r in restaurants]
        }), 200

    except Exception as e:
        print(f"Get favorites error: {str(e)}")
        return jsonify({'error': 'Failed to get favorites'}), 500

@app.route('/api/restaurants/<int:restaurant_id>/visit', methods=['POST'])
@jwt_required()
def mark_restaurant_visited(restaurant_id):
    """Mark a restaurant as visited"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not user or not restaurant:
            return jsonify({'error': 'User or restaurant not found'}), 404

        # Check if already visited
        visit = RestaurantVisit.query.filter_by(
            user_id=user.id,
            restaurant_id=restaurant.id
        ).first()

        if not visit:
            # Add visit
            visit = RestaurantVisit(user_id=user.id, restaurant_id=restaurant.id)
            db.session.add(visit)
            db.session.commit()

        return jsonify({
            'has_visited': True,
            'message': 'Restaurant marked as visited'
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Visit error: {str(e)}")
        return jsonify({'error': 'Failed to mark as visited'}), 500

# ============================================================================
# CUISINE & DIETARY ENDPOINTS
# ============================================================================

@app.route('/api/cuisines', methods=['GET'])
def get_cuisines():
    """Get all available cuisines"""
    try:
        cuisines = Cuisine.query.order_by(Cuisine.name).all()
        return jsonify({
            'cuisines': [c.to_dict() for c in cuisines]
        }), 200
    except Exception as e:
        print(f"Get cuisines error: {str(e)}")
        return jsonify({'error': 'Failed to get cuisines'}), 500

@app.route('/api/dietary-preferences', methods=['GET'])
def get_dietary_preferences():
    """Get all dietary preferences"""
    try:
        dietary = DietaryPreference.query.order_by(DietaryPreference.name).all()
        return jsonify({
            'dietary_preferences': [d.to_dict() for d in dietary]
        }), 200
    except Exception as e:
        print(f"Get dietary preferences error: {str(e)}")
        return jsonify({'error': 'Failed to get dietary preferences'}), 500

# ============================================================================
# MENU PROCESSING ENDPOINTS (from original app)
# ============================================================================

@app.route('/api/menu/upload', methods=['POST'])
@jwt_required()
def upload_menu():
    """Upload and process a menu image"""
    try:
        current_user_id = get_jwt_identity()
        filepath = None
        restaurant_id = None

        # Check if it's a file upload (multipart/form-data)
        if request.files and 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            # Validate file type
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type. Only images are allowed (png, jpg, jpeg, gif, webp)'}), 400

            # Sanitize and save file
            filename = sanitize_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Get restaurant ID from form
            restaurant_id = request.form.get('restaurant_id')

        # Check if it's base64 image data (JSON)
        elif request.is_json and request.json and 'imageData' in request.json:
            image_data = request.json['imageData']

            # Remove data URL prefix if present
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]

            # Decode and save
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_menu.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(image_data))

            # Get restaurant ID from JSON
            restaurant_id = request.json.get('restaurant_id')

        else:
            return jsonify({'error': 'No image provided'}), 400

        if not filepath:
            return jsonify({'error': 'Failed to save image'}), 500

        # Get restaurant
        restaurant = None
        if restaurant_id:
            restaurant = Restaurant.query.get(int(restaurant_id))

        # Process the menu image
        result = menu_processor.process_menu_image(
            filepath,
            restaurant.name if restaurant else 'User Upload'
        )

        if not result['success']:
            return jsonify({'error': result.get('error', 'Processing failed')}), 500

        # Save to database
        menu = Menu(
            restaurant_id=restaurant.id if restaurant else None,
            image_path=filepath,
            raw_text=result.get('raw_text', ''),
            processed_data=json.dumps(result['menu_data']),
            source='user_upload',
            is_current=True
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

        return jsonify({
            'success': True,
            'menu_id': menu.id,
            'menu_data': result['menu_data']
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Menu upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    try:
        stats = {
            'total_restaurants': Restaurant.query.filter_by(is_active=True).count(),
            'total_users': User.query.count(),
            'total_ratings': Rating.query.count(),
            'total_menus': Menu.query.count(),
            'cuisines': Cuisine.query.count(),
            'areas': ['Oracle', 'Riverside', 'Town Centre']
        }
        return jsonify(stats), 200
    except Exception as e:
        print(f"Stats error: {str(e)}")
        return jsonify({'error': 'Failed to get stats'}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database initialized")

    app.run(debug=True, host='0.0.0.0', port=5001)
