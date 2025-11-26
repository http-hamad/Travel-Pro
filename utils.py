"""Utility functions for Travel-Pro System"""
import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


def save_output_to_logs(user_request: str, output: Dict[str, Any], logs_dir: str = "logs") -> str:
    """
    Save output to logs folder with timestamp filename
    
    Args:
        user_request: The original user query/request
        output: The output dictionary to save
        logs_dir: Directory to save logs (default: "logs")
        
    Returns:
        Path to the saved file
    """
    # Create logs directory if it doesn't exist
    Path(logs_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for filename
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
    filename = f"{timestamp}.json"
    filepath = os.path.join(logs_dir, filename)
    
    # Prepare data to save (include query and output)
    iso_timestamp = now.isoformat()
    data_to_save = {
        "timestamp": iso_timestamp,
        "query": user_request,
        "output": output
    }
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, indent=2, ensure_ascii=False)
    
    # Append to CSV log
    append_to_trip_csv(
        logs_dir=logs_dir,
        timestamp=now.strftime("%Y-%m-%d %H:%M:%S"),
        user_request=user_request,
        output=output
    )

    return filepath


def append_to_trip_csv(logs_dir: str, timestamp: str, user_request: str, output: Dict[str, Any]) -> None:
    """Append request/response data to logs/trip_data.csv"""
    csv_path = Path(logs_dir) / "trip_data.csv"
    fieldnames: List[str] = [
        "timestamp",
        "query",
        "error",
        "status",
        "day",
        "current_city",
        "transportation",
        "breakfast",
        "attraction",
        "lunch",
        "dinner",
        "accommodation",
        "daily_cost",
        "total_cost",
        "remaining_budget",
    ]

    file_exists = csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        if "error" in output:
            writer.writerow(
                {
                    "timestamp": timestamp,
                    "query": user_request.strip(),
                    "error": output.get("error", ""),
                    "status": output.get("status", ""),
                }
            )
        else:
            days = output.get("days", [])
            total_cost = output.get("total_cost", "")
            remaining_budget = output.get("remaining_budget", "")
            for idx, day in enumerate(days):
                row = {
                    "timestamp": timestamp,
                    "query": user_request.strip(),
                    "error": "",
                    "status": "success",
                    "day": day.get("day", ""),
                    "current_city": day.get("current_city", ""),
                    "transportation": day.get("transportation", ""),
                    "breakfast": day.get("breakfast", ""),
                    "attraction": day.get("attraction", ""),
                    "lunch": day.get("lunch", ""),
                    "dinner": day.get("dinner", ""),
                    "accommodation": day.get("accommodation", ""),
                    "daily_cost": day.get("daily_cost", ""),
                }
                if idx == len(days) - 1:
                    row["total_cost"] = total_cost
                    row["remaining_budget"] = remaining_budget
                writer.writerow(row)

