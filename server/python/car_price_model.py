#!/usr/bin/env python3
import sys
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import pickle
import os
from pathlib import Path

MODEL_PATH = "server/python/car_price_model.pkl"
ENCODERS_PATH = "server/python/label_encoders.pkl"
DATASET_PATH = "sample_data/cars.csv"

# Car model production year ranges for validation
CAR_MODEL_YEARS = {
    "Toyota": {
        "Camry": (1982, 2024), "Corolla": (1966, 2024), "RAV4": (1994, 2024),
        "Prius": (1997, 2024), "Highlander": (2000, 2024), "Sienna": (1997, 2024),
        "Tundra": (1999, 2024), "Tacoma": (1995, 2024)
    },
    "Honda": {
        "Civic": (1972, 2024), "Accord": (1976, 2024), "CR-V": (1995, 2024),
        "Pilot": (2002, 2024), "Fit": (2001, 2024), "Odyssey": (1994, 2024),
        "Ridgeline": (2005, 2024), "HR-V": (2014, 2024)
    },
    "Ford": {
        "F-150": (1975, 2024), "Explorer": (1990, 2024), "Escape": (2000, 2024),
        "Mustang": (1964, 2024), "Focus": (1998, 2018), "Fusion": (2005, 2020),
        "Edge": (2006, 2024), "Expedition": (1996, 2024)
    },
    "Chevrolet": {
        "Silverado": (1999, 2024), "Equinox": (2004, 2024), "Malibu": (1964, 2024),
        "Tahoe": (1995, 2024), "Cruze": (2008, 2019), "Impala": (1958, 2020),
        "Traverse": (2008, 2024), "Suburban": (1935, 2024)
    },
    "Nissan": {
        "Altima": (1992, 2024), "Sentra": (1982, 2024), "Rogue": (2007, 2024),
        "Pathfinder": (1985, 2024), "370Z": (2008, 2020), "Maxima": (1981, 2023),
        "Murano": (2002, 2024), "Titan": (2003, 2024)
    },
    "BMW": {
        "3 Series": (1975, 2024), "5 Series": (1972, 2024), "X3": (2003, 2024),
        "X5": (1999, 2024), "7 Series": (1977, 2024), "X1": (2009, 2024),
        "4 Series": (2013, 2024), "2 Series": (2014, 2024)
    },
    "Mercedes-Benz": {
        "C-Class": (1993, 2024), "E-Class": (1953, 2024), "GLC": (2015, 2024),
        "GLE": (2015, 2024), "S-Class": (1972, 2024), "A-Class": (1997, 2024),
        "GLA": (2013, 2024), "CLA": (2013, 2024)
    },
    "Audi": {
        "A4": (1994, 2024), "A6": (1994, 2024), "Q5": (2008, 2024),
        "Q7": (2005, 2024), "A3": (1996, 2024), "Q3": (2011, 2024),
        "A5": (2007, 2024), "Q8": (2018, 2024)
    },
    "Volkswagen": {
        "Jetta": (1979, 2024), "Passat": (1973, 2024), "Tiguan": (2007, 2024),
        "Golf": (1974, 2024), "Atlas": (2017, 2024), "Beetle": (1997, 2019),
        "Arteon": (2018, 2024), "ID.4": (2020, 2024)
    },
    "Subaru": {
        "Outback": (1994, 2024), "Forester": (1997, 2024), "Impreza": (1992, 2024),
        "Crosstrek": (2012, 2024), "Legacy": (1989, 2024), "Ascent": (2018, 2024),
        "BRZ": (2012, 2024), "WRX": (2001, 2024)
    },
    "Mazda": {
        "CX-5": (2012, 2024), "Mazda3": (2003, 2024), "CX-9": (2006, 2024),
        "Mazda6": (2002, 2024), "CX-3": (2015, 2024), "MX-5 Miata": (1989, 2024),
        "CX-30": (2019, 2024), "CX-50": (2022, 2024)
    },
    "Hyundai": {
        "Elantra": (1990, 2024), "Tucson": (2004, 2024), "Santa Fe": (2000, 2024),
        "Sonata": (1985, 2024), "Accent": (1994, 2024), "Palisade": (2019, 2024),
        "Kona": (2017, 2024), "Veloster": (2011, 2022)
    }
}

def load_or_create_sample_data():
    """Load CSV data or create sample dataset if none exists"""
    if os.path.exists(DATASET_PATH):
        try:
            return pd.read_csv(DATASET_PATH)
        except Exception as e:
            print(f"Error loading CSV: {e}", file=sys.stderr)
    
    # Create sample dataset if CSV doesn't exist
    np.random.seed(42)
    
    makes = ["Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "BMW", "Mercedes-Benz", 
             "Audi", "Volkswagen", "Subaru", "Mazda", "Hyundai"]
    
    models = {
        "Toyota": ["Camry", "Corolla", "RAV4", "Prius", "Highlander"],
        "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Fit"],
        "Ford": ["F-150", "Explorer", "Escape", "Mustang", "Focus"],
        "Chevrolet": ["Silverado", "Equinox", "Malibu", "Tahoe", "Cruze"],
        "Nissan": ["Altima", "Sentra", "Rogue", "Pathfinder", "370Z"],
        "BMW": ["3 Series", "5 Series", "X3", "X5", "7 Series"],
        "Mercedes-Benz": ["C-Class", "E-Class", "GLC", "GLE", "S-Class"],
        "Audi": ["A4", "A6", "Q5", "Q7", "A3"],
        "Volkswagen": ["Jetta", "Passat", "Tiguan", "Golf", "Atlas"],
        "Subaru": ["Outback", "Forester", "Impreza", "Crosstrek", "Legacy"],
        "Mazda": ["CX-5", "Mazda3", "CX-9", "Mazda6", "CX-3"],
        "Hyundai": ["Elantra", "Tucson", "Santa Fe", "Sonata", "Accent"]
    }
    
    data = []
    for _ in range(5000):  # Generate 5000 sample records
        make = np.random.choice(makes)
        model = np.random.choice(models[make])
        year = np.random.randint(2010, 2025)
        mileage = np.random.randint(5000, 150000)
        
        # Price calculation with realistic factors
        base_price = 25000
        age_factor = (2024 - year) * 1200
        mileage_factor = mileage * 0.1
        
        # Make adjustments
        make_multiplier = {
            "BMW": 1.8, "Mercedes-Benz": 1.9, "Audi": 1.7,
            "Toyota": 1.2, "Honda": 1.15, "Subaru": 1.1,
            "Ford": 1.0, "Chevrolet": 0.95, "Nissan": 1.05,
            "Volkswagen": 1.3, "Mazda": 1.0, "Hyundai": 0.9
        }.get(make, 1.0)
        
        price = base_price * make_multiplier - age_factor - mileage_factor
        price = max(price, 3000)  # Minimum price
        price += np.random.normal(0, 2000)  # Add some noise
        price = max(price, 1000)  # Absolute minimum
        
        data.append({
            "year": year,
            "mileage": mileage,
            "make": make,
            "model": model,
            "price": round(price, 2)
        })
    
    return pd.DataFrame(data)

def train_model():
    """Train the RandomForest model and save it"""
    try:
        # Load data
        df = load_or_create_sample_data()
        
        # Prepare features
        le_make = LabelEncoder()
        le_model = LabelEncoder()
        
        df_encoded = df.copy()
        df_encoded['make_encoded'] = le_make.fit_transform(df['make'])
        df_encoded['model_encoded'] = le_model.fit_transform(df['model'])
        
        # Features and target
        X = df_encoded[['year', 'mileage', 'make_encoded', 'model_encoded']]
        y = df_encoded['price']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Save model and encoders
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        
        with open(ENCODERS_PATH, 'wb') as f:
            pickle.dump({'make_encoder': le_make, 'model_encoder': le_model}, f)
        
        print(f"Model trained successfully. MAE: ${mae:.2f}", file=sys.stderr)
        
    except Exception as e:
        print(f"Training failed: {e}", file=sys.stderr)
        sys.exit(1)

def validate_car_model_year(year, make, model):
    """Validate if the model existed in the given year"""
    if make not in CAR_MODEL_YEARS:
        return True, None  # Unknown make, allow prediction but with lower confidence
    
    # Check if model exists for this make
    models_for_make = CAR_MODEL_YEARS[make]
    if model not in models_for_make:
        return True, None  # Unknown model, allow prediction but with lower confidence
    
    # Check year range
    start_year, end_year = models_for_make[model]
    if year < start_year or year > end_year:
        if year < start_year:
            return False, f"The {make} {model} was first produced in {start_year}, not {year}. Please check the model year."
        else:
            return False, f"The {make} {model} was discontinued in {end_year}, not available in {year}. Please check the model year."
    
    return True, None

def apply_condition_adjustments(price, condition, accident_history):
    """Apply adjustments based on vehicle condition and accident history"""
    # Condition multipliers
    condition_multipliers = {
        "Excellent": 1.15,  # 15% premium for excellent condition
        "Good": 1.0,        # Base price for good condition
        "Fair": 0.85,       # 15% reduction for fair condition
        "Poor": 0.65,       # 35% reduction for poor condition
        "Parts only/Salvage": 0.15  # Only salvage value
    }
    
    # Accident history multipliers
    accident_multipliers = {
        "None": 1.0,              # No reduction for clean history
        "Minor (1-2)": 0.92,      # 8% reduction for minor accidents
        "Major (3+)": 0.78,       # 22% reduction for major accidents
        "Serious/Total Loss": 0.25 # Heavily reduced for serious damage
    }
    
    # Apply both adjustments
    condition_adjusted = price * condition_multipliers.get(condition, 1.0)
    final_price = condition_adjusted * accident_multipliers.get(accident_history, 1.0)
    
    return final_price

def apply_regional_adjustments(price, location, currency):
    """Apply regional market adjustments and currency conversion"""
    # Regional price multipliers based on market conditions
    regional_multipliers = {
        "US": 1.0,      # Base price (USD market)
        "Canada": 1.08  # Canadian market typically 8% higher due to taxes, import duties, etc.
    }
    
    # Apply regional adjustment
    adjusted_price = price * regional_multipliers.get(location, 1.0)
    
    # Currency conversion (approximate rates - in real app would use live rates)
    exchange_rates = {
        "USD": 1.0,
        "CAD": 1.35  # 1 USD = 1.35 CAD (approximate)
    }
    
    # Convert to target currency
    if currency == "CAD" and location == "US":
        # Converting US price to CAD
        converted_price = adjusted_price * exchange_rates["CAD"]
    elif currency == "USD" and location == "Canada":
        # Converting Canadian price to USD
        converted_price = adjusted_price / exchange_rates["CAD"]
    else:
        # Same currency and location, no conversion needed
        converted_price = adjusted_price
    
    return converted_price

def predict_price(year, mileage, make, model, location="US", currency="USD", accident_history="None", condition="Good"):
    """Predict car price using trained model with all adjustments"""
    try:
        # Validate car model and year combination
        is_valid, validation_error = validate_car_model_year(year, make, model)
        if not is_valid:
            result = {
                "error": "Invalid car model/year combination",
                "message": validation_error
            }
            print(json.dumps(result))
            return
        
        # Load model and encoders
        if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODERS_PATH):
            train_model()
        
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        
        with open(ENCODERS_PATH, 'rb') as f:
            encoders = pickle.load(f)
        
        le_make = encoders['make_encoder']
        le_model = encoders['model_encoder']
        
        # Encode categorical variables
        try:
            make_encoded = le_make.transform([make])[0]
        except ValueError:
            # Handle unknown make
            make_encoded = 0
        
        try:
            model_encoded = le_model.transform([model])[0]
        except ValueError:
            # Handle unknown model
            model_encoded = 0
        
        # Prepare features
        features = np.array([[year, mileage, make_encoded, model_encoded]])
        
        # Predict
        base_prediction = model.predict(features)[0]
        
        # Apply condition and accident history adjustments first
        condition_adjusted = apply_condition_adjustments(base_prediction, condition, accident_history)
        
        # Apply regional adjustments and currency conversion
        adjusted_prediction = apply_regional_adjustments(condition_adjusted, location, currency)
        
        # Calculate confidence range (±15%)
        low_estimate = adjusted_prediction * 0.85
        high_estimate = adjusted_prediction * 1.15
        
        # Determine confidence level - lower confidence for unknown make/model combinations
        if make not in CAR_MODEL_YEARS or model not in CAR_MODEL_YEARS.get(make, {}):
            confidence = "low"  # Unknown make/model combination
        else:
            confidence = "high" if year >= 2015 else "medium" if year >= 2010 else "low"
        
        result = {
            "estimated_price": round(adjusted_prediction, 2),
            "low_estimate": round(low_estimate, 2),
            "high_estimate": round(high_estimate, 2),
            "confidence": confidence,
            "currency": currency,
            "location": location,
            "condition": condition,
            "accident_history": accident_history
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(f"Prediction failed: {e}", file=sys.stderr)
        sys.exit(1)

def get_models_for_make_and_year(make, year):
    """Get available models for a specific make and year"""
    try:
        year = int(year)
        if make not in CAR_MODEL_YEARS:
            print(json.dumps([]))  # Return empty list for unknown makes
            return
        
        models_for_make = CAR_MODEL_YEARS[make]
        available_models = []
        
        for model, (start_year, end_year) in models_for_make.items():
            if start_year <= year <= end_year:
                available_models.append(model)
        
        # Sort models alphabetically
        available_models.sort()
        print(json.dumps(available_models))
        
    except Exception as e:
        print(f"Failed to get models: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python car_price_model.py [train|predict|get_models] [args...]", file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "train":
        train_model()
    elif command == "predict":
        if len(sys.argv) < 6 or len(sys.argv) > 10:
            print("Usage: python car_price_model.py predict <year> <mileage> <make> <model> [location] [currency] [accident_history] [condition]", file=sys.stderr)
            sys.exit(1)
        
        year = int(sys.argv[2])
        mileage = int(sys.argv[3])
        make = sys.argv[4]
        model = sys.argv[5]
        location = sys.argv[6] if len(sys.argv) > 6 else "US"
        currency = sys.argv[7] if len(sys.argv) > 7 else "USD"
        accident_history = sys.argv[8] if len(sys.argv) > 8 else "None"
        condition = sys.argv[9] if len(sys.argv) > 9 else "Good"
        
        predict_price(year, mileage, make, model, location, currency, accident_history, condition)
    elif command == "get_models":
        if len(sys.argv) != 4:
            print("Usage: python car_price_model.py get_models <make> <year>", file=sys.stderr)
            sys.exit(1)
        
        make = sys.argv[2]
        year = sys.argv[3]
        
        get_models_for_make_and_year(make, year)
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
