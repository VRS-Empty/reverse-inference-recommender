import random
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import time
import re


# CONFIGURATION - INSERT YOUR API KEY HERE
# Get your free API key from https://newsapi.org/register
NEWS_API_KEY = "INSERT YOUR API KEY HERE"  # <- INSERT YOUR API KEY HERE

# API Endpoints
NEWS_API_BASE = "https://newsapi.org/v2"
REDDIT_API_BASE = "https://www.reddit.com"


# DATA CLASSES


@dataclass
class Character:
    """Represents a virtual user with various attributes"""
    name: str
    age: int
    gender: str
    location: str
    occupation: str
    interests: List[str]
    personality_traits: List[str]
    activity_level: str = "moderate"  # low, moderate, high
    tech_savviness: str = "average"  # low, average, high
    social_connectivity: int = 50  # 0-100 representing social network size
    education_level: str = "college"  # high_school, college, graduate, other

@dataclass
class Recommendation:
    """Represents a single content recommendation"""
    title: str
    source: str
    url: str
    algorithm: str
    score: float
    description: str = ""
    published_at: str = ""


# API CLIENTS


class NewsAPIClient:
    """Client for fetching news from NewsAPI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"X-Api-Key": api_key}
    
    def fetch_by_interests(self, interests: List[str], limit: int = 5) -> List[Dict]:
        """Fetch news articles based on interests"""
        if not self.api_key or self.api_key == "YOUR_NEWS_API_KEY_HERE":
            return self._get_placeholder_news("interests", interests)
        
        articles = []
        for interest in interests[:2]:  # Limit to 2 interests to avoid rate limits
            try:
                url = f"{NEWS_API_BASE}/everything"
                params = {
                    "q": interest,
                    "sortBy": "relevancy",
                    "pageSize": limit,
                    "language": "en",
                    "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                }
                response = requests.get(url, params=params, headers=self.headers, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    articles.extend(data.get("articles", [])[:limit])
                else:
                    print(f"NewsAPI error for interest '{interest}': {response.status_code}")
            except Exception as e:
                print(f"NewsAPI request failed for interest '{interest}': {e}")
        
        return articles if articles else self._get_placeholder_news("interests", interests)
    
    def fetch_by_location(self, location: str, limit: int = 5) -> List[Dict]:
        """Fetch news articles based on location"""
        if not self.api_key or self.api_key == "YOUR_NEWS_API_KEY_HERE":
            return self._get_placeholder_news("location", [location])
        
        try:
            # Map location to country code (simplified)
            country_codes = {
                "USA": "us", "United States": "us", "UK": "gb", "United Kingdom": "gb",
                "Canada": "ca", "Australia": "au", "Germany": "de", "France": "fr", 
                "Japan": "jp", "India": "in", "Italy": "it", "Spain": "es",
                "Netherlands": "nl", "Brazil": "br", "Mexico": "mx"
            }
            
            # Extract country from location string
            country_found = None
            for country_name, code in country_codes.items():
                if country_name.lower() in location.lower():
                    country_found = code
                    break
            
            country = country_found or "us"  # Default to US
            
            url = f"{NEWS_API_BASE}/top-headlines"
            params = {"country": country, "pageSize": limit}
            response = requests.get(url, params=params, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("articles", [])[:limit]
        except Exception as e:
            print(f"NewsAPI request failed for location '{location}': {e}")
        
        return self._get_placeholder_news("location", [location])
    
    def fetch_trending(self, limit: int = 5) -> List[Dict]:
        """Fetch trending/popular news"""
        if not self.api_key or self.api_key == "YOUR_NEWS_API_KEY_HERE":
            return self._get_placeholder_news("trending", [])
        
        try:
            url = f"{NEWS_API_BASE}/top-headlines"
            params = {"country": "us", "pageSize": limit}
            response = requests.get(url, params=params, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("articles", [])[:limit]
        except Exception as e:
            print(f"NewsAPI trending request failed: {e}")
        
        return self._get_placeholder_news("trending", [])
    
    def _get_placeholder_news(self, type_: str, context: List[str]) -> List[Dict]:
        """Generate placeholder news when API is unavailable"""
        placeholders = {
            "interests": [
                {"title": f"Breaking: Major developments in {context[0] if context else 'technology'}",
                 "source": {"name": "Placeholder News"}, "url": "#", 
                 "description": "This is placeholder content - API key needed",
                 "publishedAt": datetime.now().isoformat()},
                {"title": f"Expert insights on {context[0] if context else 'science'}",
                 "source": {"name": "Placeholder Times"}, "url": "#",
                 "description": "Configure NewsAPI key for real content",
                 "publishedAt": datetime.now().isoformat()}
            ],
            "location": [
                {"title": f"Local news from {context[0] if context else 'your area'}",
                 "source": {"name": "Local Placeholder"}, "url": "#",
                 "description": "Location-based placeholder content",
                 "publishedAt": datetime.now().isoformat()}
            ],
            "trending": [
                {"title": "Trending: Major global event captures attention",
                 "source": {"name": "Trending Placeholder"}, "url": "#",
                 "description": "Trending placeholder content",
                 "publishedAt": datetime.now().isoformat()}
            ]
        }
        return placeholders.get(type_, placeholders["trending"])

class RedditClient:
    """Client for fetching content from Reddit's public API"""
    
    def __init__(self):
        self.headers = {"User-Agent": "RecommendationSystem/1.0"}
    
    def fetch_by_interests(self, interests: List[str], limit: int = 5) -> List[Dict]:
        """Fetch Reddit posts based on interests"""
        posts = []
        
        # Map interests to subreddits
        subreddit_map = {
            "technology": "technology", "gaming": "gaming", "sports": "sports",
            "music": "music", "art": "art", "science": "science",
            "food": "food", "travel": "travel", "fitness": "fitness",
            "movies": "movies", "books": "books", "photography": "photography",
            "programming": "programming", "ai": "MachineLearning", "fashion": "fashion",
            "business": "business", "finance": "finance", "cooking": "cooking",
            "health": "health", "psychology": "psychology", "history": "history",
            "politics": "politics", "environment": "environment", "space": "space"
        }
        
        for interest in interests[:2]:  # Limit requests
            subreddit = subreddit_map.get(interest.lower(), interest.lower())
            try:
                url = f"{REDDIT_API_BASE}/r/{subreddit}/hot.json"
                params = {"limit": limit}
                response = requests.get(url, params=params, headers=self.headers, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    for child in data.get("data", {}).get("children", [])[:limit]:
                        post = child.get("data", {})
                        posts.append({
                            "title": post.get("title", ""),
                            "subreddit": post.get("subreddit", ""),
                            "url": f"https://reddit.com{post.get('permalink', '')}",
                            "score": post.get("score", 0),
                            "created": post.get("created_utc", 0)
                        })
                else:
                    print(f"Reddit error for subreddit '{subreddit}': {response.status_code}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Reddit request failed for interest '{interest}': {e}")
        
        return posts if posts else self._get_placeholder_reddit("interests", interests)
    
    def fetch_trending(self, limit: int = 5) -> List[Dict]:
        """Fetch trending posts from Reddit"""
        try:
            url = f"{REDDIT_API_BASE}/r/popular/hot.json"
            params = {"limit": limit}
            response = requests.get(url, params=params, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                posts = []
                for child in data.get("data", {}).get("children", [])[:limit]:
                    post = child.get("data", {})
                    posts.append({
                        "title": post.get("title", ""),
                        "subreddit": post.get("subreddit", ""),
                        "url": f"https://reddit.com{post.get('permalink', '')}",
                        "score": post.get("score", 0),
                        "created": post.get("created_utc", 0)
                    })
                return posts
        except Exception as e:
            print(f"Reddit trending request failed: {e}")
        
        return self._get_placeholder_reddit("trending", [])
    
    def _get_placeholder_reddit(self, type_: str, context: List[str]) -> List[Dict]:
        """Generate placeholder Reddit content"""
        return [
            {"title": f"Popular discussion about {context[0] if context else 'trending topics'}",
             "subreddit": "placeholder", "url": "#", "score": 1000, "created": time.time()},
            {"title": "Placeholder Reddit content - API temporarily unavailable",
             "subreddit": "placeholder", "url": "#", "score": 500, "created": time.time()}
        ]

# RECOMMENDATION ALGORITHMS


class RecommendationInferenceEngine:
    """Infers which recommendation algorithms would be applied to a character"""
    
    def __init__(self):
        self.algorithm_weights = {
            "content_based": 0.0,
            "collaborative": 0.0,
            "popularity": 0.0,
            "demographic": 0.0
        }
    
    def infer_algorithms(self, character: Character) -> Dict[str, float]:
        """
        Probabilistically infer which algorithms would be used based on character attributes
        Returns normalized probability scores for each algorithm
        """
        
        # Reset weights
        self.algorithm_weights = {
            "content_based": 0.0,
            "collaborative": 0.0,
            "popularity": 0.0,
            "demographic": 0.0
        }
        
        # Content-Based Filtering Weight Calculation
        # More interests = higher weight for content-based
        interest_weight = min(len(character.interests) * 0.2, 1.0)
        self.algorithm_weights["content_based"] += interest_weight * 0.4
        
        # Tech-savvy users get more content-based recommendations
        if character.tech_savviness == "high":
            self.algorithm_weights["content_based"] += 0.2
        elif character.tech_savviness == "average":
            self.algorithm_weights["content_based"] += 0.1
        
        # Active users with specific interests
        if character.activity_level == "high" and len(character.interests) > 3:
            self.algorithm_weights["content_based"] += 0.15
        
        # Education level factor
        if character.education_level in ["college", "graduate"]:
            self.algorithm_weights["content_based"] += 0.1
        
        # Collaborative Filtering Weight Calculation
        # Higher social connectivity = higher collaborative weight
        social_weight = (character.social_connectivity / 100) * 0.5
        self.algorithm_weights["collaborative"] += social_weight
        
        # Active users contribute more to collaborative filtering
        if character.activity_level == "high":
            self.algorithm_weights["collaborative"] += 0.2
        elif character.activity_level == "moderate":
            self.algorithm_weights["collaborative"] += 0.1
        
        # Age factor for collaborative (25-45 age group most active)
        if 25 <= character.age <= 45:
            self.algorithm_weights["collaborative"] += 0.15
        
        # Popularity/Trending Weight Calculation
        # Younger users get more trending content
        if character.age < 25:
            self.algorithm_weights["popularity"] += 0.4
        elif character.age < 35:
            self.algorithm_weights["popularity"] += 0.25
        else:
            self.algorithm_weights["popularity"] += 0.1
        
        # Low activity users get more popular content (easier engagement)
        if character.activity_level == "low":
            self.algorithm_weights["popularity"] += 0.2
        
        # New users (simulated by low tech-savviness) get more trending
        if character.tech_savviness == "low":
            self.algorithm_weights["popularity"] += 0.15
        
        # Demographic Filtering Weight Calculation
        # Base demographic weight
        self.algorithm_weights["demographic"] += 0.15
        
        # Age-based demographic targeting
        if character.age < 18 or character.age > 65:
            self.algorithm_weights["demographic"] += 0.25
        else:
            self.algorithm_weights["demographic"] += 0.1
        
        # Location-based demographic
        if character.location:
            self.algorithm_weights["demographic"] += 0.15
        
        # Gender factor
        self.algorithm_weights["demographic"] += 0.05
        
        # Occupation factor
        if character.occupation:
            self.algorithm_weights["demographic"] += 0.1
        
        # Personality traits factor
        if len(character.personality_traits) > 3:
            self.algorithm_weights["demographic"] += 0.1
        
        # Normalize weights to sum to 1.0 (probability distribution)
        total_weight = sum(self.algorithm_weights.values())
        if total_weight > 0:
            for key in self.algorithm_weights:
                self.algorithm_weights[key] /= total_weight
        
        # Add some randomness to simulate real-world variability
        for key in self.algorithm_weights:
            noise = random.uniform(-0.05, 0.05)
            self.algorithm_weights[key] = max(0, min(1, self.algorithm_weights[key] + noise))
        
        # Re-normalize after adding noise
        total_weight = sum(self.algorithm_weights.values())
        if total_weight > 0:
            for key in self.algorithm_weights:
                self.algorithm_weights[key] /= total_weight
        
        return self.algorithm_weights

# CONTENT FETCHER AND RECOMMENDER

class ContentRecommender:
    """Fetches and combines content from multiple sources based on inferred algorithms"""
    
    def __init__(self, news_api_key: str):
        self.news_client = NewsAPIClient(news_api_key)
        self.reddit_client = RedditClient()
    
    def generate_feed(self, character: Character, algorithm_weights: Dict[str, float], 
                     total_items: int = 20) -> List[Recommendation]:
        """
        Generate a recommendation feed based on algorithm weights
        """
        recommendations = []
        
        # Calculate how many items per algorithm based on weights
        items_per_algorithm = {
            algo: max(1, int(weight * total_items))
            for algo, weight in algorithm_weights.items()
        }
        
        # Content-Based Recommendations
        if items_per_algorithm["content_based"] > 0:
            content_recs = self._get_content_based(character, items_per_algorithm["content_based"])
            recommendations.extend(content_recs)
        
        # Collaborative Filtering Recommendations (simulated)
        if items_per_algorithm["collaborative"] > 0:
            collab_recs = self._get_collaborative(character, items_per_algorithm["collaborative"])
            recommendations.extend(collab_recs)
        
        # Popularity/Trending Recommendations
        if items_per_algorithm["popularity"] > 0:
            popular_recs = self._get_popularity(character, items_per_algorithm["popularity"])
            recommendations.extend(popular_recs)
        
        # Demographic Filtering Recommendations
        if items_per_algorithm["demographic"] > 0:
            demo_recs = self._get_demographic(character, items_per_algorithm["demographic"])
            recommendations.extend(demo_recs)
        
        # Shuffle to mix different algorithm results
        random.shuffle(recommendations)
        
        return recommendations[:total_items]
    
    def _get_content_based(self, character: Character, limit: int) -> List[Recommendation]:
        """Fetch content based on user interests"""
        recommendations = []
        
        # Fetch from NewsAPI
        news_articles = self.news_client.fetch_by_interests(character.interests, limit//2 + 1)
        for article in news_articles[:limit//2]:
            recommendations.append(Recommendation(
                title=article.get("title", ""),
                source=f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}",
                url=article.get("url", "#"),
                algorithm="Content-Based",
                score=random.uniform(0.7, 0.95),
                description=article.get("description", "")[:200] if article.get("description") else "",
                published_at=article.get("publishedAt", "")
            ))
        
        # Fetch from Reddit
        reddit_posts = self.reddit_client.fetch_by_interests(character.interests, limit//2 + 1)
        for post in reddit_posts[:limit//2]:
            recommendations.append(Recommendation(
                title=post.get("title", ""),
                source=f"Reddit - r/{post.get('subreddit', 'unknown')}",
                url=post.get("url", "#"),
                algorithm="Content-Based",
                score=random.uniform(0.7, 0.95),
                description=f"Score: {post.get('score', 0)}"
            ))
        
        return recommendations
    
    def _get_collaborative(self, character: Character, limit: int) -> List[Recommendation]:
        """Simulate collaborative filtering recommendations"""
        recommendations = []
        
        # Simulate by fetching related interests
        related_interests = self._get_related_interests(character.interests)
        
        # Fetch from Reddit based on related interests
        reddit_posts = self.reddit_client.fetch_by_interests(related_interests, limit)
        for post in reddit_posts[:limit]:
            recommendations.append(Recommendation(
                title=post.get("title", ""),
                source=f"Reddit - r/{post.get('subreddit', 'unknown')}",
                url=post.get("url", "#"),
                algorithm="Collaborative",
                score=random.uniform(0.6, 0.85),
                description=f"Based on similar users' preferences"
            ))
        
        return recommendations
    
    def _get_popularity(self, character: Character, limit: int) -> List[Recommendation]:
        """Fetch trending/popular content"""
        recommendations = []
        
        # Fetch trending news
        trending_news = self.news_client.fetch_trending(limit//2 + 1)
        for article in trending_news[:limit//2]:
            recommendations.append(Recommendation(
                title=article.get("title", ""),
                source=f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}",
                url=article.get("url", "#"),
                algorithm="Popularity/Trending",
                score=random.uniform(0.8, 1.0),
                description="Trending now",
                published_at=article.get("publishedAt", "")
            ))
        
        # Fetch trending Reddit posts
        reddit_trending = self.reddit_client.fetch_trending(limit//2 + 1)
        for post in reddit_trending[:limit//2]:
            recommendations.append(Recommendation(
                title=post.get("title", ""),
                source=f"Reddit - r/{post.get('subreddit', 'unknown')}",
                url=post.get("url", "#"),
                algorithm="Popularity/Trending",
                score=random.uniform(0.8, 1.0),
                description=f"Popular with {post.get('score', 0)} upvotes"
            ))
        
        return recommendations
    
    def _get_demographic(self, character: Character, limit: int) -> List[Recommendation]:
        """Fetch content based on demographic attributes"""
        recommendations = []
        
        # Fetch location-based news
        location_news = self.news_client.fetch_by_location(character.location, limit)
        for article in location_news[:limit]:
            recommendations.append(Recommendation(
                title=article.get("title", ""),
                source=f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}",
                url=article.get("url", "#"),
                algorithm="Demographic",
                score=random.uniform(0.65, 0.9),
                description=f"Relevant to {character.location}",
                published_at=article.get("publishedAt", "")
            ))
        
        return recommendations
    
    def _get_related_interests(self, interests: List[str]) -> List[str]:
        """Get interests related to the user's interests"""
        interest_relations = {
            "technology": ["programming", "gadgets", "AI"],
            "gaming": ["esports", "gamedev", "pcgaming"],
            "sports": ["fitness", "olympics", "soccer"],
            "music": ["concerts", "instruments", "audio"],
            "art": ["design", "photography", "crafts"],
            "science": ["space", "biology", "physics"],
            "food": ["cooking", "recipes", "restaurants"],
            "travel": ["backpacking", "digitalnomad", "solotravel"],
            "business": ["entrepreneur", "startups", "investing"],
            "health": ["nutrition", "meditation", "wellness"]
        }
        
        related = []
        for interest in interests:
            related.extend(interest_relations.get(interest.lower(), [interest]))
        
        return related[:3]  # Limit to 3 related interests

# USER INTERFACE FUNCTIONS

class InteractiveCharacterBuilder:
    """Interactive character creation through user input"""
    
    @staticmethod
    def get_user_input() -> Character:
        """Collect user information through interactive prompts"""
        print("\n" + "="*80)
        print("CREATE YOUR VIRTUAL CHARACTER")
        print("="*80)
        print("Please provide the following information to create your virtual profile.")
        print("This will be used to simulate how recommendation algorithms would target you.\n")
        
        # Name
        name = input("1. What's your name? ").strip()
        if not name:
            name = "Anonymous User"
        
        # Age
        while True:
            try:
                age_input = input("2. What's your age? ")
                age = int(age_input)
                if 1 <= age <= 120:
                    break
                else:
                    print("   Please enter a valid age between 1 and 120.")
            except ValueError:
                print("   Please enter a valid number.")
        
        # Gender
        print("\n3. What's your gender?")
        print("   a) Male")
        print("   b) Female") 
        print("   c) Non-binary")
        print("   d) Prefer not to say")
        gender_choice = input("   Enter your choice (a/b/c/d): ").lower().strip()
        gender_map = {"a": "Male", "b": "Female", "c": "Non-binary", "d": "Not specified"}
        gender = gender_map.get(gender_choice, "Not specified")
        
        # Location
        print("\n4. Where are you located?")
        print("   Examples: 'New York, USA', 'London, UK', 'Tokyo, Japan'")
        location = input("   Enter your location: ").strip()
        if not location:
            location = "Not specified"
        
        # Occupation
        print("\n5. What's your occupation?")
        print("   Examples: 'Software Engineer', 'Teacher', 'Student', 'Artist'")
        occupation = input("   Enter your occupation: ").strip()
        if not occupation:
            occupation = "Not specified"
        
        # Education Level
        print("\n6. What's your highest education level?")
        print("   a) High School")
        print("   b) College/University")
        print("   c) Graduate School")
        print("   d) Other")
        edu_choice = input("   Enter your choice (a/b/c/d): ").lower().strip()
        edu_map = {"a": "high_school", "b": "college", "c": "graduate", "d": "other"}
        education_level = edu_map.get(edu_choice, "other")
        
        # Interests
        print("\n7. What are your main interests? (Enter up to 5, separated by commas)")
        print("   Examples: technology, music, sports, cooking, travel, gaming, art")
        interests_input = input("   Your interests: ").strip()
        interests = [i.strip() for i in interests_input.split(",") if i.strip()][:5]
        if not interests:
            interests = ["general"]
        
        # Personality Traits
        print("\n8. How would you describe your personality? (Enter 3-5 traits, separated by commas)")
        print("   Examples: creative, analytical, social, introverted, adventurous")
        traits_input = input("   Your traits: ").strip()
        personality_traits = [t.strip() for t in traits_input.split(",") if t.strip()][:5]
        if not personality_traits:
            personality_traits = ["balanced"]
        
        # Activity Level
        print("\n9. How active are you on social media/content platforms?")
        print("   a) Low (rarely post or interact)")
        print("   b) Moderate (occasional posts and interactions)")
        print("   c) High (frequent posts and interactions)")
        activity_choice = input("   Enter your choice (a/b/c): ").lower().strip()
        activity_map = {"a": "low", "b": "moderate", "c": "high"}
        activity_level = activity_map.get(activity_choice, "moderate")
        
        # Tech Savviness
        print("\n10. How would you rate your tech-savviness?")
        print("    a) Low (basic user)")
        print("    b) Average (comfortable with technology)")
        print("    c) High (power user/early adopter)")
        tech_choice = input("    Enter your choice (a/b/c): ").lower().strip()
        tech_map = {"a": "low", "b": "average", "c": "high"}
        tech_savviness = tech_map.get(tech_choice, "average")
        
        # Social Connectivity
        print("\n11. How large is your social network?")
        print("    a) Small (0-50 connections)")
        print("    b) Medium (50-200 connections)")
        print("    c) Large (200-500 connections)")
        print("    d) Very Large (500+ connections)")
        social_choice = input("    Enter your choice (a/b/c/d): ").lower().strip()
        social_map = {"a": 25, "b": 60, "c": 75, "d": 90}
        social_connectivity = social_map.get(social_choice, 50)
        
        # Create and return character
        character = Character(
            name=name,
            age=age,
            gender=gender,
            location=location,
            occupation=occupation,
            interests=interests,
            personality_traits=personality_traits,
            activity_level=activity_level,
            tech_savviness=tech_savviness,
            social_connectivity=social_connectivity,
            education_level=education_level
        )
        
        return character

# DISPLAY FUNCTIONS

def display_character_profile(character: Character):
    """Display character profile"""
    print("\n" + "="*80)
    print(f"CHARACTER PROFILE: {character.name}")
    print("="*80)
    print(f"Age: {character.age}")
    print(f"Gender: {character.gender}")
    print(f"Location: {character.location}")
    print(f"Occupation: {character.occupation}")
    print(f"Education: {character.education_level.replace('_', ' ').title()}")
    print(f"Interests: {', '.join(character.interests)}")
    print(f"Personality: {', '.join(character.personality_traits)}")
    print(f"Activity Level: {character.activity_level}")
    print(f"Tech Savviness: {character.tech_savviness}")
    print(f"Social Connectivity: {character.social_connectivity}%")

def display_algorithm_inference(weights: Dict[str, float]):
    """Display inferred algorithm weights"""
    print("\n" + "-"*80)
    print("INFERRED RECOMMENDATION ALGORITHMS")
    print("-"*80)
    print("\nPlatforms would likely use these algorithms for you:\n")
    
    sorted_algorithms = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    
    for algo, weight in sorted_algorithms:
        bar_length = int(weight * 50)
        bar = "█" * bar_length + "░" * (50 - bar_length)
        algo_name = algo.replace("_", " ").title()
        print(f"{algo_name:25} [{bar}] {weight:.1%}")
    
    print("\nAnalysis:")
    dominant_algo = sorted_algorithms[0][0]
    if dominant_algo == "content_based":
        print("→ Platforms would primarily use Content-Based Filtering")
        print("→ Platforms would primarily use Content-Based Filtering")
        print("  Your specific interests drive most recommendations")
    elif dominant_algo == "collaborative":
        print("→ Platforms would primarily use Collaborative Filtering")
        print("  Your behavior would be compared with similar users")
    elif dominant_algo == "popularity":
        print("→ Platforms would primarily use Popularity/Trending algorithms")
        print("  You'd see mostly trending and viral content")
    elif dominant_algo == "demographic":
        print("→ Platforms would primarily use Demographic Filtering")
        print("  Your age, location, and demographics drive recommendations")
    
    print("\nSecondary algorithms would supplement the primary approach.")

def display_recommendations(recommendations: List[Recommendation]):
    """Display the generated recommendations"""
    print("\n" + "-"*80)
    print("YOUR PERSONALIZED RECOMMENDATION FEED")
    print("-"*80)
    
    if not recommendations:
        print("No recommendations generated.")
        return
    
    # Group by algorithm for better display
    algo_groups = {}
    for rec in recommendations:
        if rec.algorithm not in algo_groups:
            algo_groups[rec.algorithm] = []
        algo_groups[rec.algorithm].append(rec)
    
    for algo, recs in algo_groups.items():
        print(f"\n📊 {algo.upper()} RECOMMENDATIONS ({len(recs)} items)")
        print("-" * 60)
        
        for i, rec in enumerate(recs[:5], 1):  # Show max 5 per algorithm
            print(f"{i}. {rec.title[:70]}{'...' if len(rec.title) > 70 else ''}")
            print(f"   Source: {rec.source}")
            print(f"   Score: {rec.score:.2f}")
            if rec.description:
                desc = rec.description[:100] + "..." if len(rec.description) > 100 else rec.description
                print(f"   {desc}")
            if rec.url != "#":
                print(f"   URL: {rec.url}")
            print()

def display_summary_stats(character: Character, weights: Dict[str, float], 
                         recommendations: List[Recommendation]):
    """Display summary statistics about the recommendation session"""
    print("\n" + "="*80)
    print("SESSION SUMMARY")
    print("="*80)
    
    print(f"Character: {character.name}")
    print(f"Total Recommendations Generated: {len(recommendations)}")
    
    # Algorithm distribution
    algo_counts = {}
    for rec in recommendations:
        algo_counts[rec.algorithm] = algo_counts.get(rec.algorithm, 0) + 1
    
    print("\nRecommendations by Algorithm:")
    for algo, count in sorted(algo_counts.items()):
        percentage = (count / len(recommendations)) * 100 if recommendations else 0
        print(f"  {algo}: {count} ({percentage:.1f}%)")
    
    # Average scores by algorithm
    print("\nAverage Recommendation Scores:")
    algo_scores = {}
    for rec in recommendations:
        if rec.algorithm not in algo_scores:
            algo_scores[rec.algorithm] = []
        algo_scores[rec.algorithm].append(rec.score)
    
    for algo, scores in algo_scores.items():
        avg_score = sum(scores) / len(scores) if scores else 0
        print(f"  {algo}: {avg_score:.3f}")
    
    # Source distribution
    source_counts = {}
    for rec in recommendations:
        source_type = "NewsAPI" if "NewsAPI" in rec.source else "Reddit" if "Reddit" in rec.source else "Other"
        source_counts[source_type] = source_counts.get(source_type, 0) + 1
    
    print("\nContent Sources:")
    for source, count in sorted(source_counts.items()):
        percentage = (count / len(recommendations)) * 100 if recommendations else 0
        print(f"  {source}: {count} ({percentage:.1f}%)")

def create_sample_character() -> Character:
    """Create a sample character for demo purposes"""
    return Character(
        name="Alex Demo",
        age=28,
        gender="Non-binary",
        location="San Francisco, USA",
        occupation="Software Engineer",
        interests=["technology", "gaming", "ai", "music", "fitness"],
        personality_traits=["analytical", "creative", "introverted", "curious"],
        activity_level="high",
        tech_savviness="high",
        social_connectivity=70,
        education_level="college"
    )

def main_menu():
    """Display main menu and handle user choices"""
    while True:
        print("\n" + "="*80)
        print("REVERSE-INFERENCE RECOMMENDATION SYSTEM")
        print("="*80)
        print("1. Create Custom Character")
        print("2. Use Demo Character")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            return "custom"
        elif choice == "2":
            return "demo"
        elif choice == "3":
            print("\nThank you for using the Recommendation System!")
            return "exit"
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def run_recommendation_analysis(character: Character, api_key: str):
    """Run the complete recommendation analysis"""
    # Display character profile
    display_character_profile(character)
    
    # Initialize components
    inference_engine = RecommendationInferenceEngine()
    content_recommender = ContentRecommender(api_key)
    
    print("\n🔄 Analyzing your profile and inferring recommendation algorithms...")
    
    # Infer algorithms
    algorithm_weights = inference_engine.infer_algorithms(character)
    
    # Display algorithm inference
    display_algorithm_inference(algorithm_weights)
    
    print("\n🔄 Fetching personalized content recommendations...")
    print("   (This may take a few moments while we query APIs...)")
    
    # Generate recommendations
    try:
        recommendations = content_recommender.generate_feed(character, algorithm_weights, 15)
    except Exception as e:
        print(f"\n❌ Error generating recommendations: {e}")
        recommendations = []
    
    # Display results
    display_recommendations(recommendations)
    display_summary_stats(character, algorithm_weights, recommendations)
    
    # Interactive options
    while True:
        print("\n" + "-"*80)
        print("OPTIONS:")
        print("1. View detailed recommendations")
        print("2. Export results to file")
        print("3. Create new character")
        print("4. Exit")
        
        option = input("\nWhat would you like to do? (1-4): ").strip()
        
        if option == "1":
            display_detailed_recommendations(recommendations)
        elif option == "2":
            export_results(character, algorithm_weights, recommendations)
        elif option == "3":
            return "restart"
        elif option == "4":
            return "exit"
        else:
            print("Invalid option. Please enter 1-4.")

def display_detailed_recommendations(recommendations: List[Recommendation]):
    """Display detailed view of recommendations"""
    if not recommendations:
        print("No recommendations to display.")
        return
    
    print("\n" + "="*80)
    print("DETAILED RECOMMENDATIONS VIEW")
    print("="*80)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n#{i}")
        print(f"Title: {rec.title}")
        print(f"Algorithm: {rec.algorithm}")
        print(f"Source: {rec.source}")
        print(f"Score: {rec.score:.3f}")
        if rec.description:
            print(f"Description: {rec.description}")
        if rec.published_at:
            print(f"Published: {rec.published_at}")
        if rec.url != "#":
            print(f"URL: {rec.url}")
        print("-" * 40)

def export_results(character: Character, weights: Dict[str, float], 
                  recommendations: List[Recommendation]):
    """Export results to a text file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recommendation_analysis_{character.name.replace(' ', '_')}_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("REVERSE-INFERENCE RECOMMENDATION SYSTEM ANALYSIS\n")
            f.write("=" * 80 + "\n\n")
            
            # Character profile
            f.write("CHARACTER PROFILE:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Name: {character.name}\n")
            f.write(f"Age: {character.age}\n")
            f.write(f"Gender: {character.gender}\n")
            f.write(f"Location: {character.location}\n")
            f.write(f"Occupation: {character.occupation}\n")
            f.write(f"Education: {character.education_level}\n")
            f.write(f"Interests: {', '.join(character.interests)}\n")
            f.write(f"Personality: {', '.join(character.personality_traits)}\n")
            f.write(f"Activity Level: {character.activity_level}\n")
            f.write(f"Tech Savviness: {character.tech_savviness}\n")
            f.write(f"Social Connectivity: {character.social_connectivity}%\n\n")
            
            # Algorithm weights
            f.write("ALGORITHM INFERENCE:\n")
            f.write("-" * 40 + "\n")
            sorted_algorithms = sorted(weights.items(), key=lambda x: x[1], reverse=True)
            for algo, weight in sorted_algorithms:
                f.write(f"{algo.replace('_', ' ').title()}: {weight:.1%}\n")
            f.write("\n")
            
            # Recommendations
            f.write("RECOMMENDATIONS:\n")
            f.write("-" * 40 + "\n")
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec.title}\n")
                f.write(f"   Algorithm: {rec.algorithm}\n")
                f.write(f"   Source: {rec.source}\n")
                f.write(f"   Score: {rec.score:.3f}\n")
                if rec.description:
                    f.write(f"   Description: {rec.description}\n")
                if rec.url != "#":
                    f.write(f"   URL: {rec.url}\n")
                f.write("\n")
        
        print(f"\n Results exported to: {filename}")
        
    except Exception as e:
        print(f"\n Error exporting results: {e}")

def main():
    """Main program entry point"""
    print(" Starting Reverse-Inference Recommendation System...")
    print("\n Note: For real content, add your NewsAPI key to the NEWS_API_KEY variable.")
    print("    Get a free key at: https://newsapi.org/register")
    print("    Without an API key, you'll see placeholder content for demonstration.")
    
    while True:
        choice = main_menu()
        
        if choice == "exit":
            break
        elif choice == "custom":
            character = InteractiveCharacterBuilder.get_user_input()
        elif choice == "demo":
            character = create_sample_character()
            print(f"\n Using demo character: {character.name}")
        
        result = run_recommendation_analysis(character, NEWS_API_KEY)
        
        if result == "exit":
            break
        # If result == "restart", the loop will continue

if __name__ == "__main__":
    main()
