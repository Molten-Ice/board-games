"""
Recommendation engine for personalized restaurant suggestions
Uses hybrid approach: collaborative filtering + content-based + preference matching
"""
from sqlalchemy import func, and_, or_
from models import db, Restaurant, User, Rating, RestaurantVisit, Favorite, Cuisine
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta
import math

class RestaurantRecommender:
    """
    Personalized restaurant recommendation engine
    Tagline: "Like you have a friend in town who knows where you'll like eating"
    """

    def __init__(self):
        self.weights = {
            'collaborative': 0.3,
            'content': 0.4,
            'preference': 0.3,
            'recency_boost': 0.1
        }

    def get_recommendations(self, user, limit=20, exclude_visited=False):
        """
        Get personalized restaurant recommendations for a user

        Args:
            user: User object
            limit: Number of recommendations to return
            exclude_visited: Whether to exclude already visited restaurants

        Returns:
            List of (restaurant, score) tuples
        """
        if not user.onboarding_completed:
            # Return popular restaurants for new users
            return self._get_popular_restaurants(limit)

        # Get candidate restaurants
        candidates = self._get_candidate_restaurants(user, exclude_visited)

        # Score each candidate
        scored_restaurants = []
        for restaurant in candidates:
            score = self._calculate_restaurant_score(user, restaurant)
            scored_restaurants.append((restaurant, score))

        # Sort by score and return top N
        scored_restaurants.sort(key=lambda x: x[1], reverse=True)
        return scored_restaurants[:limit]

    def _get_candidate_restaurants(self, user, exclude_visited):
        """Get candidate restaurants to score"""
        query = Restaurant.query.filter(Restaurant.is_active == True)

        if exclude_visited:
            # Exclude restaurants user has already visited
            visited_ids = [v.restaurant_id for v in user.visits.all()]
            if visited_ids:
                query = query.filter(~Restaurant.id.in_(visited_ids))

        # Filter by distance if user has location
        # TODO: Implement geospatial filtering when we have coordinates

        return query.all()

    def _calculate_restaurant_score(self, user, restaurant):
        """
        Calculate overall score for a restaurant based on user preferences

        Score components:
        1. Collaborative filtering (similar users' preferences)
        2. Content-based (restaurant attributes match user preferences)
        3. Preference matching (cuisines, dietary, etc.)
        4. Recency boost (newly added restaurants)
        """
        scores = {
            'collaborative': self._collaborative_score(user, restaurant),
            'content': self._content_score(user, restaurant),
            'preference': self._preference_score(user, restaurant),
            'recency': self._recency_score(restaurant)
        }

        # Weighted combination
        total_score = (
            scores['collaborative'] * self.weights['collaborative'] +
            scores['content'] * self.weights['content'] +
            scores['preference'] * self.weights['preference'] +
            scores['recency'] * self.weights['recency_boost']
        )

        return total_score

    def _collaborative_score(self, user, restaurant):
        """
        Collaborative filtering: find similar users and see what they liked
        Returns score 0-1
        """
        # Get users similar to this user
        similar_users = self._find_similar_users(user, limit=10)

        if not similar_users:
            return 0.5  # Neutral score if no similar users

        # Get ratings from similar users for this restaurant
        similar_user_ids = [u.id for u in similar_users]
        ratings = Rating.query.filter(
            and_(
                Rating.user_id.in_(similar_user_ids),
                Rating.restaurant_id == restaurant.id
            )
        ).all()

        if not ratings:
            return 0.5  # Neutral if no ratings from similar users

        # Average rating from similar users, normalized to 0-1
        avg_rating = sum(r.rating for r in ratings) / len(ratings)
        return avg_rating / 5.0

    def _content_score(self, user, restaurant):
        """
        Content-based filtering: match restaurant attributes to user preferences
        Returns score 0-1
        """
        score = 0.0
        factors = 0

        # Price range match
        if user.price_preference and restaurant.price_range:
            if user.price_preference == restaurant.price_range:
                score += 1.0
            elif self._adjacent_price_range(user.price_preference, restaurant.price_range):
                score += 0.5
            factors += 1

        # Ambiance match
        if user.preferred_ambiance and restaurant.ambiance:
            if user.preferred_ambiance == restaurant.ambiance:
                score += 1.0
            factors += 1

        # Average rating (quality signal)
        if restaurant.average_rating > 0:
            score += restaurant.average_rating / 5.0
            factors += 1

        return score / factors if factors > 0 else 0.5

    def _preference_score(self, user, restaurant):
        """
        Direct preference matching: cuisines and dietary requirements
        Returns score 0-1
        """
        score = 0.0
        factors = 0

        # Cuisine match
        user_cuisine_names = set(c.name for c in user.favorite_cuisines)
        restaurant_cuisine_names = set(c.name for c in restaurant.cuisines)

        if user_cuisine_names:
            cuisine_overlap = len(user_cuisine_names & restaurant_cuisine_names)
            cuisine_score = cuisine_overlap / len(user_cuisine_names)
            score += cuisine_score
            factors += 1

        # Check if restaurant has menu items matching dietary preferences
        if user.dietary_preferences:
            dietary_score = self._check_dietary_match(user, restaurant)
            score += dietary_score
            factors += 1

        # Adventurousness factor
        if user.adventurousness:
            # Higher adventurousness = bonus for exotic cuisines
            exotic_cuisines = {'Ethiopian', 'Moroccan', 'Korean', 'Thai', 'Vietnamese', 'Peruvian'}
            if restaurant_cuisine_names & exotic_cuisines:
                score += (user.adventurousness / 5.0) * 0.5
                factors += 0.5

        return score / factors if factors > 0 else 0.5

    def _recency_score(self, restaurant):
        """
        Boost for recently added restaurants
        Returns score 0-1
        """
        days_old = (datetime.utcnow() - restaurant.created_at).days
        if days_old < 7:
            return 1.0
        elif days_old < 30:
            return 0.7
        elif days_old < 90:
            return 0.5
        return 0.3

    def _find_similar_users(self, user, limit=10):
        """
        Find users with similar preferences and ratings

        Similarity based on:
        - Shared cuisine preferences
        - Similar price preferences
        - Similar ratings patterns
        """
        # Get users with overlapping cuisine preferences
        user_cuisine_ids = [c.id for c in user.favorite_cuisines]

        if not user_cuisine_ids:
            return []

        # Find users who like at least one of the same cuisines
        similar_users = db.session.query(User).join(User.favorite_cuisines).filter(
            and_(
                Cuisine.id.in_(user_cuisine_ids),
                User.id != user.id
            )
        ).distinct().limit(limit * 2).all()  # Get more than needed for filtering

        # Score similarity
        user_similarities = []
        for other_user in similar_users:
            similarity = self._calculate_user_similarity(user, other_user)
            user_similarities.append((other_user, similarity))

        # Sort by similarity and return top N
        user_similarities.sort(key=lambda x: x[1], reverse=True)
        return [u for u, _ in user_similarities[:limit]]

    def _calculate_user_similarity(self, user1, user2):
        """
        Calculate similarity score between two users
        Returns score 0-1
        """
        score = 0.0
        factors = 0

        # Cuisine overlap
        cuisines1 = set(c.id for c in user1.favorite_cuisines)
        cuisines2 = set(c.id for c in user2.favorite_cuisines)

        if cuisines1 and cuisines2:
            overlap = len(cuisines1 & cuisines2)
            union = len(cuisines1 | cuisines2)
            cuisine_similarity = overlap / union if union > 0 else 0
            score += cuisine_similarity
            factors += 1

        # Price preference match
        if user1.price_preference and user2.price_preference:
            if user1.price_preference == user2.price_preference:
                score += 1.0
            elif self._adjacent_price_range(user1.price_preference, user2.price_preference):
                score += 0.5
            factors += 1

        # Dietary preferences overlap
        dietary1 = set(d.id for d in user1.dietary_preferences)
        dietary2 = set(d.id for d in user2.dietary_preferences)

        if dietary1 or dietary2:
            overlap = len(dietary1 & dietary2)
            max_len = max(len(dietary1), len(dietary2))
            dietary_similarity = overlap / max_len if max_len > 0 else 0
            score += dietary_similarity
            factors += 1

        # Adventurousness similarity
        if user1.adventurousness and user2.adventurousness:
            adv_diff = abs(user1.adventurousness - user2.adventurousness)
            adv_similarity = 1.0 - (adv_diff / 4.0)  # Max diff is 4
            score += adv_similarity
            factors += 1

        return score / factors if factors > 0 else 0.0

    def _check_dietary_match(self, user, restaurant):
        """
        Check if restaurant has menu items matching user's dietary preferences
        Returns score 0-1
        """
        if not user.dietary_preferences:
            return 1.0  # No dietary restrictions = always matches

        # Get restaurant's menu items
        menu = restaurant.menus.filter_by(is_current=True).first()
        if not menu:
            return 0.5  # Neutral if no menu available

        # Check if menu has items matching dietary preferences
        user_dietary_names = [d.name.lower() for d in user.dietary_preferences]

        matching_items = 0
        total_items = 0

        for item in menu.items.all():
            total_items += 1
            try:
                import json
                item_tags = json.loads(item.dietary_tags) if item.dietary_tags else []
                item_tags_lower = [tag.lower() for tag in item_tags]

                # Check if any user preference is in item tags
                if any(pref in item_tags_lower for pref in user_dietary_names):
                    matching_items += 1
            except:
                pass

        if total_items == 0:
            return 0.5

        match_ratio = matching_items / total_items
        return min(match_ratio * 2, 1.0)  # Boost and cap at 1.0

    def _adjacent_price_range(self, price1, price2):
        """Check if two price ranges are adjacent"""
        price_order = ['budget', 'moderate', 'expensive', 'luxury']
        try:
            idx1 = price_order.index(price1)
            idx2 = price_order.index(price2)
            return abs(idx1 - idx2) == 1
        except ValueError:
            return False

    def _get_popular_restaurants(self, limit):
        """Get popular restaurants for users without preferences"""
        restaurants = Restaurant.query.filter(
            Restaurant.is_active == True
        ).order_by(
            Restaurant.average_rating.desc(),
            Restaurant.total_ratings.desc()
        ).limit(limit).all()

        # Return with neutral scores
        return [(r, 0.5) for r in restaurants]

    def get_similar_restaurants(self, restaurant, limit=5):
        """
        Find restaurants similar to a given restaurant
        Useful for "You might also like..." recommendations
        """
        candidates = Restaurant.query.filter(
            and_(
                Restaurant.id != restaurant.id,
                Restaurant.is_active == True
            )
        ).all()

        scored = []
        for candidate in candidates:
            score = self._restaurant_similarity(restaurant, candidate)
            scored.append((candidate, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]

    def _restaurant_similarity(self, restaurant1, restaurant2):
        """Calculate similarity between two restaurants"""
        score = 0.0
        factors = 0

        # Cuisine overlap
        cuisines1 = set(c.id for c in restaurant1.cuisines)
        cuisines2 = set(c.id for c in restaurant2.cuisines)

        if cuisines1 and cuisines2:
            overlap = len(cuisines1 & cuisines2)
            union = len(cuisines1 | cuisines2)
            cuisine_sim = overlap / union if union > 0 else 0
            score += cuisine_sim
            factors += 1

        # Price range match
        if restaurant1.price_range and restaurant2.price_range:
            if restaurant1.price_range == restaurant2.price_range:
                score += 1.0
            elif self._adjacent_price_range(restaurant1.price_range, restaurant2.price_range):
                score += 0.5
            factors += 1

        # Ambiance match
        if restaurant1.ambiance and restaurant2.ambiance:
            if restaurant1.ambiance == restaurant2.ambiance:
                score += 1.0
            factors += 1

        # Similar ratings
        if restaurant1.average_rating > 0 and restaurant2.average_rating > 0:
            rating_diff = abs(restaurant1.average_rating - restaurant2.average_rating)
            rating_sim = 1.0 - (rating_diff / 5.0)
            score += rating_sim
            factors += 1

        return score / factors if factors > 0 else 0.0
