#!/usr/bin/env python3
"""
car_price_model.py

Usage:
    python car_price_model.py train
    python car_price_model.py predict <year> <odometer> <odometer_unit> <make> <model> [location] [currency] [accident_history] [condition]
    python car_price_model.py get_models <make> <year>
    python car_price_model.py similar <make> <model> <year> <mileage> <mileage_unit> <location>

This script is adapted to handle datasets where make and model are in a single "make_model"
column (e.g., "chevrolet silverado 1500 crew") or separate "make" and "model" columns.
It trains a RandomForestRegressor to estimate car prices using features:
    - year
    - odometer
    - make (encoded)
    - model (encoded)
"""

import sys
import json
import pickle
from huggingface_hub import hf_hub_download
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re
import time
import math
from urllib.parse import quote_plus, urljoin

# Model paths
MODEL_PATH = "server/python/car_price_model.pkl"
ENCODERS_PATH = "server/python/label_encoders.pkl"

# Download model files from Hugging Face if they are not available locally
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = hf_hub_download(
        repo_id="SarpShark/car-price-predictor-model",
        filename="car_price_model.pkl"
    )

if not os.path.exists(ENCODERS_PATH):
    ENCODERS_PATH = hf_hub_download(
        repo_id="SarpShark/car-price-predictor-model",
        filename="label_encoders.pkl"
    )

# Dataset path
DATASET_PATH = os.path.join(
    os.getcwd(),
    "sample_data",
    "cars.csv"
)

HEADERS = {"User-Agent": "Mozilla/5.0"}
SEARCH_PATH = "/search/cta"

# Car model production year ranges for validation (subset: expand as needed)
# Car model production year ranges for validation (subset: expand as needed)
CAR_MODEL_YEARS = {
    "Toyota": {
        "Camry": (1982, 2024),
        "Corolla": (1966, 2024),
        "RAV4": (1994, 2024),
        "Prius": (1997, 2024),
        "Highlander": (2000, 2024),
        "Sienna": (1997, 2024),
        "Tundra": (1999, 2024),
        "Tacoma": (1995, 2024),
        "Avalon": (1994, 2024),
        "C-HR": (2016, 2024),
        "Mirai": (2014, 2024)
    },
    "Honda": {
        "Civic": (1972, 2024),
        "Accord": (1976, 2024),
        "CR-V": (1995, 2024),
        "Pilot": (2002, 2024),
        "Fit": (2001, 2024),
        "Odyssey": (1994, 2024),
        "Ridgeline": (2005, 2024),
        "HR-V": (2014, 2024),
        "Passport": (2019, 2024)
    },
    "Ford": {
        "F-150": (1975, 2024),
        "Explorer": (1990, 2024),
        "Escape": (2000, 2024),
        "Mustang": (1964, 2024),
        "Focus": (1998, 2018),
        "Fusion": (2005, 2020),
        "Edge": (2006, 2024),
        "Expedition": (1996, 2024),
        "Ranger": (1983, 2024),
        "Bronco": (1965, 1996),
        "Bronco (relaunch)": (2021, 2024)
    },
    "Chevrolet": {
        "Silverado": (1999, 2024),
        "Equinox": (2004, 2024),
        "Malibu": (1964, 2024),
        "Tahoe": (1995, 2024),
        "Cruze": (2008, 2019),
        "Impala": (1958, 2020),
        "Traverse": (2008, 2024),
        "Suburban": (1935, 2024),
        "Bolt EV": (2016, 2024)
    },
    "Nissan": {
        "Altima": (1992, 2024),
        "Sentra": (1982, 2024),
        "Rogue": (2007, 2024),
        "Pathfinder": (1985, 2024),
        "370Z": (2008, 2020),
        "Maxima": (1981, 2023),
        "Murano": (2002, 2024),
        "Titan": (2003, 2024),
        "Frontier": (1998, 2024),
        "Leaf": (2010, 2024)
    },
    "BMW": {
        "3 Series": (1975, 2024),
        "5 Series": (1972, 2024),
        "X3": (2003, 2024),
        "X5": (1999, 2024),
        "7 Series": (1977, 2024),
        "X1": (2009, 2024),
        "4 Series": (2013, 2024),
        "2 Series": (2014, 2024),
        "i3": (2013, 2021),
        "i4": (2021, 2024)
    },
    "Mercedes-Benz": {
        "C-Class": (1993, 2024),
        "E-Class": (1953, 2024),
        "GLC": (2015, 2024),
        "GLE": (2015, 2024),
        "S-Class": (1972, 2024),
        "A-Class": (1997, 2024),
        "GLA": (2013, 2024),
        "CLA": (2013, 2024)
    },
    "Audi": {
        "A4": (1994, 2024),
        "A6": (1994, 2024),
        "Q5": (2008, 2024),
        "Q7": (2005, 2024),
        "A3": (1996, 2024),
        "Q3": (2011, 2024),
        "A5": (2007, 2024),
        "Q8": (2018, 2024),
        "e-tron": (2018, 2022)
    },
    "Volkswagen": {
        "Jetta": (1979, 2024),
        "Passat": (1973, 2024),
        "Tiguan": (2007, 2024),
        "Golf": (1974, 2024),
        "Atlas": (2017, 2024),
        "Beetle": (1997, 2019),
        "Arteon": (2018, 2024),
        "ID.4": (2020, 2024),
        "ID.3": (2019, 2024)
    },
    "Subaru": {
        "Outback": (1994, 2024),
        "Forester": (1997, 2024),
        "Impreza": (1992, 2024),
        "Crosstrek": (2012, 2024),
        "Legacy": (1989, 2024),
        "Ascent": (2018, 2024),
        "BRZ": (2012, 2024),
        "WRX": (2001, 2024)
    },
    "Mazda": {
        "CX-5": (2012, 2024),
        "Mazda3": (2003, 2024),
        "CX-9": (2006, 2024),
        "Mazda6": (2002, 2024),
        "CX-3": (2015, 2020),
        "MX-5 Miata": (1989, 2024),
        "CX-30": (2019, 2024),
        "CX-50": (2022, 2024)
    },
    "Hyundai": {
        "Elantra": (1990, 2024),
        "Tucson": (2004, 2024),
        "Santa Fe": (2000, 2024),
        "Sonata": (1985, 2024),
        "Accent": (1994, 2024),
        "Palisade": (2019, 2024),
        "Kona": (2017, 2024),
        "Veloster": (2011, 2022),
        "Ioniq 5": (2021, 2024)
    },
    "Kia": {
        "Soul": (2008, 2024),
        "Sportage": (1993, 2024),
        "Sorento": (2002, 2024),
        "Forte": (2008, 2024),
        "Telluride": (2020, 2024),
        "Stinger": (2017, 2024),
        "EV6": (2021, 2024)
    },
    "Tesla": {
        "Model S": (2012, 2024),
        "Model X": (2015, 2024),
        "Model 3": (2017, 2024),
        "Model Y": (2020, 2024)
    },
    "Rivian": {
        "R1T": (2021, 2024),
        "R1S": (2022, 2024)
    },
    "Lucid": {
        "Air": (2021, 2024)
    },
    "Polestar": {
        "1": (2019, 2020),
        "2": (2020, 2024),
        "3": (2023, 2024)
    },
    "Fisker": {
        "Ocean": (2022, 2024)
    },
    "NIO": {
        "ES8": (2017, 2024),
        "ES6": (2018, 2024),
        "EC6": (2020, 2024),
        "ET7": (2022, 2024)
    },
    "BYD": {
        "Tang": (2015, 2024),
        "Han": (2020, 2024),
        "Yuan/Atto 3": (2019, 2024),
        "Seal": (2022, 2024)
    },
    "Xpeng": {
        "G3": (2018, 2021),
        "P7": (2020, 2024),
        "P5": (2021, 2024)
    },
    "Volvo": {
        "S60": (2000, 2024),
        "S90": (2016, 2024),
        "XC40": (2017, 2024),
        "XC60": (2008, 2024),
        "XC90": (2002, 2024)
    },
    "Genesis": {
        "G70": (2017, 2024),
        "G80": (2016, 2024),
        "GV70": (2020, 2024),
        "GV80": (2020, 2024)
    }
}

# --- Split U.S. and Canadian cities ---
US_CITIES = {
    "new york": "https://newyork.craigslist.org",
    "los angeles": "https://losangeles.craigslist.org",
    "chicago": "https://chicago.craigslist.org",
    "houston": "https://houston.craigslist.org",
    "phoenix": "https://phoenix.craigslist.org",
    "philadelphia": "https://philadelphia.craigslist.org",
    "san antonio": "https://sanantonio.craigslist.org",
    "san diego": "https://sandiego.craigslist.org",
    "dallas": "https://dallas.craigslist.org",
    "austin": "https://austin.craigslist.org",
    "jacksonville": "https://jacksonville.craigslist.org",
    "fort worth": "https://fortworth.craigslist.org",
    "columbus": "https://columbus.craigslist.org",
    "charlotte": "https://charlotte.craigslist.org", 
    "san francisco": "https://sfbay.craigslist.org",
    "indianapolis": "https://indianapolis.craigslist.org",
    "seattle": "https://seattle.craigslist.org",
    "denver": "https://denver.craigslist.org",
    "washington dc": "https://washingtondc.craigslist.org",
    "boston": "https://boston.craigslist.org",
    "el paso": "https://elpaso.craigslist.org",
    "nashville": "https://nashville.craigslist.org",
    "detroit": "https://detroit.craigslist.org",
    "oklahoma city": "https://oklahomacity.craigslist.org",
    "portland": "https://portland.craigslist.org"
}

CANADIAN_CITIES = {
    "toronto": "https://toronto.craigslist.org",
    "vancouver": "https://vancouver.craigslist.org",
    "montreal": "https://montreal.craigslist.org",
    "calgary": "https://calgary.craigslist.org",
    "edmonton": "https://edmonton.craigslist.org",
    "ottawa": "https://ottawa.craigslist.org",
    "winnipeg": "https://winnipeg.craigslist.org",
    "hamilton": "https://hamilton.craigslist.org",
    "victoria": "https://victoria.craigslist.org",
    "saskatoon": "https://saskatoon.craigslist.org",
    "regina": "https://regina.craigslist.org",
    "halifax": "https://halifax.craigslist.org",
    "kelowna": "https://kelowna.craigslist.org",
    "abbotsford": "https://abbotsford.craigslist.org",
    "laval": "https://laval.craigslist.org"
}

# Build a flattened set of known makes for matching (lowercase)
KNOWN_MAKES = set([m.lower() for m in CAR_MODEL_YEARS.keys()])

def safe_mkdir_for_path(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def normalize_text(s):
    if s is None:
        return ""
    try:
        if s != s:
            return ""
    except Exception:
        pass
    return str(s).strip()

def split_make_model_row(make_model_value):
    """
    Attempt to split a make_model string into (make, model).
    Strategy:
      1. Normalize and try to match known makes at the start (case-insensitive).
      2. If none matches, split on the first space: first token = make, rest = model.
    Returns (make, model) both capitalized nicely (title case for model, proper for dash in make).
    """
    mm = normalize_text(make_model_value).strip()
    if mm == "":
        return "", ""
    mm_lower = mm.lower()

    # Try to match any known make at the start of the string
    for make_candidate in sorted(KNOWN_MAKES, key=lambda x: -len(x)):  # longer first to match "mercedes-benz" before "mercedes"
        if mm_lower.startswith(make_candidate + " ") or mm_lower == make_candidate:
            make = make_candidate
            model = mm[len(make_candidate):].strip()
            # format: preserve common punctuation, title-case model
            make_formatted = format_make(make)
            model_formatted = model.title() if model else ""
            return make_formatted, model_formatted

    # If no known make matched, fallback: first token is make
    parts = mm.split(" ", 1)
    make = parts[0]
    model = parts[1] if len(parts) > 1 else ""
    return format_make(make), model.title()

def format_make(make_str):
    """Format make string: handle hyphens and common uppercase patterns (e.g., 'gmc' -> 'GMC')."""
    m = make_str.strip()
    # If it's an acronym (all lowercase and length <=3), uppercase it (e.g., 'gmc' -> 'GMC')
    if len(m) <= 3 and m.isalpha():
        return m.upper()
    # Handle hyphenated names
    return "-".join([part.capitalize() for part in m.split("-")])

def load_or_create_sample_data():
    """
    Loads and merges data from cars.csv, combined_canada.csv, and combined_us.csv.
    Unifies them into a consistent format:
        year, odometer, make, model, price
    Returns a cleaned and ready-to-train DataFrame.
    """
    import pandas as pd

    base_path = Path("/Users/sarpshark/Desktop/CarPricePredictor/sample_data")
    files = {
        "cars": base_path / "cars.csv",
        "canada": base_path / "combined_canada.csv",
        "us": base_path / "combined_us.csv"
    }

    dfs = []

    # --- 1. Load cars.csv (old dataset with make_model) ---
    if files["cars"].exists():
        df_cars = pd.read_csv(files["cars"])
        df_cars.columns = [c.strip().lower() for c in df_cars.columns]

        if "make_model" in df_cars.columns:
            makes, models = [], []
            for val in df_cars["make_model"].astype(str):
                make, model = split_make_model_row(val)
                makes.append(make)
                models.append(model)
            df_cars["make"] = makes
            df_cars["model"] = models

        df_cars = df_cars[["year", "odometer", "make", "model", "price"]]
        dfs.append(df_cars)

    # --- 2. Load combined_canada.csv ---
    if files["canada"].exists():
        df_can = pd.read_csv(files["canada"])
        df_can.columns = [c.strip().lower() for c in df_can.columns]
        needed = ["year", "odometer", "make", "model", "price"]
        df_can = df_can[needed].copy()
        df_can["location"] = "Canada"
        dfs.append(df_can)

    # --- 3. Load combined_us.csv ---
    if files["us"].exists():
        df_us = pd.read_csv(files["us"])
        df_us.columns = [c.strip().lower() for c in df_us.columns]
        needed = ["year", "odometer", "make", "model", "price"]
        df_us = df_us[needed].copy()
        df_us["location"] = "US"
        dfs.append(df_us)

    if not dfs:
        raise FileNotFoundError("No CSV data found in sample_data/ (cars.csv, combined_canada.csv, or combined_us.csv)")

    # --- 4. Combine all dataframes ---
    df = pd.concat(dfs, ignore_index=True)

    # --- 5. Clean and standardize ---
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["odometer"] = pd.to_numeric(df["odometer"], errors="coerce").astype("Int64")
    df["price"] = pd.to_numeric(df["price"], errors="coerce").astype(float)
    df["make"] = df["make"].astype(str).str.strip().str.title()
    df["model"] = df["model"].astype(str).str.strip().str.title()

    # Drop missing or invalid entries
    df = df.dropna(subset=["year", "odometer", "make", "model", "price"])
    df = df[(df["year"] > 1950) & (df["price"] > 500) & (df["odometer"] > 0)]

    # Remove duplicates
    df = df.drop_duplicates(subset=["year", "odometer", "make", "model", "price"])

    return df.reset_index(drop=True)

def train_model():
    """Train the RandomForest model and save it"""
    try:
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import LabelEncoder
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error

        # Load data
        df = load_or_create_sample_data()
        if df is None or df.shape[0] == 0:
            raise ValueError("No training data available.")

        # Build label encoders for make and model
        le_make = LabelEncoder()
        le_model = LabelEncoder()

        df_encoded = df.copy()

        # Fit encoders on the available make/model text
        df_encoded['make_encoded'] = le_make.fit_transform(df_encoded['make'].astype(str))
        df_encoded['model_encoded'] = le_model.fit_transform(df_encoded['model'].astype(str))

        # Features and target: use 'odometer' as the mileage column
        feature_cols = ['year', 'odometer', 'make_encoded', 'model_encoded']
        X = df_encoded[feature_cols]
        y = df_encoded['price']

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train RandomForest
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)

        # Save model and encoders
        safe_mkdir_for_path(MODEL_PATH)
        safe_mkdir_for_path(ENCODERS_PATH)

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
    if not make or not model:
        return True, None  # Can't validate empty fields

    # Try to find a matching make in CAR_MODEL_YEARS
    for known_make in CAR_MODEL_YEARS.keys():
        if known_make.lower() == make.lower():
            models_for_make = CAR_MODEL_YEARS[known_make]
            # try exact match or partial
            model_keys = list(models_for_make.keys())
            # direct match
            if model in models_for_make:
                start_year, end_year = models_for_make[model]
                if year < start_year:
                    return False, f"The {known_make} {model} was first produced in {start_year}, not {year}."
                if year > end_year:
                    return False, f"The {known_make} {model} was discontinued in {end_year}, not {year}."
                return True, None
            # try case-insensitive match
            for mk, (s, e) in models_for_make.items():
                if mk.lower() == model.lower():
                    if year < s:
                        return False, f"The {known_make} {mk} was first produced in {s}, not {year}."
                    if year > e:
                        return False, f"The {known_make} {mk} was discontinued in {e}, not {year}."
                    return True, None
            # if make found but model not, return allowed but with lower confidence
            return True, None

    # unknown make -> allow but with lower confidence
    return True, None

def apply_condition_adjustments(price, condition, accident_history):
    """Apply adjustments based on vehicle condition and accident history"""
    condition_multipliers = {
        "Excellent": 1.15,
        "Good": 1.0,
        "Fair": 0.85,
        "Poor": 0.65,
        "Parts only/Salvage": 0.15
    }
    accident_multipliers = {
        "None": 1.0,
        "Minor (1-2)": 0.92,
        "Major (3+)": 0.78,
        "Serious/Total Loss": 0.25
    }
    condition_adjusted = price * condition_multipliers.get(condition, 1.0)
    final_price = condition_adjusted * accident_multipliers.get(accident_history, 1.0)
    return final_price

def apply_regional_adjustments(price, location, currency):
    """Apply regional market adjustments and currency conversion"""
    regional_multipliers = {"US": 1.0, "Canada": 1.08}
    exchange_rates = {"USD": 1.0, "CAD": 1.35}

    adjusted_price = price * regional_multipliers.get(location, 1.0)

    if currency == "CAD" and location == "US":
        converted_price = adjusted_price * exchange_rates["CAD"]
    elif currency == "USD" and location == "Canada":
        converted_price = adjusted_price / exchange_rates["CAD"]
    else:
        converted_price = adjusted_price

    return converted_price

def convert_to_miles(mileage, unit):
    """Convert mileage to miles if needed"""
    if unit.lower() in ("km", "kilometers", "kilometres"):
        return mileage * 0.621371
    return mileage

def craigslist_search_targets(location):
    """Return Craigslist city/base URL pairs for a country or city input."""
    normalized = str(location or "").strip().lower()

    if normalized in ("canada", "ca", "cad"):
        return [
            ("vancouver", CANADIAN_CITIES["vancouver"]),
            ("toronto", CANADIAN_CITIES["toronto"]),
            ("calgary", CANADIAN_CITIES["calgary"]),
        ]

    if normalized in ("us", "usa", "united states", "united states of america", "usd"):
        return [
            ("seattle", US_CITIES["seattle"]),
            ("los angeles", US_CITIES["los angeles"]),
            ("new york", US_CITIES["new york"]),
        ]

    if normalized in CANADIAN_CITIES:
        return [(normalized, CANADIAN_CITIES[normalized])]

    if normalized in US_CITIES:
        return [(normalized, US_CITIES[normalized])]

    slug = re.sub(r"[^a-z0-9.-]", "", normalized)
    if slug:
        return [(slug, f"https://{slug}.craigslist.org")]

    return [("seattle", US_CITIES["seattle"])]

def parse_price(price_text):
    match = re.search(r"\$?\s*([\d,]+)", price_text or "")
    if not match:
        return None
    return int(match.group(1).replace(",", ""))

def parse_mileage_to_miles(text):
    text = str(text or "").lower()
    match = re.search(
        r"(\d[\d,\s]*)\s*(km|kms|kilometers|kilometres|mi|mile|miles)",
        text,
    )
    if not match:
        return None

    value = int(match.group(1).replace(",", "").replace(" ", ""))
    unit = match.group(2)
    if unit in ("km", "kms", "kilometers", "kilometres"):
        return round(convert_to_miles(value, "km"))
    return value

def clean_listing_location(value, fallback_city):
    value = str(value or "").strip().strip("()")
    lower_value = value.lower()
    if not value or "call" in lower_value or re.search(r"\d{3}", value):
        return fallback_city.title()
    return value

def scrape_listing_details(url):
    """Fetch details that often are not present on Craigslist search cards."""
    details = {}

    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        if response.status_code != 200:
            return details

        soup = BeautifulSoup(response.text, "html.parser")

        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            details["imageUrl"] = og_image["content"]
        else:
            img_tag = soup.select_one(".swipe-wrap img, img")
            if img_tag:
                details["imageUrl"] = (
                    img_tag.get("src")
                    or img_tag.get("data-src")
                    or img_tag.get("data-lazy")
                )

        title_tag = soup.find("span", id="titletextonly") or soup.find("h1")
        if title_tag:
            details["title"] = title_tag.get_text(" ", strip=True)

        price_tag = soup.find("span", class_="price")
        if price_tag:
            details["price"] = parse_price(price_tag.get_text(" ", strip=True))

        mileage = parse_mileage_to_miles(soup.get_text(" ", strip=True))
        if mileage is not None:
            details["mileage"] = mileage

    except Exception as e:
        print(f"[SCRAPER ERROR] listing detail fetch failed: {e}", file=sys.stderr)

    return details

def scrape_listing(url, city):
    """Scrape an individual Craigslist listing."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        title_el = soup.find("span", id="titletextonly") or soup.find("h1")
        title = title_el.get_text(strip=True) if title_el else "(no title)"
        title_lower = title.lower()

        if any(word in title_lower for word in ["lease", "leasing"]):
            return None

        details = {"url": url, "city": city, "title": title}

        # --- Price ---
        price_el = soup.find("span", class_="price")
        if price_el:
            price_text = re.sub(r"[^\d.]", "", price_el.get_text(strip=True))
            details["price"] = float(price_text) if price_text else None

        # --- Year, make, model ---
        important = soup.find("div", class_="attr important")
        if important:
            year_el = important.find("span", class_="valu year")
            mm_el = important.find("span", class_="valu makemodel")
            if year_el:
                details["year"] = year_el.get_text(strip=True)
            if mm_el:
                mm_text = mm_el.get_text(strip=True)
                tokens = mm_text.split()
                details["make"] = tokens[0] if len(tokens) > 0 else "?"
                details["model"] = " ".join(tokens[1:]) if len(tokens) > 1 else "?"

        # --- Odometer ---
        for div in soup.select("div.attr"):
            label = div.find("span", class_="labl")
            value = div.find("span", class_="valu")
            if not (label and value):
                continue
            label_text = label.get_text(strip=True).lower()
            value_text = value.get_text(strip=True)
            if any(word in label_text for word in ["odometer", "odomètre", "kilométrage"]):
                match = re.search(r'(\d[\d,\s]*)', value_text)
                if match:
                    details["odometer"] = int(match.group(1).replace(",", "").replace(" ", ""))

        # --- Fallback for year/make/model ---
        if "year" not in details or "make" not in details:
            match = re.match(r"(\d{4})\s+([A-Za-z]+)\s+(.*)", title)
            if match:
                details["year"], details["make"], details["model"] = match.groups()

        return details
    except Exception:
        return None


def scrape_city(base_url, city, make, model, year, sample_mode=True):
    """Scrape one Craigslist city for matching listings."""
   
    try:
        search_url = f"{base_url}/search/cta?query={make}+{model}+{year}"
        resp = requests.get(search_url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.select("a.result-title"):
            href = a.get("href")
            if href:
                full_url = href if href.startswith("http") else f"{base_url}{href}"
                links.append(full_url)

        if sample_mode:
            links = links[:5]

        results = []
        for url in links:
            # Assuming you have a scrape_listing(url, city) function already
            listing = scrape_listing(url, city)
            if listing:
                results.append(listing)
            time.sleep(1)  # polite delay to avoid hammering Craigslist

        return results

    except Exception as e:
        print(f"[{city}] Exception occurred: {e}", file=sys.stderr)
        return []



def search_marketplace_listings(make, model, year, region="canada", max_results=10):
    """
    Searches Craigslist live for matching car listings (lightweight version).
    Uses your combined_canada.csv or combined_us.csv for city base URLs.
    """
    import pandas as pd

    region_file = os.path.join(Path(__file__).parent.parent.parent, "sample_data", "combined_us.csv") if region.lower() != "canada" else os.path.join(Path(__file__).parent.parent.parent, "sample_data", "combined_canada.csv")
    try:
        df = pd.read_csv(region_file)
    except Exception:
        print(f"Could not open {region_file}", file=sys.stderr)
        return []

    if "url" not in df.columns:
        print("CSV must contain a 'url' column with base Craigslist links.", file=sys.stderr)
        return []

    listings = []
    for _, row in df.head(5).iterrows():  # only scrape first few cities for speed
        city_url = row["url"]
        city_name = row.get("city", "unknown")
        city_listings = scrape_city(city_url, city_name, make, model, year, sample_mode=True)
        listings.extend(city_listings)
        if len(listings) >= max_results:
            break
    return listings[:max_results]

def predict_price(year, odometer, odometer_unit, make, model, location="US", currency="USD", accident_history="None", condition="Good"):
    """Predict car price using trained model with all adjustments"""
    try:
        import pandas as pd

        # Basic validation
        is_valid, validation_error = validate_car_model_year(year, make, model)
        if not is_valid:
            result = {"error": "Invalid car model/year combination", "message": validation_error}
            print(json.dumps(result))
            return

        # Train model if needed
        if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODERS_PATH):
            train_model()

        with open(MODEL_PATH, 'rb') as f:
            estimator = pickle.load(f)
        with open(ENCODERS_PATH, 'rb') as f:
            encoders = pickle.load(f)

        le_make = encoders.get('make_encoder')
        le_model = encoders.get('model_encoder')

        # Encode categorical variables; handle unseen categories safely
        try:
            make_encoded = int(le_make.transform([make])[0])
        except Exception:
            # Unseen or problematic make - map to a sentinel (0) after adding if possible
            make_encoded = 0

        try:
            model_encoded = int(le_model.transform([model])[0])
        except Exception:
            model_encoded = 0

        # Convert odometer to miles if unit is not miles
        odometer_miles = convert_to_miles(odometer, odometer_unit)

        features = pd.DataFrame([{
            "year": int(year),
            "odometer": float(odometer_miles),
            "make_encoded": int(make_encoded),
            "model_encoded": int(model_encoded),
        }])
        base_prediction = float(estimator.predict(features)[0])

        # Adjustments
        condition_adjusted = apply_condition_adjustments(base_prediction, condition, accident_history)
        adjusted_prediction = apply_regional_adjustments(condition_adjusted, location, currency)

        low_estimate = adjusted_prediction * 0.85
        high_estimate = adjusted_prediction * 1.15

        if make not in CAR_MODEL_YEARS or model not in CAR_MODEL_YEARS.get(make, {}):
            confidence = "low"
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
            "accident_history": accident_history,
            "mileage_in_miles": round(odometer_miles, 0),
            "marketplace_listings": []
        }

        print(json.dumps(result))

    except Exception as e:
        print(f"Prediction failed: {e}", file=sys.stderr)
        sys.exit(1)

def get_models_for_make_and_year(make, year):
    """Get available models for a specific make and year"""
    try:
        year = int(year)
        matched_make = None
        for known in CAR_MODEL_YEARS.keys():
            if known.lower() == make.lower():
                matched_make = known
                break

        if not matched_make:
            print(json.dumps([]))
            return

        models_for_make = CAR_MODEL_YEARS[matched_make]
        available_models = []
        for model, (start_year, end_year) in models_for_make.items():
            if start_year <= year <= end_year:
                available_models.append(model)
        available_models.sort()
        print(json.dumps(available_models))

    except Exception as e:
        print(f"Failed to get models: {e}", file=sys.stderr)
        sys.exit(1)

def get_similar_listings(make, model, year, mileage, mileage_unit, location, max_results=10):
    """Search Craigslist and return listings as JSON-safe dictionaries."""
    results = []
    seen_urls = set()
    target_miles = convert_to_miles(float(mileage), mileage_unit)

    for city, base_url in craigslist_search_targets(location):
        if len(results) >= max_results:
            break

        try:
            query = quote_plus(f"{make} {model}")
            search_url = (
                f"{base_url}/search/cta?"
                f"auto_make_model={query}&"
                f"min_auto_year={quote_plus(str(year))}&"
                f"max_auto_year={quote_plus(str(year))}&"
                "hasPic=1"
            )

            response = requests.get(search_url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"[SCRAPER ERROR] {city} returned HTTP {response.status_code}", file=sys.stderr)
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            listings = soup.select("li.cl-search-result, li.cl-static-search-result, li.result-row")

            for item in listings:
                if len(results) >= max_results:
                    break

                link_tag = item.select_one("a.posting-title, a.result-title, a[href]")
                raw_url = link_tag.get("href") if link_tag and link_tag.has_attr("href") else None
                if not raw_url:
                    continue

                url = raw_url if raw_url.startswith("http") else urljoin(base_url, raw_url)
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                title_tag = item.select_one("span.label, .title, a.result-title")
                title = (
                    title_tag.get_text(" ", strip=True)
                    if title_tag
                    else item.get("title", "No title")
                )

                price_tag = item.select_one("span.priceinfo, span.result-price, .price")
                price = parse_price(price_tag.get_text(" ", strip=True) if price_tag else "")

                details_text = item.get_text(" ", strip=True)
                listing_mileage = parse_mileage_to_miles(details_text)

                location_tag = item.select_one(".location, span.result-hood")
                item_location = clean_listing_location(
                    location_tag.get_text(" ", strip=True) if location_tag else "",
                    city,
                )

                img_tag = item.find("img")
                image_url = None
                if img_tag:
                    image_url = (
                        img_tag.get("src")
                        or img_tag.get("data-src")
                        or img_tag.get("data-lazy")
                    )

                if not image_url or listing_mileage is None:
                    details = scrape_listing_details(url)
                    title = details.get("title") or title
                    price = details.get("price") if details.get("price") is not None else price
                    listing_mileage = (
                        details.get("mileage")
                        if details.get("mileage") is not None
                        else listing_mileage
                    )
                    image_url = details.get("imageUrl") or image_url

                results.append({
                    "title": title,
                    "price": price,
                    "mileage": listing_mileage,
                    "year": int(year),
                    "location": item_location,
                    "imageUrl": image_url,
                    "url": url,
                    "source": "Craigslist",
                })

        except Exception as e:
            print(f"[SCRAPER ERROR] {city}: {e}", file=sys.stderr)

    results.sort(
        key=lambda listing: (
            float("inf")
            if listing.get("mileage") is None
            else abs(float(listing["mileage"]) - target_miles)
        )
    )
    return results[:max_results]



# CLI entry point
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python car_price_model.py [train|predict|get_models] [args...]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "train":
        train_model()

    elif command == "predict":
        # Usage:
        # python car_price_model.py predict <year> <odometer> <odometer_unit> <make> <model> [location] [currency] [accident_history] [condition]
        if len(sys.argv) < 7 or len(sys.argv) > 11:
            print("Usage: python car_price_model.py predict <year> <odometer> <odometer_unit> <make> <model> [location] [currency] [accident_history] [condition]", file=sys.stderr)
            sys.exit(1)

        try:
            year = int(sys.argv[2])
            odometer = float(sys.argv[3])
            odometer_unit = sys.argv[4]
            make = sys.argv[5]
            model = sys.argv[6]
            location = sys.argv[7] if len(sys.argv) > 7 else "US"
            currency = sys.argv[8] if len(sys.argv) > 8 else "USD"
            accident_history = sys.argv[9] if len(sys.argv) > 9 else "None"
            condition = sys.argv[10] if len(sys.argv) > 10 else "Good"
        except Exception as e:
            print(f"Invalid predict args: {e}", file=sys.stderr)
            sys.exit(1)

        predict_price(year, odometer, odometer_unit, make, model, location, currency, accident_history, condition)

    elif command == "get_models":
        if len(sys.argv) != 4:
            print("Usage: python car_price_model.py get_models <make> <year>", file=sys.stderr)
            sys.exit(1)
        make = sys.argv[2]
        year = sys.argv[3]
        get_models_for_make_and_year(make, year)

    elif command == "similar":
        # Usage:
        # python car_price_model.py similar <make> <model> <year> <mileage> <mileage_unit> <location>
        if len(sys.argv) != 8:
            print("Usage: python car_price_model.py similar <make> <model> <year> <mileage> <mileage_unit> <location>", file=sys.stderr)
            sys.exit(1)

        make = sys.argv[2]
        model = sys.argv[3]
        year = sys.argv[4]
        mileage = sys.argv[5]
        mileage_unit = sys.argv[6]
        location = sys.argv[7]

        listings = get_similar_listings(make, model, year, mileage, mileage_unit, location)
        print(json.dumps(listings))

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
