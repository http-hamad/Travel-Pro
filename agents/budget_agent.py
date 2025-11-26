"""Budget Agent - Real-time cost estimation and financial forecasting"""
import config
from api_clients import FlightAPI, HotelAPI
from models import BudgetBreakdown, UserProfile, Itinerary
from typing import Dict, Any, Optional


class BudgetAgent:
    """Agent responsible for cost estimation and budget validation"""
    
    def __init__(self):
        self.flight_api = FlightAPI()
        self.hotel_api = HotelAPI()
        # Simple regression model coefficients (would be trained on historical data)
        self.meal_cost_model = {
            "budget": {"breakfast": 10, "lunch": 15, "dinner": 20},
            "moderate": {"breakfast": 15, "lunch": 25, "dinner": 40},
            "luxury": {"breakfast": 30, "lunch": 50, "dinner": 100}
        }
        self.attraction_cost_estimate = 25  # Average per attraction
        self.local_transport_per_day = 30  # Average local transport cost
    
    def fetch_baseline_costs(self, profile: UserProfile) -> BudgetBreakdown:
        """
        Fetch baseline costs for flights and hotels
        
        Args:
            profile: UserProfile with travel details
            
        Returns:
            BudgetBreakdown with initial cost estimates
        """
        breakdown = BudgetBreakdown()
        
        # Get flight prices
        flight_data = self._get_flight_prices(profile)
        breakdown.flights = flight_data.get("price", 0) or self._estimate_flight_cost(profile)
        
        # Get hotel prices
        hotel_data = self._get_hotel_prices(profile)
        breakdown.hotels = hotel_data.get("price", 0) or self._estimate_hotel_cost(profile)
        
        # Estimate variable costs (meals, attractions, transport)
        num_days = self._calculate_days(profile.start_date, profile.end_date)
        breakdown.meals = self._estimate_meal_costs(profile, num_days)
        breakdown.attractions = self.attraction_cost_estimate * num_days
        breakdown.local_transport = self.local_transport_per_day * num_days
        
        breakdown.total = (
            breakdown.flights +
            breakdown.hotels +
            breakdown.meals +
            breakdown.attractions +
            breakdown.local_transport
        )
        
        return breakdown
    
    def validate_itinerary(self, itinerary: Itinerary, profile: UserProfile, 
                          budget_breakdown: BudgetBreakdown) -> Dict[str, Any]:
        """
        Validate if itinerary fits within budget
        
        Args:
            itinerary: Proposed itinerary
            profile: User profile with budget constraint
            budget_breakdown: Current budget breakdown
            
        Returns:
            Dict with validation result and re-optimization flag if needed
        """
        total_cost = itinerary.total_estimated_cost or budget_breakdown.total
        user_budget = profile.budget
        
        # Calculate with tolerance
        max_allowed = user_budget * (1 + config.BUDGET_TOLERANCE)
        
        if total_cost > max_allowed:
            # Calculate reduction needed
            reduction_percentage = ((total_cost - user_budget) / total_cost) * 100
            reduction_amount = total_cost - user_budget
            
            return {
                "valid": False,
                "reoptimization_needed": True,
                "current_cost": total_cost,
                "budget": user_budget,
                "excess": reduction_amount,
                "reduction_percentage": reduction_percentage,
                "suggestions": self._generate_cost_reduction_suggestions(
                    budget_breakdown, reduction_amount
                )
            }
        else:
            return {
                "valid": True,
                "reoptimization_needed": False,
                "current_cost": total_cost,
                "budget": user_budget,
                "remaining": user_budget - total_cost
            }
    
    def _get_flight_prices(self, profile: UserProfile) -> Dict[str, Any]:
        """Get real-time flight prices"""
        # Convert city names to airport codes (simplified - in production use a mapping service)
        airport_codes = self._city_to_airport_code(profile.origin, profile.destination)
        
        if not airport_codes:
            return {"price": None}
        
        from_code = airport_codes["origin"]
        to_code = airport_codes["destination"]
        
        # Format dates
        depart_date = self._format_date(profile.start_date)
        return_date = self._format_date(profile.end_date)
        
        result = self.flight_api.get_min_price(
            from_id=from_code,
            to_id=to_code,
            depart_date=depart_date,
            return_date=return_date
        )
        
        return result
    
    def _get_hotel_prices(self, profile: UserProfile) -> Dict[str, Any]:
        """Get real-time hotel prices"""
        check_in = self._format_date(profile.start_date)
        check_out = self._format_date(profile.end_date)
        
        result = self.hotel_api.search_hotels(
            location=profile.destination,
            check_in=check_in,
            check_out=check_out
        )
        
        # Extract minimum price from results
        if "hotels" in result and len(result["hotels"]) > 0:
            prices = [h.get("price", {}).get("amount", 0) for h in result["hotels"] if h.get("price")]
            if prices:
                return {"price": min(prices)}
        
        return {"price": None}
    
    def _estimate_flight_cost(self, profile: UserProfile) -> float:
        """Fallback flight cost estimation"""
        # Simple heuristic: $200-800 depending on distance and travel style
        base_cost = 300
        style_multiplier = {
            "budget": 0.8,
            "moderate": 1.0,
            "luxury": 1.5
        }.get(profile.travel_style.value, 1.0)
        
        return base_cost * style_multiplier
    
    def _estimate_hotel_cost(self, profile: UserProfile) -> float:
        """Estimate hotel cost per night"""
        num_days = self._calculate_days(profile.start_date, profile.end_date)
        nights = max(1, num_days - 1)
        
        cost_per_night = {
            "budget": 80,
            "moderate": 150,
            "luxury": 300
        }.get(profile.travel_style.value, 150)
        
        return cost_per_night * nights
    
    def _estimate_meal_costs(self, profile: UserProfile, num_days: int) -> float:
        """Estimate meal costs based on travel style"""
        style = profile.travel_style.value
        costs = self.meal_cost_model.get(style, self.meal_cost_model["moderate"])
        
        daily_meal_cost = costs["breakfast"] + costs["lunch"] + costs["dinner"]
        return daily_meal_cost * num_days
    
    def _calculate_days(self, start_date: str, end_date: str) -> int:
        """Calculate number of days between dates"""
        try:
            from datetime import datetime
            import re
            
            # Remove ordinal suffixes (st, nd, rd, th)
            start_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', start_date)
            end_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', end_date)
            
            # Try multiple date formats
            date_formats = ["%B %d, %Y", "%B %d %Y", "%Y-%m-%d"]
            
            start = None
            end = None
            
            for fmt in date_formats:
                try:
                    start = datetime.strptime(start_clean, fmt)
                    break
                except:
                    continue
            
            for fmt in date_formats:
                try:
                    end = datetime.strptime(end_clean, fmt)
                    break
                except:
                    continue
            
            if start and end:
                return (end - start).days + 1
        except Exception as e:
            print(f"Error calculating days: {e}")
        
        # Fallback
        return 3
    
    def _format_date(self, date_str: str) -> str:
        """Convert date string to YYYY-MM-DD format"""
        try:
            from datetime import datetime
            import re
            
            # Remove ordinal suffixes (st, nd, rd, th)
            date_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
            
            # Try multiple date formats
            date_formats = ["%B %d, %Y", "%B %d %Y", "%Y-%m-%d"]
            
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_clean, fmt)
                    return dt.strftime("%Y-%m-%d")
                except:
                    continue
        except Exception as e:
            print(f"Error formatting date: {e}")
        
        # Return as-is if parsing fails
        return date_str
    
    def _city_to_airport_code(self, origin: str, destination: str) -> Optional[Dict[str, str]]:
        """Convert city names to airport codes (simplified mapping)"""
        # In production, use a comprehensive airport code mapping service
        airport_map = {
            "sarasota": "SRQ.AIRPORT",
            "chicago": "ORD.AIRPORT",
            "new york": "JFK.AIRPORT",
            "los angeles": "LAX.AIRPORT",
            "miami": "MIA.AIRPORT",
        }
        
        origin_lower = origin.lower()
        dest_lower = destination.lower()
        
        origin_code = None
        dest_code = None
        
        for city, code in airport_map.items():
            if city in origin_lower:
                origin_code = code
            if city in dest_lower:
                dest_code = code
        
        if origin_code and dest_code:
            return {"origin": origin_code, "destination": dest_code}
        
        return None
    
    def _generate_cost_reduction_suggestions(self, breakdown: BudgetBreakdown, 
                                           reduction_needed: float) -> Dict[str, Any]:
        """Generate suggestions for cost reduction"""
        suggestions = {}
        
        # Suggest reducing hotel costs (largest variable)
        if breakdown.hotels > reduction_needed * 0.4:
            suggestions["hotels"] = {
                "current": breakdown.hotels,
                "suggested_reduction": reduction_needed * 0.4,
                "action": "Consider budget hotels or shorter stay"
            }
        
        # Suggest reducing meal costs
        if breakdown.meals > reduction_needed * 0.3:
            suggestions["meals"] = {
                "current": breakdown.meals,
                "suggested_reduction": reduction_needed * 0.3,
                "action": "Reduce dining costs by 20%"
            }
        
        # Suggest reducing attractions
        if breakdown.attractions > reduction_needed * 0.2:
            suggestions["attractions"] = {
                "current": breakdown.attractions,
                "suggested_reduction": reduction_needed * 0.2,
                "action": "Reduce number of paid attractions"
            }
        
        return suggestions

