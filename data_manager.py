import json
import os
import csv
import pandas as pd
import re
from datetime import datetime

# Default data paths
DATA_DIR = "data"
SAVED_PLANS_FILE = os.path.join(DATA_DIR, "saved_plans.json")
USER_PROFILES_FILE = os.path.join(DATA_DIR, "user_profiles.json")

# Hong Kong whole life insurance constants
WHOLE_LIFE_FILE = os.path.join(DATA_DIR, "whole_life_insurance.json")
WHOLE_LIFE_CSV = "Compare Whole Life Critical Illness Insurance _ 10Life.csv"

# Function to clean currency values
def clean_currency(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Remove currency symbols and commas
        clean_value = re.sub(r'[^\d.]', '', value.replace(',', ''))
        return float(clean_value) if clean_value else 0.0
    return 0.0

# Function to clean score values (e.g., "9.9 / 10" -> 9.9)
def clean_score(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Extract the score part before any "/"
        if "/" in value:
            value = value.split("/")[0].strip()
        # Remove any non-numeric characters except decimal point
        clean_value = re.sub(r'[^\d.]', '', value)
        return float(clean_value) if clean_value else 0.0
    return 0.0

# Create data directory if it doesn't exist
def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

# Initialize data files if they don't exist
def initialize_data_files():
    ensure_data_dir()
    
    # Saved plans (empty by default - using a dictionary structure)
    if not os.path.exists(SAVED_PLANS_FILE):
        with open(SAVED_PLANS_FILE, 'w') as f:
            json.dump({}, f, indent=4)
    
    # User profiles (empty by default)
    if not os.path.exists(USER_PROFILES_FILE):
        with open(USER_PROFILES_FILE, 'w') as f:
            json.dump({}, f, indent=4)

# Function to import the CSV data into structured JSON
def import_whole_life_from_csv():
    """Import whole life insurance data from CSV file."""
    ensure_data_dir()
    
    if not os.path.exists(WHOLE_LIFE_CSV):
        print(f"Error: CSV file '{WHOLE_LIFE_CSV}' not found.")
        return False
    
    try:
        # Import data from CSV with semicolon delimiter
        df = pd.read_csv(WHOLE_LIFE_CSV, delimiter=';', encoding='utf-8')
        print(f"Successfully read CSV with {len(df)} rows.")
        
        # Map columns to expected structure for whole life insurance
        insurance_plans = []
        
        for _, row in df.iterrows():
            try:
                # Clean score values
                whole_life_score = clean_score(row['WholeLifeScore'])
                terms_score = clean_score(row['TermsScore'])
                total_score = clean_score(row['TotalScore'])
                
                # Create a plan structure that matches what the application expects
                plan = {
                    "id": f"whole_life_{len(insurance_plans)}",
                    "title": row['Name'],
                    "company": row['Company'],
                    "type": "whole_life",
                    "price": clean_currency(row['AnnualPremium']) / 12,  # Convert annual to monthly
                    "features": [
                        f"{row['Number_of_Covered_Major_Illnesses']} Major Illnesses",
                        f"{row['Number_of_Covered_Early_Illnesses']} Early Stage Illnesses",
                        f"Maximum Payout: {row['Maximum_Payout']}",
                        f"Premium Term: {row['PremiumTerm_Years']} years"
                    ],
                    "details": {
                        "whole_life_score": whole_life_score,
                        "terms_score": terms_score,
                        "total_score": total_score,
                        "original_whole_life_score": row['WholeLifeScore'],  # Keep original for display
                        "original_terms_score": row['TermsScore'],  # Keep original for display
                        "original_total_score": row['TotalScore'],  # Keep original for display
                        "gender": row['Gender'],
                        "age": row['Age'],
                        "smoker_status": row['Smoker_Status'],
                        "premium_term_years": row['PremiumTerm_Years'],
                        "annual_premium": row['AnnualPremium'],  # Keep original for display
                        "annual_premium_value": clean_currency(row['AnnualPremium']),  # Cleaned value for calculations
                        "major_illnesses": row['Number_of_Covered_Major_Illnesses'],
                        "early_illnesses": row['Number_of_Covered_Early_Illnesses'],
                        "maximum_payout": row['Maximum_Payout'],
                        "waiting_period": row['Waiting_Period'],
                        "issue_age": row['Issue_Age']
                    },
                    "starred": False  # Default value
                }
                insurance_plans.append(plan)
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
        
        # Save to JSON file
        with open(WHOLE_LIFE_FILE, 'w', encoding='utf-8') as f:
            json.dump(insurance_plans, f, ensure_ascii=False, indent=4)
        
        print(f"Successfully converted CSV to JSON and saved to {WHOLE_LIFE_FILE}")
        return True
    
    except Exception as e:
        print(f"Error processing CSV file: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Get whole life insurance plans
def get_whole_life_insurance():
    """Retrieve all whole life insurance plans."""
    # Import if JSON file doesn't exist
    if not os.path.exists(WHOLE_LIFE_FILE):
        import_whole_life_from_csv()
    
    try:
        with open(WHOLE_LIFE_FILE, "r", encoding="utf-8") as f:
            whole_life_plans = json.load(f)
        return whole_life_plans
    except Exception as e:
        print(f"Error loading whole life insurance data: {str(e)}")
        # Return empty list as fallback
        return []

# Filter whole life insurance plans by criteria
def filter_whole_life_insurance(gender=None, age=None, smoker_status=None, max_price=None, min_score=None):
    """Filter whole life insurance plans based on criteria."""
    all_plans = get_whole_life_insurance()
    filtered_plans = []
    
    for plan in all_plans:
        # Default to include the plan
        include_plan = True
        
        # Filter by gender
        if gender and plan["details"]["gender"] != gender:
            include_plan = False
        
        # Filter by age - check if the input age is within the plan's age range
        if age:
            try:
                plan_age = int(plan["details"]["age"])
                if age < plan_age:
                    include_plan = False
            except (ValueError, KeyError):
                pass
        
        # Filter by smoker status
        if smoker_status and plan["details"]["smoker_status"] != smoker_status:
            include_plan = False
        
        # Filter by max price
        if max_price and plan["price"] > max_price:
            include_plan = False
        
        # Filter by minimum score
        if min_score:
            try:
                plan_score = float(plan["details"]["total_score"])
                if plan_score < min_score:
                    include_plan = False
            except (ValueError, KeyError):
                pass
        
        # Add plan to filtered list if it meets all criteria
        if include_plan:
            filtered_plans.append(plan)
    
    return filtered_plans

# Get plan by ID
def get_plan_by_id(plan_id):
    """Get a specific plan by ID."""
    # Check different plan types
    all_plans = get_whole_life_insurance()
    
    # Search for the plan with the matching ID
    for plan in all_plans:
        if plan["id"] == plan_id:
            return plan
    
    return None

# Get a user's saved plans
def get_saved_plans(user_id="default"):
    """Get a user's saved plans."""
    if not os.path.exists(SAVED_PLANS_FILE):
        initialize_data_files()
    
    try:
        with open(SAVED_PLANS_FILE, 'r') as f:
            saved_plans_data = json.load(f)
        
        # If user_id key doesn't exist, return empty list
        return saved_plans_data.get(user_id, [])
    except json.JSONDecodeError:
        # If the file is corrupted, reset it
        with open(SAVED_PLANS_FILE, 'w') as f:
            json.dump({}, f, indent=4)
        return []

# Save a plan for a user
def save_plan(plan_id, user_id="default"):
    """Save a plan for a user."""
    if not os.path.exists(SAVED_PLANS_FILE):
        initialize_data_files()
    
    # Get the plan details
    plan = get_plan_by_id(plan_id)
    if not plan:
        return False
    
    # Read current saved plans
    try:
        with open(SAVED_PLANS_FILE, 'r') as f:
            saved_plans_data = json.load(f)
    except json.JSONDecodeError:
        # If the file is corrupted, reset it
        saved_plans_data = {}
    
    # Initialize user's saved plans if not exist
    if user_id not in saved_plans_data:
        saved_plans_data[user_id] = []
    
    # Check if plan is already saved
    for saved_plan in saved_plans_data[user_id]:
        if saved_plan['id'] == plan_id:
            return True  # Already saved
    
    # Add saved date to plan
    saved_plan = plan.copy()
    saved_plan['date_saved'] = datetime.now().strftime("%B %d, %Y")
    
    # Add to saved plans
    saved_plans_data[user_id].append(saved_plan)
    
    # Write back to file
    with open(SAVED_PLANS_FILE, 'w') as f:
        json.dump(saved_plans_data, f, indent=4)
    
    return True

# Remove a saved plan
def remove_saved_plan(plan_id, user_id="default"):
    """Remove a saved plan."""
    if not os.path.exists(SAVED_PLANS_FILE):
        return False
    
    # Read current saved plans
    try:
        with open(SAVED_PLANS_FILE, 'r') as f:
            saved_plans_data = json.load(f)
    except json.JSONDecodeError:
        # If the file is corrupted, reset it
        return False
    
    # Check if user has any saved plans
    if user_id not in saved_plans_data:
        return False
    
    # Remove the plan from user's saved plans
    saved_plans_data[user_id] = [plan for plan in saved_plans_data[user_id] if plan['id'] != plan_id]
    
    # Write back to file
    with open(SAVED_PLANS_FILE, 'w') as f:
        json.dump(saved_plans_data, f, indent=4)
    
    return True

# Custom JSON serializer for handling datetime objects
def json_serializable(obj):
    if hasattr(obj, 'isoformat'):  # Check if it's a datetime object
        return obj.isoformat()
    elif isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# Save user profile data
def save_user_profile(profile_data, user_id="default"):
    """Save user profile data."""
    if not os.path.exists(USER_PROFILES_FILE):
        initialize_data_files()
    
    # Create a serializable copy of the profile data
    serializable_profile = {}
    for key, value in profile_data.items():
        # Convert datetime objects to strings
        if hasattr(value, 'isoformat'):  # Check if it's a datetime object
            serializable_profile[key] = value.isoformat()
        else:
            serializable_profile[key] = value
    
    # Read current profiles
    try:
        with open(USER_PROFILES_FILE, 'r') as f:
            profiles = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        # If the file is corrupted or empty, reset it
        profiles = {}
    
    # Update profile
    profiles[user_id] = serializable_profile
    
    # Write back to file
    with open(USER_PROFILES_FILE, 'w') as f:
        json.dump(profiles, f, indent=4)
    
    return True

# Get user profile data
def get_user_profile(user_id="default"):
    """Get user profile data."""
    if not os.path.exists(USER_PROFILES_FILE):
        initialize_data_files()
    
    # Read profiles
    try:
        with open(USER_PROFILES_FILE, 'r') as f:
            profiles = json.load(f)
        
        # Return the profile or empty dict if not found
        return profiles.get(user_id, {})
    except json.JSONDecodeError:
        # If the file is corrupted, reset it
        with open(USER_PROFILES_FILE, 'w') as f:
            json.dump({}, f, indent=4)
        return {}

# Initialize data files when module is imported
initialize_data_files() 