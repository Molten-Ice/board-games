"""
Enhanced database models for restaurant recommender system
Includes user management, restaurants, preferences, and recommendations
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

# Association table for user favorite cuisines
user_cuisines = db.Table('user_cuisines',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('cuisine_id', db.Integer, db.ForeignKey('cuisines.id'), primary_key=True)
)

# Association table for user dietary preferences
user_dietary = db.Table('user_dietary',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('dietary_id', db.Integer, db.ForeignKey('dietary_preferences.id'), primary_key=True)
)

# Association table for restaurant cuisines
restaurant_cuisines = db.Table('restaurant_cuisines',
    db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurants.id'), primary_key=True),
    db.Column('cuisine_id', db.Integer, db.ForeignKey('cuisines.id'), primary_key=True)
)

class User(db.Model):
    """User model with preferences and personalization data"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Profile
    display_name = db.Column(db.String(100))
    location = db.Column(db.String(200))  # User's location for proximity recommendations

    # Preferences
    price_preference = db.Column(db.String(20))  # budget, moderate, expensive, luxury
    preferred_distance_km = db.Column(db.Float, default=5.0)
    preferred_ambiance = db.Column(db.String(100))  # casual, fine_dining, romantic, family_friendly

    # Personalization settings
    spice_tolerance = db.Column(db.Integer, default=3)  # 1-5 scale
    adventurousness = db.Column(db.Integer, default=3)  # 1-5 scale (comfort food vs exotic)
    health_consciousness = db.Column(db.Integer, default=3)  # 1-5 scale

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    onboarding_completed = db.Column(db.Boolean, default=False)

    # Relationships
    favorite_cuisines = db.relationship('Cuisine', secondary=user_cuisines, backref='users')
    dietary_preferences = db.relationship('DietaryPreference', secondary=user_dietary, backref='users')
    ratings = db.relationship('Rating', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    visits = db.relationship('RestaurantVisit', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_private=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name or self.username,
            'location': self.location,
            'onboarding_completed': self.onboarding_completed,
            'preferences': {
                'price': self.price_preference,
                'distance_km': self.preferred_distance_km,
                'ambiance': self.preferred_ambiance,
                'spice_tolerance': self.spice_tolerance,
                'adventurousness': self.adventurousness,
                'health_consciousness': self.health_consciousness,
                'cuisines': [c.name for c in self.favorite_cuisines],
                'dietary': [d.name for d in self.dietary_preferences]
            }
        }
        if include_private:
            data['email'] = self.email
        return data

class Restaurant(db.Model):
    """Restaurant model with detailed information"""
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)

    # Location
    address = db.Column(db.Text)
    postcode = db.Column(db.String(20), index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    area = db.Column(db.String(100))  # e.g., Oracle, Riverside

    # Details
    phone = db.Column(db.String(50))
    website = db.Column(db.String(500))
    description = db.Column(db.Text)

    # Attributes
    price_range = db.Column(db.String(20))  # budget, moderate, expensive, luxury
    ambiance = db.Column(db.String(100))  # casual, fine_dining, romantic, family_friendly
    average_rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)

    # Features
    has_outdoor_seating = db.Column(db.Boolean, default=False)
    has_parking = db.Column(db.Boolean, default=False)
    accepts_reservations = db.Column(db.Boolean, default=True)
    delivery_available = db.Column(db.Boolean, default=False)

    # Data source
    source = db.Column(db.String(100))  # scraped, manual, user_added
    source_url = db.Column(db.String(500))

    # Status
    is_active = db.Column(db.Boolean, default=True)
    verified = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cuisines = db.relationship('Cuisine', secondary=restaurant_cuisines, backref='restaurants')
    menus = db.relationship('Menu', backref='restaurant', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='restaurant', lazy='dynamic', cascade='all, delete-orphan')
    visits = db.relationship('RestaurantVisit', backref='restaurant', lazy='dynamic')

    def calculate_average_rating(self):
        """Recalculate average rating from all ratings"""
        ratings_list = list(self.ratings)
        if ratings_list:
            self.average_rating = sum(r.rating for r in ratings_list) / len(ratings_list)
            self.total_ratings = len(ratings_list)
        else:
            self.average_rating = 0.0
            self.total_ratings = 0

    def to_dict(self, include_menu=False):
        """Convert restaurant to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'postcode': self.postcode,
            'area': self.area,
            'phone': self.phone,
            'website': self.website,
            'description': self.description,
            'price_range': self.price_range,
            'ambiance': self.ambiance,
            'average_rating': round(self.average_rating, 1) if self.average_rating else 0.0,
            'total_ratings': self.total_ratings,
            'features': {
                'outdoor_seating': self.has_outdoor_seating,
                'parking': self.has_parking,
                'reservations': self.accepts_reservations,
                'delivery': self.delivery_available
            },
            'cuisines': [c.name for c in self.cuisines],
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude
            } if self.latitude and self.longitude else None
        }

        if include_menu:
            latest_menu = self.menus.order_by(Menu.created_at.desc()).first()
            if latest_menu:
                data['menu'] = latest_menu.to_dict()

        return data

class Menu(db.Model):
    """Menu model - links to restaurant and stores digitized menu data"""
    __tablename__ = 'menus'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    # Menu data
    menu_type = db.Column(db.String(50))  # main, lunch, dinner, drinks, dessert
    image_path = db.Column(db.String(512))
    raw_text = db.Column(db.Text)
    processed_data = db.Column(db.Text)  # JSON

    # Source
    source = db.Column(db.String(100))  # scraped, uploaded, photographed
    source_url = db.Column(db.String(500))

    # Status
    is_current = db.Column(db.Boolean, default=True)
    verified = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = db.relationship('MenuItem', backref='menu', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        """Convert menu to dictionary"""
        try:
            processed_data = json.loads(self.processed_data) if self.processed_data else {}
        except (json.JSONDecodeError, TypeError):
            processed_data = {}

        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'menu_type': self.menu_type,
            'is_current': self.is_current,
            'verified': self.verified,
            'processed_data': processed_data,
            'item_count': self.items.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MenuItem(db.Model):
    """Individual menu item"""
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)

    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.String(50))
    category = db.Column(db.String(100), index=True)

    # Dietary tags (JSON list)
    dietary_tags = db.Column(db.Text)

    # Metadata
    spice_level = db.Column(db.Integer)  # 1-5
    is_popular = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert menu item to dictionary"""
        try:
            dietary_tags = json.loads(self.dietary_tags) if self.dietary_tags else []
        except (json.JSONDecodeError, TypeError):
            dietary_tags = []

        return {
            'id': self.id,
            'menu_id': self.menu_id,
            'name': self.name,
            'description': self.description or '',
            'price': self.price or '',
            'category': self.category or 'Other',
            'dietary_tags': dietary_tags,
            'spice_level': self.spice_level,
            'is_popular': self.is_popular
        }

class Cuisine(db.Model):
    """Cuisine types"""
    __tablename__ = 'cuisines'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class DietaryPreference(db.Model):
    """Dietary preferences (vegan, gluten-free, etc.)"""
    __tablename__ = 'dietary_preferences'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class Rating(db.Model):
    """User ratings for restaurants"""
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    rating = db.Column(db.Float, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text)

    # Detailed ratings
    food_rating = db.Column(db.Float)
    service_rating = db.Column(db.Float)
    ambiance_rating = db.Column(db.Float)
    value_rating = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: one rating per user per restaurant
    __table_args__ = (db.UniqueConstraint('user_id', 'restaurant_id', name='unique_user_restaurant_rating'),)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'restaurant_id': self.restaurant_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'detailed_ratings': {
                'food': self.food_rating,
                'service': self.service_rating,
                'ambiance': self.ambiance_rating,
                'value': self.value_rating
            },
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class RestaurantVisit(db.Model):
    """Track user visits to restaurants for recommendations"""
    __tablename__ = 'restaurant_visits'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    enjoyed = db.Column(db.Boolean)  # True/False/None for implicit feedback

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Favorite(db.Model):
    """User favorite restaurants"""
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'restaurant_id', name='unique_user_restaurant_favorite'),)
