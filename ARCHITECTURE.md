# Travel-Pro Architecture Documentation

This document provides a comprehensive overview of the Travel-Pro Multi-Agent System architecture, design patterns, and implementation details.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Core Components](#core-components)
4. [Agent Architecture](#agent-architecture)
5. [Data Flow](#data-flow)
6. [State Management](#state-management)
7. [Orchestration Framework](#orchestration-framework)
8. [Data Models](#data-models)
9. [API Integrations](#api-integrations)
10. [Design Patterns](#design-patterns)
11. [Error Handling](#error-handling)
12. [Performance Considerations](#performance-considerations)
13. [Scalability](#scalability)

## System Overview

Travel-Pro is a Multi-Agent System (MAS) that employs a decentralized, modular architecture. The system consists of four primary agents that collaborate through a central coordinator to generate personalized travel itineraries.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (Terminal)                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Coordinator Agent                        │
│              (LangGraph Orchestration)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Global State Management                 │   │
│  └──────────────────────────────────────────────────────┘   │
└───────┬──────────────┬──────────────┬───────────────────────┘
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   User       │ │   Budget     │ │  Itinerary   │
│ Preference   │ │    Agent     │ │    Agent     │
│   Agent      │ │              │ │              │
└──────┬─────-─┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   OpenAI     │ │  RapidAPI    │ │    POI       │
│   GPT-4      │ │  (Booking)   │ │  Database    │
│              │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
       │
       ▼
┌──────────────┐
│   Pinecone   │
│  Vector DB   │
└──────────────┘
```

## Architecture Principles

### 1. Modularity

Each agent is an independent module with:
- **Clear Responsibilities**: Single, well-defined purpose
- **Loose Coupling**: Minimal dependencies on other agents
- **High Cohesion**: Related functionality grouped together
- **Interface-Based Design**: Communication through well-defined interfaces

### 2. Decentralization

- **Autonomous Agents**: Each agent makes independent decisions
- **No Central Authority**: Coordinator orchestrates but doesn't control
- **Distributed Processing**: Agents can operate in parallel
- **Fault Tolerance**: Failure of one agent doesn't crash the system

### 3. State-Driven Workflow

- **Explicit State**: All state managed through LangGraph
- **Immutable Updates**: State updates create new state objects
- **Traceability**: Complete state history for debugging
- **Reversibility**: Can rollback to previous states if needed

### 4. Extensibility

- **Plugin Architecture**: Easy to add new agents
- **Configurable**: Behavior controlled through configuration
- **API Abstraction**: External services abstracted behind interfaces

## Core Components

### 1. Coordinator Agent

**Location**: `coordinator.py`

**Responsibilities**:
- Orchestrates agent workflow using LangGraph
- Manages global state transitions
- Handles error propagation
- Coordinates re-optimization loops
- Formats final output

**Key Methods**:
- `process_request()`: Main entry point
- `_build_graph()`: Constructs LangGraph workflow
- `_extract_preferences_node()`: Routes to Preference Agent
- `_fetch_baseline_costs_node()`: Routes to Budget Agent
- `_propose_itinerary_node()`: Routes to Itinerary Agent
- `_validate_budget_node()`: Validates budget constraints
- `_should_reoptimize()`: Decision logic for re-optimization

**State Management**:
```python
class GraphState(TypedDict):
    user_request: str
    user_profile: UserProfile | None
    budget_breakdown: BudgetBreakdown | None
    itinerary: Itinerary | None
    reoptimization_count: int
    status: str
    error: str | None
    reoptimization_constraints: dict | None
```

### 2. User Preference Agent

**Location**: `agents/user_preference_agent.py`

**Responsibilities**:
- Extracts preferences from natural language
- Validates travel dates
- Enriches profile with vector embeddings
- Handles fallback extraction

**Key Methods**:
- `extract_preferences()`: Main extraction method
- `_enrich_with_embeddings()`: Pinecone vector search
- `_validate_dates()`: Date validation logic
- `_fallback_extraction()`: Regex-based fallback

**Integration Points**:
- **OpenAI GPT-4o-mini**: Entity extraction and reasoning
- **OpenAI Embeddings**: Vector generation
- **Pinecone**: Semantic preference matching

**Data Flow**:
```
User Request → GPT Extraction → Date Validation → 
Pinecone Enrichment → UserProfile Object
```

### 3. Budget Agent

**Location**: `agents/budget_agent.py`

**Responsibilities**:
- Fetches real-time flight/hotel prices
- Estimates variable costs (meals, attractions, transport)
- Validates itinerary against budget
- Generates cost reduction suggestions

**Key Methods**:
- `fetch_baseline_costs()`: Gets initial cost estimates
- `validate_itinerary()`: Validates budget constraints
- `_get_flight_prices()`: Flight API integration
- `_get_hotel_prices()`: Hotel API integration
- `_estimate_meal_costs()`: Meal cost calculation
- `_generate_cost_reduction_suggestions()`: Re-optimization hints

**Cost Models**:
- **Meals**: Style-based pricing (budget/moderate/luxury)
- **Attractions**: Fixed $25 per attraction
- **Local Transport**: $30 per day
- **Flights**: Real-time API or fallback estimation
- **Hotels**: Real-time API or style-based estimation

### 4. Itinerary Agent

**Location**: `agents/itinerary_agent.py`

**Responsibilities**:
- Generates day-by-day itinerary
- Selects POIs and restaurants
- Schedules activities
- Calculates daily costs

**Key Methods**:
- `propose_itinerary()`: Main itinerary generation
- `_create_day_plan()`: Creates plan for single day
- `_select_restaurants()`: Restaurant selection logic
- `_select_attractions()`: POI selection logic
- `_calculate_daily_cost()`: Daily cost calculation
- `_apply_reoptimization_constraints()`: Applies budget constraints

**Integration Points**:
- **POI Database**: Points of interest lookup
- **Restaurant Database**: Dining recommendations
- **Budget Agent**: Cost information

## Agent Architecture

### Agent Design Pattern

All agents follow a consistent design pattern:

```python
class Agent:
    def __init__(self):
        # Initialize dependencies
        # Set up API clients
        # Configure models
        
    def process(self, input_data):
        # Main processing method
        # Returns structured output
        # Handles errors gracefully
```

### Communication Pattern

Agents communicate through:
1. **State Objects**: Shared state in LangGraph
2. **Return Values**: Structured data models
3. **Error Propagation**: Exceptions caught and logged

### Error Handling Strategy

Each agent implements:
- **Try-Except Blocks**: Catch and handle errors
- **Fallback Mechanisms**: Graceful degradation
- **Error Logging**: Detailed error information
- **State Updates**: Update state with error information

## Data Flow

### Complete Request Lifecycle

```
1. User Input (Terminal)
   │
   ▼
2. Coordinator.process_request()
   │
   ▼
3. LangGraph State Initialization
   │
   ├─► extract_preferences Node
   │   │
   │   ├─► User Preference Agent
   │   │   ├─► GPT-4 Extraction
   │   │   ├─► Date Validation
   │   │   └─► Pinecone Enrichment
   │   │
   │   └─► UserProfile Object
   │
   ├─► fetch_baseline_costs Node
   │   │
   │   ├─► Budget Agent
   │   │   ├─► Flight API Call
   │   │   ├─► Hotel API Call
   │   │   └─► Cost Estimation
   │   │
   │   └─► BudgetBreakdown Object
   │
   ├─► propose_itinerary Node
   │   │
   │   ├─► Itinerary Agent
   │   │   ├─► POI Selection
   │   │   ├─► Restaurant Selection
   │   │   ├─► Day Plan Creation
   │   │   └─► Cost Calculation
   │   │
   │   └─► Itinerary Object
   │
   ├─► validate_budget Node
   │   │
   │   ├─► Budget Agent Validation
   │   │
   │   └─► Validation Result
   │       │
   │       ├─► Valid → Finalize
   │       └─► Invalid → Re-optimize (up to 3 times)
   │
   └─► Finalize Node
       │
       ├─► Format Output
       ├─► Save to Logs
       └─► Return JSON
```

### Parallel Execution

Some operations can run in parallel:
- Preference extraction and baseline cost fetching (after date validation)
- Multiple API calls within Budget Agent
- POI and restaurant lookups

### Sequential Dependencies

Certain operations must be sequential:
1. Date validation before preference extraction
2. Preference extraction before itinerary generation
3. Itinerary generation before budget validation
4. Budget validation before finalization

## State Management

### LangGraph State

The system uses LangGraph's state management:

**State Structure**:
```python
GraphState = {
    "user_request": str,              # Original request
    "user_profile": UserProfile,      # Extracted preferences
    "budget_breakdown": BudgetBreakdown,  # Cost estimates
    "itinerary": Itinerary,           # Generated plan
    "reoptimization_count": int,      # Re-opt attempts
    "status": str,                     # Current status
    "error": str | None,              # Error message
    "reoptimization_constraints": dict  # Re-opt hints
}
```

### State Transitions

```
initialized → extracting_preferences → preferences_extracted →
fetching_costs → costs_fetched → proposing_itinerary →
itinerary_proposed → validating_budget → 
  ├─► budget_validated → completed
  └─► budget_exceeded → proposing_itinerary (re-optimize)
```

### State Immutability

- State updates create new state objects
- Previous states preserved in graph history
- Enables debugging and rollback

## Orchestration Framework

### LangGraph Workflow

**Graph Structure**:
```
Entry Point: extract_preferences
    │
    ├─► [Conditional] Date Validation Check
    │   ├─► continue → fetch_baseline_costs
    │   └─► error → finalize
    │
    ├─► fetch_baseline_costs
    │   │
    │   └─► propose_itinerary
    │       │
    │       └─► validate_budget
    │           │
    │           ├─► [Conditional] Re-optimization Check
    │           │   ├─► reoptimize → propose_itinerary
    │           │   └─► finalize → END
    │
    └─► finalize → END
```

### Conditional Edges

1. **Date Validation Check**: After preference extraction
   - Routes to error if dates invalid
   - Routes to continue if valid

2. **Re-optimization Check**: After budget validation
   - Routes to reoptimize if budget exceeded and attempts < 3
   - Routes to finalize otherwise

### Node Execution

Each node:
- Receives current state
- Performs agent operation
- Updates state
- Returns updated state

## Data Models

### Core Models

**UserProfile** (`models.py`):
```python
- origin: str
- destination: str
- start_date: str
- end_date: str
- budget: float
- travel_style: TravelStyle (enum)
- preferences: List[str]
- constraints: Dict[str, Any]
- explicit_constraints: Dict[str, Any]
- implicit_preferences: Dict[str, Any]
```

**BudgetBreakdown** (`models.py`):
```python
- flights: float
- hotels: float
- meals: float
- attractions: float
- local_transport: float
- total: float
```

**Itinerary** (`models.py`):
```python
- days: List[DayPlan]
- total_estimated_cost: float
- remaining_budget: float
```

**DayPlan** (`models.py`):
```python
- day: int
- current_city: str
- transportation: str
- breakfast: str
- attraction: str
- lunch: str
- dinner: str
- accommodation: str
- daily_cost: float
```

### Model Validation

All models use Pydantic for:
- Type validation
- Data coercion
- Schema validation
- Error messages

## API Integrations

### OpenAI Integration

**Services Used**:
1. **GPT-4o-mini**: Natural language understanding
2. **text-embedding-3-small**: Vector embeddings (1536 dims)

**Usage**:
- Preference extraction
- Entity recognition
- Semantic understanding
- Embedding generation

**Error Handling**:
- Fallback to regex extraction
- Graceful degradation
- Error logging

### Pinecone Integration

**Configuration**:
- Index: `travel-planner`
- Dimensions: 1536
- Metric: cosine
- Model: text-embedding-3-small

**Operations**:
- Vector upsert (data ingestion)
- Similarity search (preference matching)
- Metadata filtering

**Error Handling**:
- Continues without enrichment if unavailable
- Warning messages logged
- No system failure

### RapidAPI (Booking.com)

**Endpoints**:
- `/api/v1/flights/getMinPrice`: Flight pricing
- `/api/v1/hotels/searchHotels`: Hotel search
- `/api/v1/hotels/getHotelDetails`: Hotel details

**Error Handling**:
- Fallback cost estimation
- Timeout handling (10s)
- Error logging

## Design Patterns

### 1. Strategy Pattern

**Budget Agent Cost Models**:
- Different cost models for different travel styles
- Easily swappable strategies
- Extensible for new styles

### 2. Factory Pattern

**Agent Initialization**:
- Coordinator creates agents
- Centralized initialization
- Dependency injection

### 3. Observer Pattern

**State Updates**:
- LangGraph observes state changes
- Triggers next node execution
- Enables reactive workflow

### 4. Template Method Pattern

**Agent Processing**:
- Common processing structure
- Agent-specific implementations
- Consistent interface

### 5. Facade Pattern

**API Clients**:
- Simplified interface to complex APIs
- Abstraction layer
- Error handling centralization

## Error Handling

### Error Propagation

```
Agent Error → State Update → Coordinator → User
```

### Error Types

1. **Validation Errors**: Date validation, input validation
2. **API Errors**: Network issues, timeout, authentication
3. **Processing Errors**: Agent failures, data issues
4. **System Errors**: Unexpected exceptions

### Error Recovery

- **Fallback Mechanisms**: Alternative processing paths
- **Graceful Degradation**: Continue with reduced features
- **Retry Logic**: Automatic retries for transient errors
- **User Feedback**: Clear error messages

### Error Logging

- All errors logged to state
- Detailed error information
- Stack traces preserved
- Saved to log files and CSV (see [Logging Pipeline](#logging-pipeline))

## Logging Pipeline

Travel-Pro produces two complementary log types for every request:

1. **Structured JSON (`logs/YYYYMMDD_HHMMSS_mmm.json`)**
   - Contains timestamp, original query, and the full output payload (itinerary or error).
   - Used for reproducing complete responses and auditing agent behavior.

2. **Tabular CSV (`logs/trip_data.csv`)**
   - Schema: `timestamp, query, error, status, day, current_city, transportation, breakfast, attraction, lunch, dinner, accommodation, daily_cost, total_cost, remaining_budget`.
   - Error entries occupy a single row; successful itineraries add one row per day (with total/remaining budget on the final day row).
   - Enables downstream analytics in spreadsheets/BI tools.

Both logs are written atomically after each run by `utils.save_output_to_logs`, ensuring consistent observability and audit trails.

## Performance Considerations

### Optimization Strategies

1. **Parallel Processing**: Where possible, run operations in parallel
2. **Caching**: Cache API responses when appropriate
3. **Lazy Loading**: Load data only when needed
4. **Batch Operations**: Group similar operations

### Bottlenecks

1. **API Calls**: Network latency
   - Solution: Timeout handling, fallback estimates
2. **LLM Processing**: GPT API latency
   - Solution: Efficient prompts, response caching
3. **Vector Search**: Pinecone query time
   - Solution: Top-k limiting, index optimization

### Performance Metrics

- **End-to-End Latency**: ~10-30 seconds
- **API Call Time**: ~2-5 seconds per call
- **LLM Processing**: ~3-8 seconds
- **Vector Search**: ~0.5-1 second

## Scalability

### Horizontal Scaling

- **Stateless Agents**: Can run on multiple instances
- **API Rate Limits**: Distributed across instances
- **Load Balancing**: Coordinator can distribute load

### Vertical Scaling

- **Resource Optimization**: Efficient memory usage
- **Concurrent Processing**: Parallel agent execution
- **Caching**: Reduce redundant API calls

### Limitations

- **Single Coordinator**: Central bottleneck
- **State Management**: In-memory state (not distributed)
- **API Dependencies**: External service limits

### Future Improvements

- **Distributed State**: Redis or similar
- **Message Queue**: Async agent communication
- **Microservices**: Separate agent services
- **Caching Layer**: Redis for API responses

## Security Considerations

### API Key Management

- **Environment Variables**: Keys in .env file
- **Git Ignore**: Keys excluded from version control
- **Default Values**: Fallback for development

### Data Privacy

- **User Data**: Not stored permanently
- **Log Files**: Local storage only
- **API Data**: Transient, not cached

### Input Validation

- **Date Validation**: Prevents invalid dates
- **Type Checking**: Pydantic validation
- **Sanitization**: Input cleaning

## Testing Strategy

### Unit Testing

- Individual agent methods
- Data model validation
- Utility functions

### Integration Testing

- Agent interactions
- API integrations
- End-to-end workflows

### System Testing

- Complete request lifecycle
- Error scenarios
- Performance testing

## Deployment Considerations

### Environment Setup

- Python 3.8+ required
- Dependencies from requirements.txt
- API keys configured
- Pinecone index created

### Monitoring

- Log file analysis
- Error rate tracking
- Performance metrics
- API usage monitoring

### Maintenance

- Regular dependency updates
- API key rotation
- Pinecone index updates
- Log file cleanup

## Future Architecture Enhancements

### Planned Improvements

1. **Microservices Architecture**: Separate services per agent
2. **Event-Driven Architecture**: Message-based communication
3. **Distributed State**: Shared state management
4. **Caching Layer**: Redis for performance
5. **API Gateway**: Centralized API management
6. **Monitoring**: Prometheus/Grafana integration
7. **Containerization**: Docker deployment
8. **CI/CD Pipeline**: Automated testing and deployment

### Scalability Roadmap

1. **Phase 1**: Current monolithic architecture
2. **Phase 2**: Service separation
3. **Phase 3**: Distributed architecture
4. **Phase 4**: Cloud-native deployment

---

This architecture documentation provides a comprehensive view of the Travel-Pro system. For usage instructions, see [USAGE.md](USAGE.md).

