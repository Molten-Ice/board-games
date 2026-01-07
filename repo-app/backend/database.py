from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Menu(db.Model):
    """Menu model to store scanned menus"""
    __tablename__ = 'menus'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_name = db.Column(db.String(255), nullable=False)
    image_path = db.Column(db.String(512), nullable=False)
    raw_text = db.Column(db.Text)
    processed_data = db.Column(db.Text)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    items = db.relationship('MenuItem', backref='menu', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """Convert menu to dictionary"""
        return {
            'id': self.id,
            'restaurant_name': self.restaurant_name,
            'image_path': self.image_path,
            'raw_text': self.raw_text,
            'processed_data': json.loads(self.processed_data) if self.processed_data else {},
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'item_count': len(self.items)
        }

class MenuItem(db.Model):
    """MenuItem model to store individual menu items"""
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.String(50))
    category = db.Column(db.String(100))
    dietary_tags = db.Column(db.Text)  # JSON string of tags
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert menu item to dictionary"""
        return {
            'id': self.id,
            'menu_id': self.menu_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'dietary_tags': json.loads(self.dietary_tags) if self.dietary_tags else [],
            'created_at': self.created_at.isoformat()
        }
