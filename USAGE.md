# Travel-Pro Usage Guide

This comprehensive guide covers all aspects of using the Travel-Pro Multi-Agent System, from basic usage to advanced features and troubleshooting.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Interactive Mode](#interactive-mode)
4. [Programmatic Usage](#programmatic-usage)
5. [Input Format](#input-format)
6. [Output Format](#output-format)
7. [Understanding Costs](#understanding-costs)
8. [Error Handling](#error-handling)
9. [Logging and Output Files](#logging-and-output-files)
10. [Advanced Features](#advanced-features)
11. [Examples](#examples)
12. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites Check

Before using Travel-Pro, ensure you have:

1. ✅ Python 3.8+ installed
2. ✅ All dependencies installed (`pip install -r requirements.txt`)
3. ✅ API keys configured (OpenAI, Pinecone, RapidAPI)
4. ✅ Pinecone index populated (`python populate_pinecone.py`)

### First Run

```bash
python main.py
```

You'll see the welcome screen and be prompted to enter your travel request.

## Basic Usage

### Interactive Terminal Mode

The simplest way to use Travel-Pro is through the interactive terminal:

```bash
python main.py
```

**Example Session:**

```
============================================================
Travel-Pro Multi-Agent System
============================================================

Please enter your travel request:
(Example: Please plan a trip from New York to Paris for 5 days,
 from December 1, 2025 to December 6, 2025. Budget: $3,000)

Enter your request (press Enter twice or Ctrl+D when done, 'quit' to exit):
------------------------------------------------------------
Please plan a trip from Miami to Los Angeles for 4 days, 
from December 15, 2025 to December 19, 2025. Budget: $2,500

============================================================
Processing your request...
============================================================
```

**Input Tips:**
- Type your request naturally in plain English
- Press Enter twice to submit (or Ctrl+D)
- Type `quit`, `exit`, or `q` to exit
- Use Ctrl+C to cancel

## Programmatic Usage

### Using the Coordinator Directly

For integration into other applications:

```python
from coordinator import Coordinator

# Initialize the coordinator
coordinator = Coordinator()

# Process a travel request
user_request = """
Please plan a trip for me starting from Sarasota to Chicago for 3 days, 
from December 24, 2025 to December 27, 2025. The budget for this trip is set at $1,900.
"""

result = coordinator.process_request(user_request)

# Check for errors
if "error" in result:
    print(f"Error: {result['error']}")
else:
    # Process the itinerary
    print(f"Total cost: ${result['total_cost']}")
    print(f"Remaining budget: ${result['remaining_budget']}")
    for day in result['days']:
        print(f"Day {day['day']}: {day['current_city']} - ${day['daily_cost']}")
```

### Batch Processing

Process multiple requests:

```python
from coordinator import Coordinator

coordinator = Coordinator()

requests = [
    "Plan a trip from New York to Paris for 5 days, from December 1, 2025 to December 6, 2025. Budget: $3,000",
    "Plan a budget trip from Miami to Orlando for 2 days, from January 10, 2026 to January 12, 2026. Budget: $500",
]

for request in requests:
    result = coordinator.process_request(request)
    # Process each result
    print(f"Request processed: {result.get('total_cost', 'Error')}")
```

## Input Format

### Required Information

Your travel request should include:

1. **Origin City**: Where the trip starts
2. **Destination City**: Where you're traveling to
3. **Travel Dates**: Start and end dates (must be in the future)
4. **Budget**: Total budget for the trip

### Date Formats

The system accepts various date formats:

- ✅ "December 1, 2025"
- ✅ "December 1st, 2025"
- ✅ "Dec 1, 2025"
- ✅ "2025-12-01"

**Important**: Dates must be at least tomorrow (not today or in the past).

### Budget Formats

- ✅ "$1,900"
- ✅ "$1900"
- ✅ "1900"
- ✅ "1,900 dollars"

### Example Requests

**Simple Request:**
```
Please plan a trip from New York to Paris for 5 days, 
from December 1, 2025 to December 6, 2025. Budget: $3,000.
```

**Detailed Request:**
```
I want a luxury beach vacation from Miami to the Caribbean. 
Travel dates: December 15, 2025 to December 22, 2025 (7 days).
My budget is $5,000. I prefer fine dining and spa services.
```

**Budget-Conscious Request:**
```
Plan a budget-friendly trip from Chicago to New York for 3 days,
from January 10, 2026 to January 13, 2026. 
Maximum budget: $800. Focus on affordable options.
```

## Output Format

### Successful Response Structure

```json
{
  "days": [
    {
      "day": 1,
      "current_city": "from Sarasota to Chicago",
      "transportation": "United, from Sarasota to Chicago, Departure Time: 4:12 PM, Arrival Time: 6:20 PM",
      "breakfast": "-",
      "attraction": "-",
      "lunch": "-",
      "dinner": "Portillo's, Chicago",
      "accommodation": "Hyatt Centric Chicago Magnificent Mile (Hotel), Chicago",
      "daily_cost": 340.0
    },
    {
      "day": 2,
      "current_city": "Chicago",
      "transportation": "-",
      "breakfast": "Lou Mitchell's, Chicago",
      "attraction": "Millennium Park, Chicago; Cloud Gate (The Bean), Chicago; Art Institute of Chicago, Chicago",
      "lunch": "Seoul Taco, Chicago",
      "dinner": "Portillo's, Chicago",
      "accommodation": "Hyatt Centric Chicago Magnificent Mile (Hotel), Chicago",
      "daily_cost": 335.0
    }
  ],
  "total_cost": 1175.0,
  "remaining_budget": 725.0
}
```

### Error Response Structure

```json
{
  "error": "Date Validation Error: Travel dates must be in the future...",
  "status": "completed"
}
```

## Understanding Costs

### Daily Cost Breakdown

Each day's cost includes:

1. **Transportation** (on travel days only)
   - Flight costs split between first and last day
   - Example: $600 flight = $300 on Day 1, $300 on last day

2. **Meals** (based on travel style)
   - **Budget**: Breakfast $10, Lunch $15, Dinner $20
   - **Moderate**: Breakfast $15, Lunch $25, Dinner $40
   - **Luxury**: Breakfast $30, Lunch $50, Dinner $100

3. **Attractions**
   - $25 per attraction
   - Only counted on destination days (not travel days)

4. **Accommodation**
   - Hotel costs distributed evenly across nights
   - Example: $450 for 3 nights = $150 per night

5. **Local Transport**
   - $30 per day
   - Only on destination days (not travel days)

### Cost Calculation Example

**Day 1 (Travel Day):**
- Flight: $300 (half of $600)
- Dinner: $40 (moderate style)
- Hotel: $150 (1/3 of $450)
- **Total: $490**

**Day 2 (Destination Day):**
- Breakfast: $15
- Lunch: $25
- Dinner: $40
- 3 Attractions: $75 (3 × $25)
- Hotel: $150
- Local Transport: $30
- **Total: $335**

## Error Handling

### Common Errors and Solutions

#### 1. Date Validation Error

**Error Message:**
```
Date Validation Error: Travel dates must be in the future. 
The start date (2020-01-01) is in the past or today.
```

**Solution:**
- Ensure dates are at least tomorrow
- Check date format (use "Month Day, Year")
- Verify year is correct

#### 2. Missing Information

**Error Message:**
```
Error: No itinerary generated
```

**Solution:**
- Ensure your request includes origin, destination, dates, and budget
- Check that all required information is clearly stated

#### 3. API Connection Issues

**Warning:**
```
Warning: Could not connect to Pinecone index...
```

**Solution:**
- Run `python populate_pinecone.py` to create/verify index
- Check your Pinecone API key
- System will continue with reduced functionality

#### 4. Budget Exceeded

The system automatically re-optimizes if budget is exceeded. You'll see:
- Multiple optimization attempts
- Cost reduction suggestions
- Final optimized itinerary

## Logging and Output Files

### Automatic Logging

All outputs are automatically saved to the `logs/` folder:

**File Naming:**
- Format: `YYYYMMDD_HHMMSS_mmm.json`
- Example: `20251124_004134_480.json`
- Includes milliseconds for uniqueness

**File Structure:**
```json
{
  "timestamp": "2025-11-24T00:41:34.480121",
  "query": "Original user request...",
  "output": {
    // Complete output (itinerary or error)
  }
}
```

### Accessing Logs

```bash
# List all log files
ls -la logs/

# View latest log
cat logs/$(ls -t logs/*.json | head -1)

# Search logs for specific queries
grep -r "Chicago" logs/

# Parse logs with Python
python -c "
import json
import glob
for file in sorted(glob.glob('logs/*.json')):
    with open(file) as f:
        data = json.load(f)
        print(f\"{data['timestamp']}: {data['query'][:50]}...\")
"
```

### CSV Log (`logs/trip_data.csv`)

In addition to JSON, each request is appended to `logs/trip_data.csv` with the schema:

```
timestamp,query,error,status,day,current_city,transportation,
breakfast,attraction,lunch,dinner,accommodation,daily_cost,
total_cost,remaining_budget
```

- Errors produce a single row with the error message.
- Successful itineraries write one row per day; the last row includes total/remaining budget.
- This file can be opened directly in Excel/Sheets for quick analysis.

## Advanced Features

### 1. Travel Style Preferences

The system automatically detects travel style from your request:

- **Luxury**: "luxury", "premium", "high-end", "5-star"
- **Budget**: "budget", "affordable", "cheap", "economy"
- **Moderate**: Default if not specified
- **Adventure**: "adventure", "outdoor", "hiking"
- **Relaxed**: "relaxing", "spa", "wellness"

### 2. Preference Enrichment

The system uses Pinecone to find similar travel preferences:

- Matches your request with historical preferences
- Enriches your profile with implicit preferences
- Improves personalization based on similar trips

### 3. Budget Re-optimization

If initial itinerary exceeds budget:

1. System identifies cost overruns
2. Generates reduction suggestions
3. Re-optimizes itinerary (up to 3 attempts)
4. Returns optimized plan within budget

### 4. Date Validation

Automatic validation ensures:
- Dates are in the future (at least tomorrow)
- End date is after start date
- Clear error messages if validation fails

## Examples

### Example 1: Simple City Trip

**Input:**
```
Please plan a trip from New York to Chicago for 3 days, 
from December 1, 2025 to December 4, 2025. Budget: $1,500.
```

**Output Highlights:**
- 3-day itinerary with flights
- Daily activities and meals
- Total cost: ~$1,200
- Remaining budget: ~$300

### Example 2: Luxury Vacation

**Input:**
```
I want a luxury beach vacation from Miami to the Caribbean for 7 days,
from December 15, 2025 to December 22, 2025. Budget: $5,000.
```

**Output Highlights:**
- Luxury accommodations
- Fine dining recommendations
- Premium activities
- Higher daily costs ($400-600/day)

### Example 3: Budget Trip

**Input:**
```
Plan a budget trip from Chicago to New York for 2 days,
from January 10, 2026 to January 12, 2026. Budget: $600.
```

**Output Highlights:**
- Budget-friendly hotels
- Affordable dining options
- Free/cheap attractions
- Lower daily costs ($200-300/day)

## Troubleshooting

### Issue: System Not Responding

**Symptoms:** No output after entering request

**Solutions:**
1. Check internet connection (required for APIs)
2. Verify API keys are correct
3. Check Python version: `python --version` (needs 3.8+)
4. Review error messages in terminal

### Issue: Incorrect Cost Estimates

**Symptoms:** Costs seem too high or too low

**Solutions:**
1. Check travel style (luxury vs budget)
2. Review number of attractions
3. Verify hotel costs from API
4. Check if flight API is responding

### Issue: Missing Attractions/Restaurants

**Symptoms:** Many "-" values in output

**Solutions:**
1. POI database may not have data for that city
2. System uses fallback when data unavailable
3. Check `api_clients.py` to add more cities

### Issue: Pinecone Warnings

**Symptoms:** "Warning: Could not connect to Pinecone index"

**Solutions:**
1. Run `python populate_pinecone.py`
2. Check Pinecone API key
3. Verify index name matches config
4. System works without Pinecone (reduced features)

## Best Practices

1. **Be Specific**: Include all details (dates, budget, preferences)
2. **Use Future Dates**: Always use dates at least tomorrow
3. **Clear Budget**: Specify budget clearly with dollar amount
4. **Review Outputs**: Check logs folder for all generated itineraries
5. **Iterate**: Try different requests to see how system adapts

## Performance Tips

1. **First Run**: May be slower due to API initialization
2. **Subsequent Runs**: Faster due to cached connections
3. **API Limits**: Be aware of API rate limits
4. **Batch Processing**: Process multiple requests sequentially

## Getting Help

If you encounter issues:

1. Check the error message in terminal
2. Review log files in `logs/` folder
3. Verify all prerequisites are met
4. Check API keys and configuration
5. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system details

---

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).

