"""User Preference Agent - Extracts and models user preferences"""
import config
import json
from openai import OpenAI
from pinecone import Pinecone
from models import UserProfile, TravelStyle
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import re


class UserPreferenceAgent:
    """Agent responsible for understanding user needs and building user profile"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.index = None
        self.pinecone_available = False
        try:
            self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
            self.index = self.pc.Index(config.PINECONE_INDEX_NAME)
            # Verify index is accessible
            stats = self.index.describe_index_stats()
            self.pinecone_available = True
            print(f"✓ Connected to Pinecone index: {config.PINECONE_INDEX_NAME}")
            print(f"  Index contains {stats.total_vector_count} vectors")
        except Exception as e:
            error_msg = str(e)
            if "NOT_FOUND" in error_msg or "404" in error_msg:
                print(f"⚠ Pinecone index '{config.PINECONE_INDEX_NAME}' not found.")
                print(f"  Run 'python populate_pinecone.py' to populate the index with sample data.")
            else:
                print(f"⚠ Could not connect to Pinecone index: {error_msg}")
            print("  Continuing without vector search enrichment...")
            self.index = None
    
    def extract_preferences(self, user_request: str) -> UserProfile:
        """
        Extract user preferences from natural language request
        
        Args:
            user_request: Natural language travel request
            
        Returns:
            UserProfile object with structured preferences
        """
        # Use GPT for entity extraction and reasoning
        extraction_prompt = f"""
        Extract the following information from this travel request:
        {user_request}
        
        Extract:
        1. Origin city
        2. Destination city
        3. Start date (format: YYYY-MM-DD)
        4. End date (format: YYYY-MM-DD)
        5. Budget amount (numeric value)
        6. Travel style (luxury, budget, moderate, adventure, relaxed)
        7. Explicit preferences mentioned
        8. Implicit preferences inferred
        
        Return a JSON object with these fields.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting travel preferences from natural language. Return only valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            extracted_data = json.loads(response.choices[0].message.content)
            
            # Handle different field name variations from GPT
            origin = extracted_data.get("origin") or extracted_data.get("origin_city", "")
            destination = extracted_data.get("destination") or extracted_data.get("destination_city", "")
            start_date = extracted_data.get("start_date", "")
            end_date = extracted_data.get("end_date", "")
            budget = float(extracted_data.get("budget") or extracted_data.get("budget_amount", 0))
            travel_style = extracted_data.get("travel_style", "moderate").lower()
            
            # Ensure implicit_preferences is a dict, not a list
            implicit_prefs = extracted_data.get("implicit_preferences", {})
            if isinstance(implicit_prefs, list):
                implicit_prefs = {}
            if not isinstance(implicit_prefs, dict):
                implicit_prefs = {}
            
            # Ensure explicit_constraints is a dict
            explicit_constraints = extracted_data.get("explicit_constraints", {})
            if not isinstance(explicit_constraints, dict):
                explicit_constraints = {}
            
            # Get preferences (could be in different fields)
            preferences = extracted_data.get("preferences", [])
            if not preferences and extracted_data.get("explicit_preferences"):
                preferences = extracted_data.get("explicit_preferences", [])
            
            # Build UserProfile
            profile = UserProfile(
                origin=origin,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                travel_style=TravelStyle(travel_style),
                preferences=preferences,
                explicit_constraints=explicit_constraints,
                implicit_preferences=implicit_prefs
            )
            
            # Validate dates are in the future
            self._validate_dates(profile)
            
            # Retrieve similar preferences from Pinecone
            self._enrich_with_embeddings(profile, user_request)
            
            return profile
            
        except ValueError as e:
            # Re-raise date validation errors
            raise e
        except Exception as e:
            print(f"Error in preference extraction: {e}")
            # Fallback to basic extraction
            profile = self._fallback_extraction(user_request)
            # Validate dates even for fallback
            self._validate_dates(profile)
            return profile
    
    def _enrich_with_embeddings(self, profile: UserProfile, user_request: str):
        """Enrich profile using vector embeddings from Pinecone"""
        if self.index is None:
            # Pinecone not available, skip enrichment
            return
            
        try:
            # Generate embedding for user request
            embedding_response = self.client.embeddings.create(
                model=config.EMBEDDING_MODEL,
                input=user_request
            )
            embedding = embedding_response.data[0].embedding
            
            # Query Pinecone for similar preferences
            results = self.index.query(
                vector=embedding,
                top_k=3,
                include_metadata=True
            )
            
            # Enrich profile with similar preferences if found
            if results.matches:
                print(f"Found {len(results.matches)} similar travel preferences from Pinecone")
                for match in results.matches:
                    if match.metadata:
                        # Merge similar preferences
                        if "preferences" in match.metadata:
                            new_prefs = match.metadata.get("preferences", [])
                            # Avoid duplicates
                            for pref in new_prefs:
                                if pref not in profile.preferences:
                                    profile.preferences.append(pref)
                        
                        # Enrich travel style if similar and not explicitly set
                        if match.metadata.get("travel_style") and not profile.travel_style:
                            try:
                                profile.travel_style = TravelStyle(match.metadata.get("travel_style"))
                            except:
                                pass
                        
                        # Add activities if available
                        if "activities" in match.metadata:
                            activities = match.metadata.get("activities", [])
                            if "activities" not in profile.implicit_preferences:
                                profile.implicit_preferences["activities"] = []
                            profile.implicit_preferences["activities"].extend(activities)
                            
        except Exception as e:
            print(f"Error enriching with embeddings: {e}")
            # Continue without enrichment
    
    def _validate_dates(self, profile: UserProfile):
        """
        Validate that travel dates are in the future (at least tomorrow)
        
        Args:
            profile: UserProfile with dates to validate
            
        Raises:
            ValueError: If dates are in the past or not at least tomorrow
        """
        if not profile.start_date:
            raise ValueError("Start date is required. Please provide a valid start date for your trip.")
        
        # Parse the start date
        start_date = self._parse_date_string(profile.start_date)
        if start_date is None:
            raise ValueError(f"Invalid start date format: {profile.start_date}. Please use format like 'May 28, 2025' or '2025-05-28'.")
        
        # Get tomorrow's date (at least one day in the future)
        tomorrow = datetime.now().date() + timedelta(days=1)
        
        # Check if start date is at least tomorrow
        if start_date < tomorrow:
            raise ValueError(
                f"Travel dates must be in the future. The start date ({profile.start_date}) is in the past or today. "
                f"Please provide dates starting from {tomorrow.strftime('%B %d, %Y')} or later."
            )
        
        # Validate end date if provided
        if profile.end_date:
            end_date = self._parse_date_string(profile.end_date)
            if end_date is None:
                raise ValueError(f"Invalid end date format: {profile.end_date}. Please use format like 'May 30, 2025' or '2025-05-30'.")
            
            if end_date < start_date:
                raise ValueError(
                    f"End date ({profile.end_date}) must be after start date ({profile.start_date}). "
                    "Please provide valid travel dates."
                )
    
    def _parse_date_string(self, date_str: str) -> Optional[datetime.date]:
        """
        Parse date string to date object, handling multiple formats
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            datetime.date object or None if parsing fails
        """
        if not date_str:
            return None
        
        # Remove ordinal suffixes (st, nd, rd, th)
        date_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        
        # Try multiple date formats
        date_formats = [
            "%Y-%m-%d",           # 2025-05-28
            "%B %d, %Y",          # May 28, 2025
            "%B %d %Y",           # May 28 2025
            "%m/%d/%Y",           # 05/28/2025
            "%d/%m/%Y",           # 28/05/2025
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_clean.strip(), fmt)
                return dt.date()
            except ValueError:
                continue
        
        return None
    
    def _fallback_extraction(self, user_request: str) -> UserProfile:
        """Fallback extraction using regex patterns"""
        # Extract dates (handles formats like "May 28th, 2025" or "May 28, 2025")
        date_pattern = r'(\w+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})'
        dates = re.findall(date_pattern, user_request)
        
        # Extract budget
        budget_pattern = r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        budget_matches = re.findall(budget_pattern, user_request)
        budget = float(budget_matches[-1].replace(',', '')) if budget_matches else 0
        
        # Extract origin and destination (improved pattern)
        origin = ""
        destination = ""
        user_lower = user_request.lower()
        
        # Better pattern: "from X to Y" - capture city names (words) until "to" or "for"
        pattern = r'from\s+([A-Za-z]+)\s+to\s+([A-Za-z]+)(?:\s+for|\s+|$)'
        match = re.search(pattern, user_lower)
        if match:
            origin = match.group(1).strip().title()
            destination = match.group(2).strip().title()
        else:
            # Fallback: try separate patterns with word boundaries
            from_match = re.search(r'from\s+([A-Za-z]+)\b', user_lower)
            to_match = re.search(r'to\s+([A-Za-z]+)\b', user_lower)
            if from_match:
                origin = from_match.group(1).strip().title()
            if to_match:
                destination = to_match.group(1).strip().title()
        
        return UserProfile(
            origin=origin,
            destination=destination,
            start_date=dates[0] if len(dates) > 0 else "",
            end_date=dates[1] if len(dates) > 1 else dates[0] if dates else "",
            budget=budget,
            travel_style=TravelStyle.MODERATE
        )

