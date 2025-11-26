"""Data models for Travel-Pro System"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TravelStyle(str, Enum):
    LUXURY = "luxury"
    BUDGET = "budget"
    MODERATE = "moderate"
    ADVENTURE = "adventure"
    RELAXED = "relaxed"


class UserProfile(BaseModel):
    """Structured user preference profile"""
    origin: str
    destination: str
    start_date: str
    end_date: str
    budget: float
    travel_style: Optional[TravelStyle] = TravelStyle.MODERATE
    preferences: List[str] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    explicit_constraints: Dict[str, Any] = Field(default_factory=dict)
    implicit_preferences: Dict[str, Any] = Field(default_factory=dict)


class Transportation(BaseModel):
    """Transportation details"""
    provider: str
    route: str
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    cost: Optional[float] = None


class DayPlan(BaseModel):
    """Plan for a single day"""
    day: int
    current_city: str
    transportation: str
    breakfast: str
    attraction: str
    lunch: str
    dinner: str
    accommodation: str
    daily_cost: float = 0.0  # Cost for this day


class Itinerary(BaseModel):
    """Complete travel itinerary"""
    days: List[DayPlan]
    total_estimated_cost: float = 0.0
    remaining_budget: float = 0.0


class BudgetBreakdown(BaseModel):
    """Detailed budget breakdown"""
    flights: float = 0.0
    hotels: float = 0.0
    meals: float = 0.0
    attractions: float = 0.0
    local_transport: float = 0.0
    total: float = 0.0


class SystemState(BaseModel):
    """Global state managed by Coordinator"""
    user_request: str
    user_profile: Optional[UserProfile] = None
    budget_breakdown: Optional[BudgetBreakdown] = None
    itinerary: Optional[Itinerary] = None
    reoptimization_count: int = 0
    status: str = "initialized"
    error: Optional[str] = None

