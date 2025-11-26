# Travel-Pro Multi-Agent System

A sophisticated Multi-Agent System (MAS) that automates complex trip planning by integrating dynamic personalization with real-time budget accuracy. The system utilizes a modular architecture of autonomous agents that specialize in preference modeling, route optimization, and financial forecasting.

## 🎯 Overview

Travel-Pro is an intelligent travel planning system that transforms natural language travel requests into detailed, budget-optimized itineraries. Unlike traditional monolithic planners, Travel-Pro employs a decentralized multi-agent architecture where specialized agents collaborate to generate personalized travel plans.

### Key Capabilities

- **Natural Language Processing**: Understands complex travel requests in plain English
- **Intelligent Preference Extraction**: Extracts both explicit and implicit preferences using LLMs
- **Vector-Based Personalization**: Uses Pinecone vector database for semantic preference matching
- **Real-Time Cost Estimation**: Integrates with flight and hotel APIs for live pricing
- **Budget-Aware Planning**: Validates and optimizes itineraries against budget constraints
- **Automatic Re-optimization**: Iteratively refines plans when budget constraints are violated
- **Comprehensive Logging**: All outputs saved with timestamps for audit and analysis

## 🏗️ System Architecture

Travel-Pro implements a decentralized decision-making framework where agents operate asynchronously but coordinate towards a single goal: generating the user's optimal itinerary.

### Core Components

1. **Coordinator Agent (Orchestrator)**: Central controller using LangGraph to manage state and message passing between agents
2. **User Preference Agent**: Semantic understanding of user needs using GPT-4/3.5 and Pinecone vector embeddings
3. **Itinerary Agent**: Route optimization and activity scheduling with POI database integration
4. **Budget Agent**: Real-time cost estimation using API lookups and predictive ML models

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## ✨ Features

- **Dynamic Personalization**: Extracts explicit and implicit preferences from natural language
- **Real-time Pricing**: Integrates with flight and hotel APIs for live price data
- **Budget Validation**: Validates itineraries against budget constraints with automatic re-optimization
- **Iterative Refinement**: Supports feedback loops where budget validation can trigger itinerary re-optimization
- **Modular Architecture**: Each agent is independent, allowing for easy updates and maintenance
- **Date Validation**: Ensures all travel dates are in the future (at least tomorrow)
- **Cost Tracking**: Detailed daily cost breakdown and total trip cost calculation
- **Comprehensive Logging**: All requests and outputs saved with timestamps

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **OpenAI API Key**: For GPT models and embeddings
- **Pinecone API Key**: For vector database operations
- **RapidAPI Key**: For Booking.com flights/hotels APIs
- **Internet Connection**: Required for API calls

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd "AgenticAI Project cursor"

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file (or use the default values in `config.py`):

```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=travel-planner
PINECONE_HOST=your_pinecone_host
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST=booking-com15.p.rapidapi.com
```

### 3. Initialize Pinecone

Populate Pinecone with sample travel preferences:

```bash
python populate_pinecone.py
```

This will:
- Create the Pinecone index if it doesn't exist
- Generate embeddings for 12 sample travel preferences
- Verify the ingestion pipeline

### 4. Run the System

```bash
python main.py
```

The system will prompt you to enter your travel request interactively.

## 📖 Documentation

- **[USAGE.md](USAGE.md)**: Comprehensive usage guide with examples
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed system architecture and design

## 📊 Output Format

The system returns a JSON structure with day-by-day itinerary:

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
    }
  ],
  "total_cost": 1175.0,
  "remaining_budget": 725.0
}
```

### Cost Breakdown

Each day includes a `daily_cost` field that calculates:
- **Transportation**: Flight costs (distributed on first/last day)
- **Meals**: Breakfast, lunch, and dinner costs based on travel style
  - Budget: $10/$15/$20
  - Moderate: $15/$25/$40
  - Luxury: $30/$50/$100
- **Attractions**: $25 per attraction visited
- **Accommodation**: Hotel costs distributed across nights
- **Local Transport**: $30 per day for local transportation

## 🔧 Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Orchestration | LangGraph | Agent workflow and state management |
| LLM Backend | OpenAI GPT-4o-mini | Natural language understanding |
| Embeddings | text-embedding-3-small | Vector embeddings (1536 dimensions) |
| Vector Database | Pinecone | Semantic preference matching |
| Backend Language | Python 3.8+ | Core implementation |
| Flight/Hotel APIs | RapidAPI (Booking.com) | Real-time pricing |
| Data Models | Pydantic | Type-safe data structures |
| Logging | JSON files | Output persistence |

## 📁 Project Structure

```
.
├── agents/                    # Agent implementations
│   ├── __init__.py
│   ├── user_preference_agent.py   # Preference extraction and enrichment
│   ├── budget_agent.py            # Cost estimation and validation
│   └── itinerary_agent.py         # Itinerary generation
├── coordinator.py            # LangGraph orchestration
├── models.py                 # Pydantic data models
├── api_clients.py           # External API integrations
├── config.py                # Configuration management
├── utils.py                 # Utility functions (logging)
├── main.py                  # Entry point
├── populate_pinecone.py     # Pinecone data ingestion
├── example.py              # Usage examples
├── requirements.txt        # Python dependencies
├── logs/                   # Output logs (auto-generated)
│   └── .gitkeep
├── README.md               # This file
├── USAGE.md                # Detailed usage guide
└── ARCHITECTURE.md         # Architecture documentation
```

## 🔄 System Workflow

1. **Input Parsing**: User provides natural language travel request via terminal
2. **Date Validation**: System validates dates are in the future
3. **State Initialization**: Coordinator initializes LangGraph state
4. **Preference Extraction**: User Preference Agent extracts and enriches profile
5. **Cost Estimation**: Budget Agent fetches baseline costs from APIs
6. **Itinerary Generation**: Itinerary Agent creates day-by-day plan
7. **Budget Validation**: Budget Agent validates against constraints
8. **Re-optimization**: If budget exceeded, system iteratively refines plan
9. **Output Generation**: Final itinerary formatted as JSON
10. **Logging**: Output saved to logs folder with timestamp

## 📝 Logging

All outputs are automatically saved to the `logs/` folder in JSON format:

- **Filename Format**: `YYYYMMDD_HHMMSS_mmm.json` (e.g., `20251124_004134_480.json`)
- **Content**: Original query, timestamp, and complete output
- **Format**: Raw JSON for easy parsing and analysis

Both successful itineraries and error responses are logged for audit and debugging.

### CSV Log (`logs/trip_data.csv`)

Every run also appends structured rows to `logs/trip_data.csv` with the schema:

```
timestamp, query, error, status, day, current_city, transportation,
breakfast, attraction, lunch, dinner, accommodation, daily_cost,
total_cost, remaining_budget
```

- **Error rows** include timestamp, query, error, and status.
- **Success rows** include one entry per itinerary day; the final day row carries `total_cost` and `remaining_budget`.
- This CSV can be imported into spreadsheets or BI tools for downstream analysis.

## ⚙️ Configuration

### Pinecone Setup

- **Index Name**: `travel-planner`
- **Metric**: `cosine`
- **Dimensions**: `1536` (for `text-embedding-3-small` model)
- **Model**: `text-embedding-3-small`
- **Initial Data**: Run `python populate_pinecone.py` to populate with sample data

### RapidAPI (Booking.com)

The system uses Booking.com APIs for:
- Flight pricing: `/api/v1/flights/getMinPrice`
- Hotel search: `/api/v1/hotels/searchHotels`
- Hotel details: `/api/v1/hotels/getHotelDetails`

## 🧪 Testing

Test the system with various scenarios:

```bash
# Test with future dates
python main.py
# Enter: "Please plan a trip from New York to Paris for 5 days, from December 1, 2025 to December 6, 2025. Budget: $3,000"

# Test date validation (should error)
# Enter: "Please plan a trip from New York to Paris from January 1, 2020 to January 5, 2020. Budget: $2,000"
```

## 🐛 Troubleshooting

### Common Issues

1. **Pinecone Index Not Found**
   - Run `python populate_pinecone.py` to create and populate the index
   - Check your Pinecone API key in `config.py`

2. **Date Validation Errors**
   - Ensure dates are in the future (at least tomorrow)
   - Use format: "Month Day, Year" (e.g., "December 1, 2025")

3. **API Timeout Errors**
   - System will use fallback cost estimation
   - Check your internet connection and API keys

4. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Activate your conda environment if using one

## 🔮 Future Enhancements

- **Real POI Integration**: Replace mock database with real POI service
- **Comprehensive Airport Mapping**: Full airport code database
- **ML Cost Models**: Train regression models on historical pricing data
- **Geo-spatial Clustering**: Optimize routes using geographic clustering
- **Multi-city Support**: Plan trips with multiple destinations
- **Weather Integration**: Consider weather forecasts in planning
- **User History**: Learn from past user preferences

## 📄 License

This project is part of an academic research project on Multi-Agent Systems.

## 📚 Additional Resources

- [USAGE.md](USAGE.md) - Detailed usage guide with examples
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design patterns
- Technical Implementation Report (see project documentation)

## 🤝 Contributing

This is an academic research project. For questions or issues, please refer to the technical implementation report or contact the project maintainers.

---

**Travel-Pro Multi-Agent System** - Intelligent travel planning powered by multi-agent collaboration.
