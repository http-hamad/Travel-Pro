"""Example usage of Travel-Pro System"""
from coordinator import Coordinator
import json


def example_1():
    """Example 1: Basic trip planning"""
    print("=" * 60)
    print("Example 1: Basic Trip Planning")
    print("=" * 60)
    print()
    
    coordinator = Coordinator()
    
    user_request = """
    Please plan a trip for me starting from Sarasota to Chicago for 3 days, 
    from May 28th to May 30th, 2025. The budget for this trip is set at $1,900.
    """
    
    print(f"Request: {user_request.strip()}")
    print()
    print("Processing...")
    print()
    
    result = coordinator.process_request(user_request)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("Generated Itinerary:")
        print(json.dumps(result, indent=2))
    print()


def example_2():
    """Example 2: Custom request"""
    print("=" * 60)
    print("Example 2: Custom Request")
    print("=" * 60)
    print()
    
    coordinator = Coordinator()
    
    user_request = input("Enter your travel request: ")
    print()
    print("Processing...")
    print()
    
    result = coordinator.process_request(user_request)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("Generated Itinerary:")
        print(json.dumps(result, indent=2))
    print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        example_2()
    else:
        example_1()

