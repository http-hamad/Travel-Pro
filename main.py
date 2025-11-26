"""Main entry point for Travel-Pro System"""
from coordinator import Coordinator
import json
import sys


def get_user_input() -> str:
    """Get travel request from user via terminal"""
    print("=" * 60)
    print("Travel-Pro Multi-Agent System")
    print("=" * 60)
    # Instructions for the user
    print()
    print("Please enter your travel request:")
    print("(Example: Please plan a trip from New York to Paris for 5 days,")
    print(" from December 1, 2025 to December 6, 2025. Budget: $3,000)")
    print()
    print("Enter your request (press Enter twice or Ctrl+D when done, 'quit' to exit):")
    print("-" * 60)
    
    # Read multi-line input
    lines = []
    try:
        while True:
            try:
                line = input()
                if line.strip().lower() in ['quit', 'exit', 'q']:
                    print("Exiting...")
                    sys.exit(0)
                lines.append(line)
                # Allow user to finish with empty line (after at least one line)
                if not line.strip() and lines:
                    break
            except EOFError:
                # Ctrl+D pressed
                break
    except KeyboardInterrupt:
        # Ctrl+C pressed
        print("\nExiting...")
        sys.exit(0)
    
    user_request = "\n".join(lines).strip()
    
    if not user_request:
        print("Error: No request provided. Exiting...")
        sys.exit(1)
    
    return user_request


def main():
    """Main function to run Travel-Pro"""
    # Get user input from terminal
    user_request = get_user_input()
    
    print()
    print("=" * 60)
    print("Processing your request...")
    print("=" * 60)
    print()
    
    # Initialize coordinator
    coordinator = Coordinator()
    
    print("Generating itinerary...")
    print()
    
    # Process request
    result = coordinator.process_request(user_request)
    
    # Display results
    if "error" in result:
        print("=" * 60)
        print("Error:")
        print("=" * 60)
        print(result['error'])
        print(f"\nStatus: {result.get('status', 'unknown')}")
        print("=" * 60)
    else:
        print("=" * 60)
        print("Generated Itinerary:")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        print()
        print("=" * 60)


if __name__ == "__main__":
    main()

