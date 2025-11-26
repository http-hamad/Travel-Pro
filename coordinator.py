"""Coordinator Agent - Orchestrates the multi-agent system using LangGraph"""
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from models import UserProfile, BudgetBreakdown, Itinerary
from agents import UserPreferenceAgent, BudgetAgent, ItineraryAgent
from utils import save_output_to_logs
import json


class GraphState(TypedDict):
    """State managed by LangGraph"""
    user_request: str
    user_profile: Annotated[UserProfile | None, "User profile extracted from request"]
    budget_breakdown: Annotated[BudgetBreakdown | None, "Budget breakdown with costs"]
    itinerary: Annotated[Itinerary | None, "Proposed itinerary"]
    reoptimization_count: Annotated[int, "Number of reoptimization attempts"]
    status: Annotated[str, "Current status of the system"]
    error: Annotated[str | None, "Error message if any"]
    reoptimization_constraints: Annotated[dict | None, "Constraints for reoptimization"]


class Coordinator:
    """Central orchestrator for the Travel-Pro multi-agent system"""
    
    def __init__(self):
        self.preference_agent = UserPreferenceAgent()
        self.budget_agent = BudgetAgent()
        self.itinerary_agent = ItineraryAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("extract_preferences", self._extract_preferences_node)
        workflow.add_node("fetch_baseline_costs", self._fetch_baseline_costs_node)
        workflow.add_node("propose_itinerary", self._propose_itinerary_node)
        workflow.add_node("validate_budget", self._validate_budget_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Define edges
        workflow.set_entry_point("extract_preferences")
        
        # Conditional edge after preference extraction to check for date validation errors
        workflow.add_conditional_edges(
            "extract_preferences",
            self._check_date_validation,
            {
                "continue": "fetch_baseline_costs",
                "error": "finalize"
            }
        )
        
        workflow.add_edge("fetch_baseline_costs", "propose_itinerary")
        workflow.add_edge("propose_itinerary", "validate_budget")
        
        # Conditional edge from validate_budget
        workflow.add_conditional_edges(
            "validate_budget",
            self._should_reoptimize,
            {
                "reoptimize": "propose_itinerary",
                "finalize": "finalize"
            }
        )
        
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _extract_preferences_node(self, state: GraphState) -> GraphState:
        """Extract user preferences"""
        try:
            state["status"] = "extracting_preferences"
            profile = self.preference_agent.extract_preferences(state["user_request"])
            state["user_profile"] = profile
            state["status"] = "preferences_extracted"
        except ValueError as e:
            # Date validation error - ask for a new query
            state["error"] = f"Date Validation Error: {str(e)}\n\nPlease provide a new travel request with dates in the future (at least tomorrow)."
            state["status"] = "date_validation_failed"
        except Exception as e:
            state["error"] = f"Error extracting preferences: {str(e)}"
            state["status"] = "error"
        return state
    
    def _fetch_baseline_costs_node(self, state: GraphState) -> GraphState:
        """Fetch baseline costs for flights and hotels"""
        try:
            if not state["user_profile"]:
                state["error"] = "User profile not available"
                state["status"] = "error"
                return state
            
            state["status"] = "fetching_costs"
            breakdown = self.budget_agent.fetch_baseline_costs(state["user_profile"])
            state["budget_breakdown"] = breakdown
            state["status"] = "costs_fetched"
        except Exception as e:
            state["error"] = f"Error fetching costs: {str(e)}"
            state["status"] = "error"
        return state
    
    def _propose_itinerary_node(self, state: GraphState) -> GraphState:
        """Propose itinerary"""
        try:
            if not state["user_profile"] or not state["budget_breakdown"]:
                state["error"] = "Missing required data for itinerary"
                state["status"] = "error"
                return state
            
            state["status"] = "proposing_itinerary"
            itinerary = self.itinerary_agent.propose_itinerary(
                profile=state["user_profile"],
                budget_breakdown=state["budget_breakdown"],
                reoptimization_constraints=state.get("reoptimization_constraints")
            )
            state["itinerary"] = itinerary
            state["status"] = "itinerary_proposed"
        except Exception as e:
            state["error"] = f"Error proposing itinerary: {str(e)}"
            state["status"] = "error"
        return state
    
    def _validate_budget_node(self, state: GraphState) -> GraphState:
        """Validate budget"""
        try:
            if not state["user_profile"] or not state["itinerary"] or not state["budget_breakdown"]:
                state["error"] = "Missing required data for validation"
                state["status"] = "error"
                return state
            
            state["status"] = "validating_budget"
            validation_result = self.budget_agent.validate_itinerary(
                itinerary=state["itinerary"],
                profile=state["user_profile"],
                budget_breakdown=state["budget_breakdown"]
            )
            
            if validation_result["valid"]:
                state["status"] = "budget_validated"
            else:
                state["status"] = "budget_exceeded"
                state["reoptimization_constraints"] = validation_result.get("suggestions", {})
                state["reoptimization_count"] = state.get("reoptimization_count", 0) + 1
        except Exception as e:
            state["error"] = f"Error validating budget: {str(e)}"
            state["status"] = "error"
        return state
    
    def _check_date_validation(self, state: GraphState) -> Literal["continue", "error"]:
        """Check if date validation passed"""
        if state.get("status") == "date_validation_failed" or state.get("error"):
            return "error"
        return "continue"
    
    def _should_reoptimize(self, state: GraphState) -> Literal["reoptimize", "finalize"]:
        """Determine if reoptimization is needed"""
        max_attempts = 3
        
        if state.get("status") == "budget_exceeded":
            if state.get("reoptimization_count", 0) < max_attempts:
                return "reoptimize"
        
        return "finalize"
    
    def _finalize_node(self, state: GraphState) -> GraphState:
        """Finalize the plan"""
        state["status"] = "completed"
        return state
    
    def process_request(self, user_request: str) -> dict:
        """
        Process a user travel request
        
        Args:
            user_request: Natural language travel request
            
        Returns:
            Final itinerary as JSON
        """
        initial_state: GraphState = {
            "user_request": user_request,
            "user_profile": None,
            "budget_breakdown": None,
            "itinerary": None,
            "reoptimization_count": 0,
            "status": "initialized",
            "error": None,
            "reoptimization_constraints": None
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Prepare output
        output = {}
        if final_state.get("error"):
            output = {
                "error": final_state["error"],
                "status": final_state["status"]
            }
        elif final_state.get("itinerary"):
            itinerary = final_state["itinerary"]
            output = self._format_output(itinerary)
        else:
            output = {
                "error": "No itinerary generated",
                "status": final_state["status"]
            }
        
        # Save output to logs
        try:
            log_filepath = save_output_to_logs(user_request, output)
            print(f"✓ Output saved to: {log_filepath}")
        except Exception as e:
            print(f"⚠ Warning: Could not save output to logs: {e}")
        
        return output
    
    def _format_output(self, itinerary: Itinerary) -> dict:
        """Format itinerary to match required JSON structure"""
        return {
            "days": [
                {
                    "day": day.day,
                    "current_city": day.current_city,
                    "transportation": day.transportation,
                    "breakfast": day.breakfast,
                    "attraction": day.attraction,
                    "lunch": day.lunch,
                    "dinner": day.dinner,
                    "accommodation": day.accommodation,
                    "daily_cost": day.daily_cost
                }
                for day in itinerary.days
            ],
            "total_cost": itinerary.total_estimated_cost,
            "remaining_budget": itinerary.remaining_budget
        }

