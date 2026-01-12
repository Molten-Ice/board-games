"""
Web scraper for Reading, UK restaurants (Oracle/Riverside area)
Extracts restaurant information, menus, and details
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReadingRestaurantScraper:
    """
    Scraper for Reading, UK restaurants in Oracle and Riverside areas
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Oracle and Riverside restaurant data (manually curated for production)
        # In production, these would be scraped from various sources
        self.oracle_riverside_restaurants = [
            {
                'name': 'Bill\'s Reading',
                'address': 'The Oracle, Riverside, Reading RG1 2AG',
                'postcode': 'RG1 2AG',
                'area': 'Oracle',
                'phone': '01189 596950',
                'website': 'https://bills-website.co.uk/restaurants/reading',
                'description': 'Fresh, seasonal British food in a relaxed setting',
                'cuisines': ['British', 'Breakfast'],
                'price_range': 'moderate',
                'ambiance': 'casual',
                'has_outdoor_seating': True,
                'has_parking': True,
                'accepts_reservations': True,
                'latitude': 51.4552,
                'longitude': -0.9736
            },
            {
                'name': 'Côte Brasserie Reading',
                'address': '14-15 The Oracle, Reading RG1 2AG',
                'postcode': 'RG1 2AG',
                'area': 'Oracle',
                'phone': '01189 507230',
                'website': 'https://www.cote.co.uk',
                'description': 'French brasserie serving classic dishes',
                'cuisines': ['French', 'European'],
                'price_range': 'moderate',
                'ambiance': 'casual',
                'has_outdoor_seating': True,
                'has_parking': True,
                'accepts_reservations': True,
                'latitude': 51.4548,
                'longitude': -0.9734
            },
            {
                'name': 'Nando\'s Reading Oracle',
                'address': 'Unit 8, The Oracle, Reading RG1 2AG',
                'postcode': 'RG1 2AG',
                'area': 'Oracle',
                'phone': '01189 589935',
                'website': 'https://www.nandos.co.uk',
                'description': 'Flame-grilled PERi-PERi chicken in a lively atmosphere',
                'cuisines': ['Portuguese', 'African'],
                'price_range': 'budget',
                'ambiance': 'casual',
                'has_outdoor_seating': False,
                'has_parking': True,
                'accepts_reservations': False,
                'latitude': 51.4550,
                'longitude': -0.9735
            },
            {
                'name': 'Wagamama Reading',
                'address': 'The Oracle Shopping Centre, Reading RG1 2AG',
                'postcode': 'RG1 2AG',
                'area': 'Oracle',
                'phone': '01189 589720',
                'website': 'https://www.wagamama.com',
                'description': 'Pan-Asian cuisine served in a modern, canteen-style setting',
                'cuisines': ['Asian', 'Japanese', 'Thai'],
                'price_range': 'moderate',
                'ambiance': 'casual',
                'has_outdoor_seating': False,
                'has_parking': True,
                'accepts_reservations': False,
                'latitude': 51.4551,
                'longitude': -0.9737
            },
            {
                'name': 'Turtle Bay Reading',
                'address': '1 Riverside, Level, Reading RG1 8DH',
                'postcode': 'RG1 8DH',
                'area': 'Riverside',
                'phone': '01189 509090',
                'website': 'https://www.turtlebay.co.uk',
                'description': 'Caribbean food, cocktails and rum bar',
                'cuisines': ['Caribbean', 'Jamaican'],
                'price_range': 'moderate',
                'ambiance': 'casual',
                'has_outdoor_seating': True,
                'has_parking': False,
                'accepts_reservations': True,
                'delivery_available': True,
                'latitude': 51.4557,
                'longitude': -0.9745
            },
            {
                'name': 'Zizzi Reading',
                'address': 'The Oracle, Reading RG1 2AQ',
                'postcode': 'RG1 2AQ',
                'area': 'Oracle',
                'phone': '01189 502220',
                'website': 'https://www.zizzi.co.uk',
                'description': 'Italian chain restaurant offering pizza, pasta and more',
                'cuisines': ['Italian', 'Pizza'],
                'price_range': 'moderate',
                'ambiance': 'family_friendly',
                'has_outdoor_seating': True,
                'has_parking': True,
                'accepts_reservations': True,
                'delivery_available': True,
                'latitude': 51.4549,
                'longitude': -0.9733
            },
            {
                'name': 'Honest Burgers Reading',
                'address': 'The Oracle, Reading RG1 2AG',
                'postcode': 'RG1 2AG',
                'area': 'Oracle',
                'phone': '01189 502200',
                'website': 'https://www.honestburgers.co.uk',
                'description': 'British beef burgers, rosemary fries and craft beer',
                'cuisines': ['American', 'Burgers'],
                'price_range': 'moderate',
                'ambiance': 'casual',
                'has_outdoor_seating': False,
                'has_parking': True,
                'accepts_reservations': False,
                'latitude': 51.4552,
                'longitude': -0.9738
            },
            {
                'name': 'Coppa Club Reading',
                'address': 'Riverside, Reading RG1 2AH',
                'postcode': 'RG1 2AH',
                'area': 'Riverside',
                'phone': '01189 583900',
                'website': 'https://www.coppaclub.co.uk',
                'description': 'Contemporary British menu with riverside views',
                'cuisines': ['British', 'European'],
                'price_range': 'expensive',
                'ambiance': 'fine_dining',
                'has_outdoor_seating': True,
                'has_parking': False,
                'accepts_reservations': True,
                'latitude': 51.4560,
                'longitude': -0.9750
            },
            {
                'name': 'Las Iguanas Reading',
                'address': 'The Oracle, Reading RG1 2AG',
                'postcode': 'RG1 2AG',
                'area': 'Oracle',
                'phone': '01189 589945',
                'website': 'https://www.iguanas.co.uk',
                'description': 'Latin American food and cocktails',
                'cuisines': ['Latin American', 'Mexican'],
                'price_range': 'moderate',
                'ambiance': 'casual',
                'has_outdoor_seating': True,
                'has_parking': True,
                'accepts_reservations': True,
                'delivery_available': True,
                'latitude': 51.4553,
                'longitude': -0.9739
            },
            {
                'name': 'The Riverside Restaurant & Terrace',
                'address': 'Riverside, Reading RG1 2AH',
                'postcode': 'RG1 2AH',
                'area': 'Riverside',
                'phone': '01189 505050',
                'website': 'https://www.riverside-reading.co.uk',
                'description': 'Fine dining with stunning riverside views',
                'cuisines': ['British', 'European'],
                'price_range': 'expensive',
                'ambiance': 'fine_dining',
                'has_outdoor_seating': True,
                'has_parking': False,
                'accepts_reservations': True,
                'latitude': 51.4561,
                'longitude': -0.9751
            },
            {
                'name': 'Thai Edge Reading',
                'address': '94 Friar Street, Reading RG1 1EX',
                'postcode': 'RG1 1EX',
                'area': 'Town Centre',
                'phone': '01189 509888',
                'website': 'https://www.thaiedge.co.uk',
                'description': 'Contemporary Thai restaurant with authentic dishes',
                'cuisines': ['Thai', 'Asian'],
                'price_range': 'moderate',
                'ambiance': 'casual',
                'has_outdoor_seating': False,
                'has_parking': False,
                'accepts_reservations': True,
                'delivery_available': True,
                'latitude': 51.4563,
                'longitude': -0.9730
            },
            {
                'name': 'Côte Brasserie Reading',
                'address': '14-15 The Oracle, Reading RG1 2AG',
                'postcode': 'RG1 2AG',
                'area': 'Oracle',
                'phone': '01189 507230',
                'website': 'https://www.cote.co.uk',
                'description': 'French brasserie serving classic dishes',
                'cuisines': ['French', 'European'],
                'price_range': 'moderate',
                'ambiance': 'casual',
                'has_outdoor_seating': True,
                'has_parking': True,
                'accepts_reservations': True,
                'latitude': 51.4548,
                'longitude': -0.9734
            },
            {
                'name': 'Wildwood Reading',
                'address': 'The Oracle, Reading RG1 2AG',
                'postcode': 'RG1 2AG',
                'area': 'Oracle',
                'phone': '01189 561234',
                'website': 'https://www.wildwoodrestaurants.co.uk',
                'description': 'Italian classics with wood-fired pizzas',
                'cuisines': ['Italian', 'Pizza'],
                'price_range': 'moderate',
                'ambiance': 'family_friendly',
                'has_outdoor_seating': True,
                'has_parking': True,
                'accepts_reservations': True,
                'latitude': 51.4550,
                'longitude': -0.9736
            },
            {
                'name': 'Pho Reading',
                'address': 'The Oracle, Reading RG1 2AG',
                'postcode': 'RG1 2AG',
                'area': 'Oracle',
                'phone': '01189 502500',
                'website': 'https://www.phocafe.co.uk',
                'description': 'Vietnamese street food and fresh noodles',
                'cuisines': ['Vietnamese', 'Asian'],
                'price_range': 'budget',
                'ambiance': 'casual',
                'has_outdoor_seating': False,
                'has_parking': True,
                'accepts_reservations': False,
                'delivery_available': True,
                'latitude': 51.4551,
                'longitude': -0.9737
            },
            {
                'name': 'Miller & Carter Reading',
                'address': 'Riverside, Reading RG1 2AH',
                'postcode': 'RG1 2AH',
                'area': 'Riverside',
                'phone': '01189 589100',
                'website': 'https://www.millerandcarter.co.uk',
                'description': 'Premium British steakhouse',
                'cuisines': ['Steakhouse', 'British'],
                'price_range': 'expensive',
                'ambiance': 'fine_dining',
                'has_outdoor_seating': True,
                'has_parking': False,
                'accepts_reservations': True,
                'latitude': 51.4559,
                'longitude': -0.9748
            },
            {
                'name': 'Giggling Squid Reading',
                'address': 'The Oracle, Reading RG1 2AG',
                'postcode': 'RG1 2AG',
                'area': 'Oracle',
                'phone': '01189 503030',
                'website': 'https://www.gigglingsquid.com',
                'description': 'Thai restaurant with authentic street food dishes',
                'cuisines': ['Thai', 'Asian'],
                'price_range': 'moderate',
                'ambiance': 'casual',
                'has_outdoor_seating': True,
                'has_parking': True,
                'accepts_reservations': True,
                'delivery_available': True,
                'latitude': 51.4552,
                'longitude': -0.9735
            }
        ]

    def get_oracle_riverside_restaurants(self) -> List[Dict]:
        """
        Get curated list of Oracle and Riverside restaurants
        In production, this would scrape from multiple sources
        """
        logger.info(f"Returning {len(self.oracle_riverside_restaurants)} Oracle/Riverside restaurants")
        return self.oracle_riverside_restaurants

    def scrape_restaurant_menu(self, restaurant_data: Dict) -> Optional[Dict]:
        """
        Attempt to scrape menu from restaurant website
        Returns menu data if successful, None otherwise
        """
        website = restaurant_data.get('website')
        if not website:
            return None

        try:
            logger.info(f"Attempting to scrape menu from {website}")

            # Add rate limiting
            time.sleep(1)

            response = requests.get(website, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for common menu patterns
            menu_data = self._extract_menu_from_html(soup, restaurant_data['name'])

            if menu_data:
                logger.info(f"Successfully scraped menu for {restaurant_data['name']}")
                return menu_data
            else:
                logger.warning(f"No menu found for {restaurant_data['name']}")
                return None

        except Exception as e:
            logger.error(f"Error scraping menu for {restaurant_data['name']}: {str(e)}")
            return None

    def _extract_menu_from_html(self, soup: BeautifulSoup, restaurant_name: str) -> Optional[Dict]:
        """
        Extract menu items from HTML
        This is a generic extractor - specific sites would need custom parsers
        """
        menu_items = []

        # Common menu selectors to try
        selectors = [
            {'name': '.menu-item-name', 'price': '.menu-item-price', 'desc': '.menu-item-description'},
            {'name': '.dish-name', 'price': '.dish-price', 'desc': '.dish-description'},
            {'name': 'h3.item-title', 'price': '.price', 'desc': '.description'},
        ]

        for selector_set in selectors:
            # Try to find menu items with these selectors
            items = soup.select(selector_set['name'])

            if items:
                for item in items:
                    name = item.get_text(strip=True)

                    # Try to find price near the name
                    price = ''
                    price_elem = item.find_next(class_=selector_set['price'].replace('.', ''))
                    if price_elem:
                        price = price_elem.get_text(strip=True)

                    # Try to find description
                    desc = ''
                    desc_elem = item.find_next(class_=selector_set['desc'].replace('.', ''))
                    if desc_elem:
                        desc = desc_elem.get_text(strip=True)

                    if name:
                        menu_items.append({
                            'name': name,
                            'description': desc,
                            'price': price,
                            'category': 'Other'
                        })

        if menu_items:
            return {
                'source': 'scraped_html',
                'items': menu_items,
                'total_items': len(menu_items)
            }

        return None

    def enrich_restaurant_data(self, restaurant_data: Dict) -> Dict:
        """
        Enrich restaurant data with additional details
        Could include: reviews, opening hours, photos, etc.
        """
        # In production, this would fetch additional data from various APIs
        # For now, we'll add some sample data

        enriched = restaurant_data.copy()

        # Add default features if not present
        enriched.setdefault('delivery_available', False)
        enriched.setdefault('verified', True)
        enriched.setdefault('source', 'curated')

        return enriched

    def get_sample_menus(self) -> Dict[str, List[Dict]]:
        """
        Sample menu data for Reading restaurants
        In production, these would be scraped or from official APIs
        """
        return {
            "Bill's Reading": [
                {"name": "Eggs Benedict", "description": "Toasted muffin, smoked ham, poached eggs & hollandaise", "price": "£9.95", "category": "Breakfast"},
                {"name": "Pancakes", "description": "Buttermilk pancakes with maple syrup", "price": "£7.95", "category": "Breakfast"},
                {"name": "Quinoa & Halloumi Salad", "description": "Mixed leaves, cucumber, tomato, mint (V)", "price": "£11.95", "category": "Main"},
                {"name": "Fish & Chips", "description": "Beer-battered haddock with chips & mushy peas", "price": "£14.95", "category": "Main"},
            ],
            "Wagamama Reading": [
                {"name": "Chicken Katsu Curry", "description": "Crispy chicken with curry sauce & rice", "price": "£12.95", "category": "Main"},
                {"name": "Yasai Pad Thai", "description": "Stir-fried noodles with vegetables (VG)", "price": "£10.95", "category": "Main"},
                {"name": "Gyoza", "description": "Steamed dumplings with dipping sauce", "price": "£5.95", "category": "Appetizer"},
                {"name": "Ramen", "description": "Noodle soup with chicken or vegetables", "price": "£11.95", "category": "Main"},
            ],
            "Nando's Reading Oracle": [
                {"name": "Butterfly Chicken", "description": "Whole chicken, grilled with PERi-PERi", "price": "£13.95", "category": "Main"},
                {"name": "Halloumi Wrap", "description": "Grilled halloumi with spicy rice (V)", "price": "£7.95", "category": "Main"},
                {"name": "Peri Chips", "description": "Fries with PERi-PERi seasoning", "price": "£3.95", "category": "Sides"},
                {"name": "Sunset Burger", "description": "Chicken breast with cheese & PERi-PERi mayo", "price": "£9.95", "category": "Main"},
            ],
            "Turtle Bay Reading": [
                {"name": "Jerk Chicken", "description": "Caribbean spiced chicken with rice & peas", "price": "£14.95", "category": "Main"},
                {"name": "Roti Wrap", "description": "Curried goat or vegetables in roti (Spicy)", "price": "£12.95", "category": "Main"},
                {"name": "Plantain", "description": "Sweet fried plantain (VG)", "price": "£4.50", "category": "Sides"},
                {"name": "Caribbean Bowl", "description": "Jerk vegetables with coconut rice (VG)", "price": "£11.95", "category": "Main"},
            ],
            "Thai Edge Reading": [
                {"name": "Pad Thai", "description": "Classic stir-fried noodles with prawns or tofu", "price": "£11.95", "category": "Main"},
                {"name": "Green Curry", "description": "Spicy coconut curry with vegetables (Spicy)", "price": "£10.95", "category": "Main"},
                {"name": "Tom Yum Soup", "description": "Hot & sour soup with lemongrass (Spicy)", "price": "£6.95", "category": "Appetizer"},
                {"name": "Spring Rolls", "description": "Crispy vegetable rolls (VG)", "price": "£5.50", "category": "Appetizer"},
            ]
        }
