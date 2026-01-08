#!/usr/bin/env python
import data_manager
import json
import sys
import pandas as pd
import os
import re

def main():
    """Test the whole life insurance data import and filtering using the new CSV format."""
    print("Importing whole life insurance data from new CSV format...")
    
    # Define paths
    csv_path = "Compare Whole Life Critical Illness Insurance _ 10Life.csv"
    json_path = "whole_life_insurance.json"
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"Error: File '{csv_path}' not found.")
        return False
    
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
        
    try:
        # Import data from the new CSV format with semicolon delimiter
        df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
        print(f"Successfully read CSV with {len(df)} rows.")
        
        # Function to clean currency values
        def clean_currency(value):
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                # Remove currency symbols and commas
                clean_value = re.sub(r'[^\d.]', '', value.replace(',', ''))
                return float(clean_value) if clean_value else 0.0
            return 0.0
        
        # Map columns to expected structure for whole life insurance
        insurance_plans = []
        
        for _, row in df.iterrows():
            # Handle potential missing or invalid data
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
                    }
                }
                insurance_plans.append(plan)
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
        
        # Save to JSON file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(insurance_plans, f, ensure_ascii=False, indent=4)
        
        print(f"Successfully converted CSV to JSON format and saved to {json_path}")
        
        # Test filtering function
        print("\nTop 5 whole life insurance plans:")
        for plan in insurance_plans[:5]:
            print(f"- {plan['title']} by {plan['company']}")
            print(f"  Price: {plan['details']['annual_premium']} ({plan['price']:.2f}/month)")
            print(f"  Total Score: {plan['details']['original_total_score']} (cleaned: {plan['details']['total_score']:.1f})")
            print(f"  WholeLife Score: {plan['details']['original_whole_life_score']} (cleaned: {plan['details']['whole_life_score']:.1f})")
            print(f"  Terms Score: {plan['details']['original_terms_score']} (cleaned: {plan['details']['terms_score']:.1f})")
            print(f"  Features: {', '.join(plan['features'])}")
            print()
        
        # Filter plans for a 35-year old male non-smoker
        filtered_plans = [p for p in insurance_plans 
                          if p['details']['gender'] == 'Male' 
                          and int(float(p['details']['age'])) >= 35
                          and p['details']['smoker_status'] == 'Non Smoker'
                          and p['price'] <= 5000]
        
        print(f"\nFound {len(filtered_plans)} plans for a 35-year old male non-smoker:")
        
        # Sort by price
        filtered_plans.sort(key=lambda x: x["price"])
        
        # Display top 5 filtered plans by price
        for plan in filtered_plans[:5]:
            print(f"- {plan['title']} by {plan['company']}")
            print(f"  Price: {plan['details']['annual_premium']} ({plan['price']:.2f}/month)")
            print(f"  Total Score: {plan['details']['original_total_score']}")
            print()
        
        # Create a summary object
        summary = {
            "total_plans": len(insurance_plans),
            "plans_by_company": {},
            "avg_price": sum(p["price"] for p in insurance_plans) / len(insurance_plans),
            "avg_score": sum(p["details"]["total_score"] for p in insurance_plans) / len(insurance_plans),
            "price_range": {
                "min": min(p["price"] for p in insurance_plans),
                "max": max(p["price"] for p in insurance_plans)
            }
        }
        
        # Count plans by company
        for plan in insurance_plans:
            company = plan["company"]
            if company not in summary["plans_by_company"]:
                summary["plans_by_company"][company] = 0
            summary["plans_by_company"][company] += 1
        
        # Save summary
        with open("hk_insurance_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)
        
        print("\nSummary information saved to hk_insurance_summary.json")
        return True
        
    except Exception as e:
        print(f"Error processing CSV file: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main() 