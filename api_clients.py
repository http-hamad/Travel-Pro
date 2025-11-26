"""API clients for external services"""
import requests
import config
from typing import Dict, Any, Optional, List
from datetime import datetime


class FlightAPI:
    """Client for flight pricing API"""
    
    @staticmethod
    def get_min_price(
        from_id: str,
        to_id: str,
        depart_date: str,
        return_date: Optional[str] = None,
        cabin_class: str = "ECONOMY",
        currency_code: str = "USD"
    ) -> Dict[str, Any]:
        """
        Get minimum flight price
        
        Args:
            from_id: Origin airport code (e.g., "SRQ.AIRPORT")
            to_id: Destination airport code (e.g., "ORD.AIRPORT")
            depart_date: Departure date (YYYY-MM-DD)
            return_date: Return date (YYYY-MM-DD), optional
            cabin_class: Cabin class (ECONOMY, BUSINESS, FIRST)
            currency_code: Currency code (USD, EUR, etc.)
        """
        url = "https://booking-com15.p.rapidapi.com/api/v1/flights/getMinPrice"
        
        params = {
            "fromId": from_id,
            "toId": to_id,
            "departDate": depart_date,
            "cabinClass": cabin_class,
            "currency_code": currency_code
        }
        
        if return_date:
            params["returnDate"] = return_date
        
        headers = {
            "x-rapidapi-host": config.RAPIDAPI_HOST,
            "x-rapidapi-key": config.RAPIDAPI_KEY
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Flight API error: {e}")
            return {"price": None, "error": str(e)}


class HotelAPI:
    """Client for hotel pricing API"""
    
    @staticmethod
    def search_hotels(
        location: str,
        check_in: str,
        check_out: str,
        adults: int = 2,
        currency_code: str = "USD"
    ) -> Dict[str, Any]:
        """
        Search for hotels
        
        Args:
            location: City or location name
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            adults: Number of adults
            currency_code: Currency code
        """
        url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
        
        params = {
            "location": location,
            "checkin_date": check_in,
            "checkout_date": check_out,
            "adults": adults,
            "currency_code": currency_code
        }
        
        headers = {
            "x-rapidapi-host": config.RAPIDAPI_HOST,
            "x-rapidapi-key": config.RAPIDAPI_KEY
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Hotel API error: {e}")
            return {"hotels": [], "error": str(e)}
    
    @staticmethod
    def get_hotel_details(hotel_id: str, currency_code: str = "USD") -> Dict[str, Any]:
        """Get detailed hotel information including pricing"""
        url = f"https://booking-com15.p.rapidapi.com/api/v1/hotels/getHotelDetails"
        
        params = {
            "hotel_id": hotel_id,
            "currency_code": currency_code
        }
        
        headers = {
            "x-rapidapi-host": config.RAPIDAPI_HOST,
            "x-rapidapi-key": config.RAPIDAPI_KEY
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Hotel details API error: {e}")
            return {"error": str(e)}


class POIDatabase:
    """Mock POI database - in production, this would connect to a real POI service"""
    
    # Sample POI data - in production, this would be from a real database
    POI_DATABASE = {
        "Chicago": [
            {"name": "Millennium Park", "type": "park", "location": "Chicago", "visit_duration": 60},
            {"name": "Cloud Gate (The Bean)", "type": "sculpture", "location": "Chicago", "visit_duration": 30},
            {"name": "Art Institute of Chicago", "type": "museum", "location": "Chicago", "visit_duration": 120},
            {"name": "Navy Pier", "type": "entertainment", "location": "Chicago", "visit_duration": 90},
            {"name": "Willis Tower Skydeck", "type": "observation deck", "location": "Chicago", "visit_duration": 60},
            {"name": "Chicago Riverwalk", "type": "scenic walk", "location": "Chicago", "visit_duration": 75},
            {"name": "Museum of Science and Industry", "type": "museum", "location": "Chicago", "visit_duration": 120},
            {"name": "Field Museum", "type": "museum", "location": "Chicago", "visit_duration": 120},
            {"name": "Lincoln Park Zoo", "type": "zoo", "location": "Chicago", "visit_duration": 90},
            {"name": "Chicago Architecture Boat Tour", "type": "tour", "location": "Chicago River", "visit_duration": 75},
            {"name": "West Loop Art District", "type": "neighborhood", "location": "Chicago", "visit_duration": 90},
            {"name": "Hyde Park & University of Chicago", "type": "neighborhood", "location": "Chicago", "visit_duration": 120}
        ],
        "Sarasota": [
            {"name": "Ringling Museum", "type": "museum", "location": "Sarasota", "visit_duration": 90},
            {"name": "Siesta Key Beach", "type": "beach", "location": "Sarasota", "visit_duration": 120},
            {"name": "Marie Selby Botanical Gardens", "type": "garden", "location": "Sarasota", "visit_duration": 75},
            {"name": "Downtown Sarasota Farmers Market", "type": "market", "location": "Sarasota", "visit_duration": 60},
            {"name": "St. Armands Circle", "type": "shopping", "location": "Sarasota", "visit_duration": 90}
        ],
        "New York": [
            {"name": "Times Square", "type": "entertainment", "location": "New York", "visit_duration": 60},
            {"name": "Central Park", "type": "park", "location": "New York", "visit_duration": 120},
            {"name": "Metropolitan Museum of Art", "type": "museum", "location": "New York", "visit_duration": 150},
            {"name": "Statue of Liberty & Ellis Island", "type": "historic", "location": "New York Harbor", "visit_duration": 180},
            {"name": "Brooklyn Bridge Walk", "type": "scenic walk", "location": "New York", "visit_duration": 90},
            {"name": "High Line Park", "type": "park", "location": "New York", "visit_duration": 75},
            {"name": "Museum of Modern Art", "type": "museum", "location": "New York", "visit_duration": 120},
            {"name": "Broadway Show", "type": "theater", "location": "New York", "visit_duration": 150},
            {"name": "Chelsea Market Food Tour", "type": "food", "location": "New York", "visit_duration": 90},
            {"name": "One World Observatory", "type": "observation deck", "location": "New York", "visit_duration": 90}
        ],
        "Paris": [
            {"name": "Eiffel Tower", "type": "landmark", "location": "Paris", "visit_duration": 90},
            {"name": "Louvre Museum", "type": "museum", "location": "Paris", "visit_duration": 150},
            {"name": "Musée d'Orsay", "type": "museum", "location": "Paris", "visit_duration": 120},
            {"name": "Montmartre & Sacré-Cœur", "type": "neighborhood", "location": "Paris", "visit_duration": 120},
            {"name": "Seine River Cruise", "type": "tour", "location": "Paris", "visit_duration": 75},
            {"name": "Palace of Versailles", "type": "historic", "location": "Versailles", "visit_duration": 180},
            {"name": "Le Marais Food Walk", "type": "food", "location": "Paris", "visit_duration": 90},
            {"name": "Luxembourg Gardens", "type": "park", "location": "Paris", "visit_duration": 75},
            {"name": "Latin Quarter Walk", "type": "neighborhood", "location": "Paris", "visit_duration": 90},
            {"name": "Catacombs of Paris", "type": "historic", "location": "Paris", "visit_duration": 90}
        ]
    }
    
    RESTAURANTS = {
        "Chicago": [
            {"name": "Lou Mitchell's", "type": "breakfast", "location": "Chicago", "price_range": "moderate"},
            {"name": "Beatnik on the River", "type": "breakfast", "location": "Chicago", "price_range": "luxury"},
            {"name": "Wildberry Pancakes & Cafe", "type": "breakfast", "location": "Chicago", "price_range": "moderate"},
            {"name": "Portillo's", "type": "dinner", "location": "Chicago", "price_range": "budget"},
            {"name": "Girl & The Goat", "type": "dinner", "location": "Chicago", "price_range": "luxury"},
            {"name": "Au Cheval", "type": "lunch", "location": "Chicago", "price_range": "moderate"},
            {"name": "Xoco", "type": "lunch", "location": "Chicago", "price_range": "budget"},
            {"name": "RPM Italian", "type": "dinner", "location": "Chicago", "price_range": "luxury"},
            {"name": "The Purple Pig", "type": "lunch", "location": "Chicago", "price_range": "moderate"},
            {"name": "Parson's Chicken & Fish", "type": "dinner", "location": "Chicago", "price_range": "budget"},
            {"name": "Virtue Restaurant", "type": "dinner", "location": "Chicago", "price_range": "moderate"},
            {"name": "Sweet Greens Lincoln Park", "type": "lunch", "location": "Chicago", "price_range": "budget"}
        ],
        "Sarasota": [
            {"name": "The Breakfast House", "type": "breakfast", "location": "Sarasota", "price_range": "moderate"},
            {"name": "Station 400", "type": "breakfast", "location": "Sarasota", "price_range": "moderate"},
            {"name": "Shore Diner", "type": "lunch", "location": "Sarasota", "price_range": "moderate"},
            {"name": "Owen's Fish Camp", "type": "dinner", "location": "Sarasota", "price_range": "moderate"},
            {"name": "Indigenous", "type": "dinner", "location": "Sarasota", "price_range": "luxury"},
            {"name": "Yoder's Restaurant", "type": "lunch", "location": "Sarasota", "price_range": "budget"}
        ],
        "New York": [
            {"name": "Clinton St. Baking Company", "type": "breakfast", "location": "New York", "price_range": "moderate"},
            {"name": "Ess-a-Bagel", "type": "breakfast", "location": "New York", "price_range": "budget"},
            {"name": "Balthazar", "type": "breakfast", "location": "New York", "price_range": "luxury"},
            {"name": "Shake Shack", "type": "lunch", "location": "New York", "price_range": "budget"},
            {"name": "Joe's Pizza", "type": "lunch", "location": "New York", "price_range": "budget"},
            {"name": "Los Tacos No. 1", "type": "lunch", "location": "New York", "price_range": "moderate"},
            {"name": "Katz's Delicatessen", "type": "lunch", "location": "New York", "price_range": "budget"},
            {"name": "Le Bernardin", "type": "dinner", "location": "New York", "price_range": "luxury"},
            {"name": "Carbone", "type": "dinner", "location": "New York", "price_range": "luxury"},
            {"name": "Momofuku Noodle Bar", "type": "dinner", "location": "New York", "price_range": "moderate"}
        ],
        "Paris": [
            {"name": "Café de Flore", "type": "breakfast", "location": "Paris", "price_range": "luxury"},
            {"name": "Le Pain Quotidien", "type": "breakfast", "location": "Paris", "price_range": "moderate"},
            {"name": "Du Pain et des Idées", "type": "breakfast", "location": "Paris", "price_range": "moderate"},
            {"name": "Le Relais de l'Entrecôte", "type": "lunch", "location": "Paris", "price_range": "moderate"},
            {"name": "L'As du Fallafel", "type": "lunch", "location": "Paris", "price_range": "budget"},
            {"name": "Frenchie to Go", "type": "lunch", "location": "Paris", "price_range": "moderate"},
            {"name": "Le Comptoir de la Gastronomie", "type": "dinner", "location": "Paris", "price_range": "moderate"},
            {"name": "Septime", "type": "dinner", "location": "Paris", "price_range": "luxury"},
            {"name": "Chez Janou", "type": "dinner", "location": "Paris", "price_range": "moderate"},
            {"name": "Bistrot Paul Bert", "type": "dinner", "location": "Paris", "price_range": "moderate"}
        ]
    }
    
    @staticmethod
    def get_pois(city: str, limit: int | None = None) -> List[Dict[str, Any]]:
        """Get points of interest for a city"""
        pois = POIDatabase.POI_DATABASE.get(city, [])
        if limit is None:
            return pois
        return pois[:limit]
    
    @staticmethod
    def get_restaurants(city: str, meal_type: str = None) -> List[Dict[str, Any]]:
        """Get restaurants for a city, optionally filtered by meal type"""
        restaurants = POIDatabase.RESTAURANTS.get(city, [])
        if meal_type:
            return [r for r in restaurants if r["type"] == meal_type]
        return restaurants

