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

def predict_price(year, mileage, make, model):
    """Predict car price using trained model"""
    try:
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
        prediction = model.predict(features)[0]
        
        # Calculate confidence range (±15%)
        low_estimate = prediction * 0.85
        high_estimate = prediction * 1.15
        
        # Determine confidence level
        confidence = "high" if year >= 2015 else "medium" if year >= 2010 else "low"
        
        result = {
            "estimated_price": round(prediction, 2),
            "low_estimate": round(low_estimate, 2),
            "high_estimate": round(high_estimate, 2),
            "confidence": confidence
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(f"Prediction failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python car_price_model.py [train|predict] [args...]", file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "train":
        train_model()
    elif command == "predict":
        if len(sys.argv) != 6:
            print("Usage: python car_price_model.py predict <year> <mileage> <make> <model>", file=sys.stderr)
            sys.exit(1)
        
        year = int(sys.argv[2])
        mileage = int(sys.argv[3])
        make = sys.argv[4]
        model = sys.argv[5]
        
        predict_price(year, mileage, make, model)
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
