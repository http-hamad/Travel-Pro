"""Itinerary Agent - Route optimization and activity scheduling"""
import config
from openai import OpenAI
from api_clients import POIDatabase
from models import UserProfile, Itinerary, DayPlan, BudgetBreakdown
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class ItineraryAgent:
    """Agent responsible for creating optimized travel itineraries"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.poi_db = POIDatabase()
    
    def propose_itinerary(
        self,
        profile: UserProfile,
        budget_breakdown: BudgetBreakdown,
        reoptimization_constraints: Optional[Dict[str, Any]] = None
    ) -> Itinerary:
        """
        Propose a travel itinerary
        
        Args:
            profile: User profile with preferences
            budget_breakdown: Budget constraints
            reoptimization_constraints: Constraints from budget validation failure
            
        Returns:
            Itinerary object with day-by-day plan
        """
        # Calculate number of days
        num_days = self._calculate_days(profile.start_date, profile.end_date)
        
        # Get POIs and restaurants for origin/destination
        destination_pois = self.poi_db.get_pois(profile.destination)
        destination_restaurants = self.poi_db.get_restaurants(profile.destination)
        origin_restaurants = self.poi_db.get_restaurants(profile.origin)
        
        # Apply reoptimization constraints if present
        if reoptimization_constraints:
            destination_pois, destination_restaurants = self._apply_reoptimization_constraints(
                destination_pois, destination_restaurants, reoptimization_constraints
            )
        
        # Track attractions already used to avoid duplicates
        used_attractions: set[str] = set()

        # Generate day plans
        days = []
        current_date = self._parse_date(profile.start_date)
        
        for day_num in range(1, num_days + 1):
            day_plan = self._create_day_plan(
                day_num=day_num,
                profile=profile,
                current_date=current_date,
                destination_restaurants=destination_restaurants,
                origin_restaurants=origin_restaurants,
                destination_pois=destination_pois,
                is_first_day=(day_num == 1),
                is_last_day=(day_num == num_days),
                used_attractions=used_attractions,
                budget_breakdown=budget_breakdown,
                num_days=num_days
            )
            days.append(day_plan)
            current_date += timedelta(days=1)
        
        # Calculate total estimated cost
        total_cost = self._calculate_itinerary_cost(days, budget_breakdown)
        
        itinerary = Itinerary(
            days=days,
            total_estimated_cost=total_cost,
            remaining_budget=profile.budget - total_cost
        )
        
        return itinerary
    
    def _create_day_plan(
        self,
        day_num: int,
        profile: UserProfile,
        current_date: datetime,
        destination_pois: List[Dict[str, Any]],
        destination_restaurants: List[Dict[str, Any]],
        origin_restaurants: List[Dict[str, Any]],
        is_first_day: bool,
        is_last_day: bool,
        used_attractions: set,
        budget_breakdown: BudgetBreakdown,
        num_days: int
    ) -> DayPlan:
        """Create a plan for a single day"""
        
        # Determine current city
        if is_first_day:
            current_city = f"from {profile.origin} to {profile.destination}"
        elif is_last_day:
            current_city = f"from {profile.destination} to {profile.origin}"
        else:
            current_city = profile.destination
        
        # Transportation
        transportation = "-"
        if is_first_day:
            transportation = self._format_transportation(
                provider="United",
                route=f"from {profile.origin} to {profile.destination}",
                departure_time="4:12 PM",
                arrival_time="6:20 PM"
            )
        elif is_last_day:
            transportation = self._format_transportation(
                provider="United",
                route=f"from {profile.destination} ({self._get_airport_code(profile.destination)}) to {profile.origin} ({self._get_airport_code(profile.origin)})",
                departure_time="11:12 AM",
                arrival_time="3:08 PM"
            )
        
        # Meals - select based on day type with daily variation
        if is_first_day:
            breakfast = self._select_restaurant(
                origin_restaurants, "breakfast", profile.travel_style, profile.origin, day_num, offset=0
            )
            lunch = self._select_restaurant(
                origin_restaurants, "lunch", profile.travel_style, profile.origin, day_num, offset=1
            )
            dinner = self._select_restaurant(
                destination_restaurants, "dinner", profile.travel_style, profile.destination, day_num, offset=2
            )
        elif is_last_day:
            breakfast = self._select_restaurant(
                destination_restaurants, "breakfast", profile.travel_style, profile.destination, day_num, offset=0
            )
            lunch = self._select_restaurant(
                destination_restaurants, "lunch", profile.travel_style, profile.destination, day_num, offset=1
            )
            dinner = "-"
        else:
            breakfast = self._select_restaurant(
                destination_restaurants, "breakfast", profile.travel_style, profile.destination, day_num, offset=0
            )
            lunch = self._select_restaurant(
                destination_restaurants, "lunch", profile.travel_style, profile.destination, day_num, offset=1
            )
            dinner = self._select_restaurant(
                destination_restaurants, "dinner", profile.travel_style, profile.destination, day_num, offset=2
            )

        # Attractions - provide recommendations for all days with variation
        # Avoid repeating attractions by filtering out previously used ones
        available_pois = [p for p in destination_pois if p["name"] not in used_attractions]

        if is_first_day:
            # Evening attractions after arrival
            selected_pois = self._select_attractions(available_pois, day_num, max_attractions=2)
            if selected_pois:
                attraction = "; ".join([f"{p['name']}, {p['location']}" for p in selected_pois])
            else:
                attraction = self._generate_attraction_recommendations(
                    profile.destination, profile.travel_style, day_num, used_attractions, max_attractions=2
                )
        elif is_last_day:
            # Morning attractions before departure
            selected_pois = self._select_attractions(available_pois, day_num, max_attractions=1)
            if selected_pois:
                attraction = f"{selected_pois[0]['name']}, {selected_pois[0]['location']}"
            else:
                attraction = self._generate_attraction_recommendations(
                    profile.destination, profile.travel_style, day_num, used_attractions, max_attractions=1
                )
        else:
            # Full day attractions
            selected_pois = self._select_attractions(available_pois, day_num, max_attractions=3)
            if selected_pois:
                attraction = "; ".join([f"{p['name']}, {p['location']}" for p in selected_pois])
            else:
                # Fallback: Use GPT to generate attraction recommendations
                attraction = self._generate_attraction_recommendations(
                    profile.destination, profile.travel_style, day_num, used_attractions, max_attractions=3
                )
        
        # Accommodation
        accommodation = "-"
        if not is_last_day:
            hotel_name = self._select_hotel(profile.destination, profile.travel_style)
            accommodation = f"{hotel_name} (Hotel), {profile.destination}"
        
        # Calculate daily cost
        daily_cost = self._calculate_daily_cost(
            day_num=day_num,
            profile=profile,
            transportation=transportation,
            breakfast=breakfast,
            lunch=lunch,
            dinner=dinner,
            attraction=attraction,
            accommodation=accommodation,
            is_first_day=is_first_day,
            is_last_day=is_last_day,
            budget_breakdown=budget_breakdown,
            num_days=num_days
        )
        
        return DayPlan(
            day=day_num,
            current_city=current_city,
            transportation=transportation,
            breakfast=breakfast,
            attraction=attraction,
            lunch=lunch,
            dinner=dinner,
            accommodation=accommodation,
            daily_cost=daily_cost
        )
    
    def _select_restaurant(
        self,
        restaurants: List[Dict[str, Any]],
        meal_type: str,
        travel_style,
        city: str,
        day_num: int,
        offset: int = 0
    ) -> str:
        """Select restaurants with day-based variation and GPT fallback"""
        # Filter by meal type
        filtered = [r for r in restaurants if r.get("type") == meal_type]
        
        if filtered:
            # Prioritize by travel style preference
            style_filtered = filtered
            if travel_style.value == "budget":
                style_filtered = [r for r in filtered if r.get("price_range") == "budget"] or filtered
            elif travel_style.value == "luxury":
                style_filtered = [r for r in filtered if r.get("price_range") == "luxury"] or filtered
            
            # Deterministic random selection based on day number
            seed = hash(f"{city}-{meal_type}-{travel_style.value}-{day_num}-{offset}")
            rand = random.Random(seed)
            selected = rand.choice(style_filtered)
            return f"{selected['name']}, {selected['location']}"
        else:
            # Fallback: Use GPT to generate restaurant recommendation
            return self._generate_restaurant_recommendation(city, meal_type, travel_style, day_num)
    
    def _generate_restaurant_recommendation(
        self,
        city: str,
        meal_type: str,
        travel_style,
        day_num: int
    ) -> str:
        """Generate restaurant recommendation using GPT when database is empty"""
        try:
            prompt = f"""
            Recommend a {meal_type} restaurant in {city} for a {travel_style.value} traveler.
            This is for day {day_num} of the trip, so provide variety if possible.
            Return only the restaurant name and city in the format: "Restaurant Name, {city}"
            Be specific and realistic. Return only the name and city, nothing else.
            """
            
            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a travel guide expert. Return only restaurant names in the requested format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=50
            )
            
            recommendation = response.choices[0].message.content.strip()
            # Keep only the first line/entry
            recommendation = recommendation.splitlines()[0].strip()
            if ";" in recommendation:
                recommendation = recommendation.split(";")[0].strip()
            # Ensure it includes the city
            if city.lower() not in recommendation.lower():
                recommendation = f"{recommendation}, {city}"
            
            return recommendation
        except Exception as e:
            print(f"Error generating restaurant recommendation: {e}")
            # Final fallback
            style_names = {
                "budget": "Budget",
                "moderate": "Moderate",
                "luxury": "Luxury"
            }
            return f"{style_names.get(travel_style.value, 'Local')} {meal_type.title()} Restaurant, {city}"
    
    def _select_attractions(
        self,
        pois: List[Dict[str, Any]],
        day_num: int,
        max_attractions: int = 3
    ) -> List[Dict[str, Any]]:
        """Select attractions for the day with deterministic randomness for variety"""
        if not pois:
            return []
        
        total = min(max_attractions, len(pois))
        # Deterministic sampling based on day number
        seed = hash(f"{day_num}-{len(pois)}-{max_attractions}")
        rand = random.Random(seed)
        if len(pois) <= total:
            return list(pois)
        indices = rand.sample(range(len(pois)), total)
        return [pois[i] for i in indices]
    
    def _generate_attraction_recommendations(
        self,
        city: str,
        travel_style,
        day_num: int,
        used_attractions: set,
        max_attractions: int = 3
    ) -> str:
        """Generate attraction recommendations using GPT when database is empty"""
        try:
            prompt = f"""
            Recommend {max_attractions} popular tourist attractions or points of interest in {city} 
            suitable for a {travel_style.value} travel style on day {day_num} of a trip.
            Return them in the format: "Attraction 1, {city}; Attraction 2, {city}; Attraction 3, {city}"
            Be specific with actual attraction names. Return only the attractions in the requested format, nothing else.
            """
            
            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a travel guide expert. Return only attraction names in the requested format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            recommendations = response.choices[0].message.content.strip()
            parts = []
            for raw_part in recommendations.replace("\n", ";").split(";"):
                cleaned = raw_part.strip(" -•\t\r")
                if cleaned:
                    if city.lower() not in cleaned.lower():
                        cleaned = f"{cleaned}, {city}"
                    parts.append(cleaned)
                if len(parts) >= max_attractions:
                    break
            if parts:
                recommendations = "; ".join(parts)
            # Ensure format is correct
            if not recommendations or recommendations == "-":
                # Final fallback
                style_attractions = {
                    "budget": ["City Park", "Local Market", "Free Museum"],
                    "moderate": ["Museum", "Historic Site", "City Center"],
                    "luxury": ["Premium Museum", "Exclusive Tour", "VIP Experience"]
                }
                attractions = style_attractions.get(travel_style.value, ["Museum", "Historic Site", "City Center"])
                recommendations = "; ".join([f"{attr}, {city}" for attr in attractions[:max_attractions]])
            
            return recommendations
        except Exception as e:
            print(f"Error generating attraction recommendations: {e}")
            # Final fallback
            return f"Popular Attractions, {city}; City Center, {city}; Local Museum, {city}"
    
    
    def _select_hotel(self, city: str, travel_style) -> str:
        """Select hotel based on city and travel style"""
        # In production, this would query hotel API
        # For now, return a sample hotel name
        hotels = {
            "chicago": {
                "budget": "Budget Inn Chicago",
                "moderate": "Hyatt Centric Chicago Magnificent Mile",
                "luxury": "The Langham Chicago"
            }
        }
        
        city_lower = city.lower()
        style = travel_style.value
        
        # Find matching city
        for city_key, city_hotels in hotels.items():
            if city_key in city_lower:
                return city_hotels.get(style, city_hotels.get("moderate", "Hotel"))
        
        return f"Hotel in {city}"
    
    def _format_transportation(
        self,
        provider: str,
        route: str,
        departure_time: str,
        arrival_time: str
    ) -> str:
        """Format transportation string"""
        return f"{provider}, {route}, Departure Time: {departure_time}, Arrival Time: {arrival_time}"
    
    def _get_airport_code(self, city: str) -> str:
        """Get airport code for city"""
        airport_map = {
            "sarasota": "SRQ",
            "chicago": "ORD",
            "new york": "JFK",
            "los angeles": "LAX",
        }
        
        city_lower = city.lower()
        for city_key, code in airport_map.items():
            if city_key in city_lower:
                return code
        
        return city.upper()[:3]
    
    def _calculate_days(self, start_date: str, end_date: str) -> int:
        """Calculate number of days"""
        try:
            start = self._parse_date(start_date)
            end = self._parse_date(end_date)
            return (end - start).days + 1
        except:
            return 3
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime"""
        import re
        
        # Remove ordinal suffixes (st, nd, rd, th)
        date_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        
        # Try multiple date formats
        date_formats = ["%B %d, %Y", "%B %d %Y", "%Y-%m-%d"]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_clean, fmt)
            except:
                continue
        
        # Fallback to current date
        return datetime.now()
    
    def _calculate_daily_cost(
        self,
        day_num: int,
        profile: UserProfile,
        transportation: str,
        breakfast: str,
        lunch: str,
        dinner: str,
        attraction: str,
        accommodation: str,
        is_first_day: bool,
        is_last_day: bool,
        budget_breakdown: BudgetBreakdown,
        num_days: int
    ) -> float:
        """Calculate cost for a single day"""
        daily_cost = 0.0
        
        # Meal costs based on travel style
        meal_costs = {
            "budget": {"breakfast": 10, "lunch": 15, "dinner": 20},
            "moderate": {"breakfast": 15, "lunch": 25, "dinner": 40},
            "luxury": {"breakfast": 30, "lunch": 50, "dinner": 100}
        }
        style = profile.travel_style.value
        costs = meal_costs.get(style, meal_costs["moderate"])
        
        # Breakfast cost
        if breakfast != "-":
            daily_cost += costs["breakfast"]
        
        # Lunch cost
        if lunch != "-":
            daily_cost += costs["lunch"]
        
        # Dinner cost
        if dinner != "-":
            daily_cost += costs["dinner"]
        
        # Attraction costs (count number of attractions)
        if attraction != "-":
            num_attractions = len(attraction.split(";"))
            daily_cost += 25 * num_attractions  # $25 per attraction
        
        # Accommodation cost (per night)
        if accommodation != "-":
            # Distribute hotel cost across nights
            nights = max(1, num_days - 1)
            if nights > 0:
                daily_cost += budget_breakdown.hotels / nights
        
        # Transportation cost (flights on first/last day)
        if transportation != "-" and (is_first_day or is_last_day):
            # Distribute flight cost between first and last day
            if is_first_day:
                daily_cost += budget_breakdown.flights / 2
            elif is_last_day:
                daily_cost += budget_breakdown.flights / 2
        
        # Local transport cost (every day except travel days)
        if not is_first_day and not is_last_day:
            daily_cost += 30  # Local transport per day
        
        return round(daily_cost, 2)
    
    def _calculate_itinerary_cost(
        self,
        days: List[DayPlan],
        budget_breakdown: BudgetBreakdown
    ) -> float:
        """Calculate total cost of itinerary by summing daily costs"""
        total = sum(day.daily_cost for day in days)
        return round(total, 2)
    
    def _apply_reoptimization_constraints(
        self,
        destination_pois: List[Dict[str, Any]],
        destination_restaurants: List[Dict[str, Any]],
        constraints: Dict[str, Any]
    ) -> tuple:
        """Apply constraints from budget validation"""
        # Reduce number of POIs if needed
        if "attractions" in constraints.get("suggestions", {}):
            destination_pois = destination_pois[:2]  # Reduce to key attractions
        
        # Filter restaurants by price range if meal reduction needed
        if "meals" in constraints.get("suggestions", {}):
            destination_restaurants = [
                r for r in destination_restaurants if r.get("price_range") in ["budget", "moderate"]
            ]
        
        return destination_pois, destination_restaurants

