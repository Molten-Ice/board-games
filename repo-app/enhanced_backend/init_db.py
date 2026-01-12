"""
Database initialization and seeding script
Populates database with cuisines, dietary preferences, and Reading restaurants
"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(__file__))

from app_enhanced import app, db
from models import Restaurant, Cuisine, DietaryPreference, Menu, MenuItem
from scraper import ReadingRestaurantScraper
import json

def init_database():
    """Initialize database with all tables"""
    print("Creating database tables...")
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")

def seed_cuisines():
    """Seed cuisine types"""
    print("\nSeeding cuisines...")

    cuisines_data = [
        {'name': 'British', 'description': 'Traditional British cuisine'},
        {'name': 'Italian', 'description': 'Italian cuisine including pizza and pasta'},
        {'name': 'Chinese', 'description': 'Chinese cuisine'},
        {'name': 'Indian', 'description': 'Indian and South Asian cuisine'},
        {'name': 'Japanese', 'description': 'Japanese cuisine including sushi'},
        {'name': 'Thai', 'description': 'Thai cuisine'},
        {'name': 'Vietnamese', 'description': 'Vietnamese cuisine'},
        {'name': 'French', 'description': 'French cuisine'},
        {'name': 'Spanish', 'description': 'Spanish and tapas'},
        {'name': 'Mexican', 'description': 'Mexican cuisine'},
        {'name': 'American', 'description': 'American cuisine'},
        {'name': 'Greek', 'description': 'Greek and Mediterranean'},
        {'name': 'Turkish', 'description': 'Turkish cuisine'},
        {'name': 'Korean', 'description': 'Korean cuisine'},
        {'name': 'Caribbean', 'description': 'Caribbean and Jamaican'},
        {'name': 'Portuguese', 'description': 'Portuguese cuisine'},
        {'name': 'Latin American', 'description': 'Latin American cuisine'},
        {'name': 'European', 'description': 'General European cuisine'},
        {'name': 'Asian', 'description': 'Pan-Asian cuisine'},
        {'name': 'African', 'description': 'African cuisine'},
        {'name': 'Middle Eastern', 'description': 'Middle Eastern cuisine'},
        {'name': 'Steakhouse', 'description': 'Steakhouse and grills'},
        {'name': 'Pizza', 'description': 'Pizza restaurants'},
        {'name': 'Burgers', 'description': 'Burger restaurants'},
        {'name': 'Breakfast', 'description': 'Breakfast and brunch'}
    ]

    with app.app_context():
        for cuisine_data in cuisines_data:
            existing = Cuisine.query.filter_by(name=cuisine_data['name']).first()
            if not existing:
                cuisine = Cuisine(**cuisine_data)
                db.session.add(cuisine)

        db.session.commit()
        print(f"✅ Seeded {len(cuisines_data)} cuisines")

def seed_dietary_preferences():
    """Seed dietary preferences"""
    print("\nSeeding dietary preferences...")

    dietary_data = [
        {'name': 'vegan', 'description': 'No animal products'},
        {'name': 'vegetarian', 'description': 'No meat or fish'},
        {'name': 'gluten-free', 'description': 'No gluten'},
        {'name': 'dairy-free', 'description': 'No dairy products'},
        {'name': 'nut-free', 'description': 'No nuts'},
        {'name': 'halal', 'description': 'Halal certified'},
        {'name': 'kosher', 'description': 'Kosher certified'},
        {'name': 'pescatarian', 'description': 'Fish but no meat'},
        {'name': 'low-carb', 'description': 'Low carbohydrate'},
        {'name': 'keto', 'description': 'Ketogenic diet'},
        {'name': 'paleo', 'description': 'Paleolithic diet'}
    ]

    with app.app_context():
        for dietary_item in dietary_data:
            existing = DietaryPreference.query.filter_by(name=dietary_item['name']).first()
            if not existing:
                dietary = DietaryPreference(**dietary_item)
                db.session.add(dietary)

        db.session.commit()
        print(f"✅ Seeded {len(dietary_data)} dietary preferences")

def seed_restaurants():
    """Seed Reading restaurants"""
    print("\nSeeding Reading restaurants...")

    scraper = ReadingRestaurantScraper()
    restaurants_data = scraper.get_oracle_riverside_restaurants()

    with app.app_context():
        added_count = 0

        for rest_data in restaurants_data:
            # Check if restaurant already exists
            existing = Restaurant.query.filter_by(name=rest_data['name']).first()

            if not existing:
                # Get cuisine objects
                cuisine_names = rest_data.pop('cuisines', [])
                cuisines = Cuisine.query.filter(Cuisine.name.in_(cuisine_names)).all()

                # Create restaurant
                restaurant = Restaurant(**rest_data)
                restaurant.cuisines = cuisines
                restaurant.verified = True
                restaurant.source = 'curated'

                db.session.add(restaurant)
                added_count += 1

        db.session.commit()
        print(f"✅ Seeded {added_count} restaurants")

def seed_sample_menus():
    """Seed sample menus for restaurants"""
    print("\nSeeding sample menus...")

    scraper = ReadingRestaurantScraper()
    sample_menus = scraper.get_sample_menus()

    with app.app_context():
        added_count = 0

        for restaurant_name, menu_items in sample_menus.items():
            restaurant = Restaurant.query.filter_by(name=restaurant_name).first()

            if restaurant and not restaurant.menus.filter_by(is_current=True).first():
                # Create menu
                menu = Menu(
                    restaurant_id=restaurant.id,
                    menu_type='main',
                    source='curated',
                    is_current=True,
                    verified=True,
                    processed_data=json.dumps({
                        'items': menu_items,
                        'total_items': len(menu_items)
                    })
                )
                db.session.add(menu)
                db.session.flush()

                # Add menu items
                for item_data in menu_items:
                    # Extract dietary tags from description
                    dietary_tags = []
                    description = item_data.get('description', '').lower()

                    if '(v)' in description or '(vg)' in description or 'vegan' in description:
                        dietary_tags.append('vegan' if '(vg)' in description else 'vegetarian')
                    if '(spicy)' in description or 'spicy' in description:
                        dietary_tags.append('spicy')

                    menu_item = MenuItem(
                        menu_id=menu.id,
                        name=item_data['name'],
                        description=item_data['description'],
                        price=item_data['price'],
                        category=item_data['category'],
                        dietary_tags=json.dumps(dietary_tags)
                    )
                    db.session.add(menu_item)

                added_count += 1

        db.session.commit()
        print(f"✅ Seeded {added_count} sample menus")

def main():
    """Main initialization function"""
    print("=" * 60)
    print("Restaurant Recommender - Database Initialization")
    print("=" * 60)

    try:
        # Initialize database
        init_database()

        # Seed data
        seed_cuisines()
        seed_dietary_preferences()
        seed_restaurants()
        seed_sample_menus()

        print("\n" + "=" * 60)
        print("✅ Database initialization complete!")
        print("=" * 60)

        # Print summary
        with app.app_context():
            print(f"\nSummary:")
            print(f"  Restaurants: {Restaurant.query.count()}")
            print(f"  Cuisines: {Cuisine.query.count()}")
            print(f"  Dietary Preferences: {DietaryPreference.query.count()}")
            print(f"  Menus: {Menu.query.count()}")
            print(f"  Menu Items: {MenuItem.query.count()}")

    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
