# Car Price Predictor

## Overview

Car Price Predictor is a full-stack web application that estimates the market value of used vehicles using a machine learning model trained on historical listing data. The application allows users to enter vehicle information, receive an estimated price range, and compare the estimate with similar listings scraped from Craigslist.

This project was developed to gain experience with machine learning, full-stack web development, and integrating Python-based models into a modern web application.

---

## Features

* Estimates used vehicle prices using a Random Forest regression model
* Supports predictions based on:

  * Year
  * Make
  * Model
  * Mileage
  * Vehicle condition
  * Accident history
  * Country (United States or Canada)
* Provides estimated price ranges and confidence levels
* Retrieves similar live vehicle listings from Craigslist
* Validates vehicle model production years
* Supports both USD and CAD pricing

---

## Technology Stack

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS

### Backend

* Node.js
* Express
* TypeScript

### Machine Learning

* Python
* Scikit-learn
* Pandas

### Web Scraping

* BeautifulSoup
* Requests

---

## Project Architecture

The application consists of three primary components:

1. **Frontend**

   * Collects vehicle information from the user.
   * Displays predicted prices and comparable listings.

2. **Backend API**

   * Processes incoming requests.
   * Validates user input.
   * Launches the Python prediction engine.
   * Returns prediction results to the frontend.

3. **Machine Learning Engine**

   * Loads a trained Random Forest regression model.
   * Encodes categorical features such as make and model.
   * Predicts a vehicle's estimated market value.
   * Applies adjustments based on condition, accident history, region, and currency.

---

## Machine Learning Model

The prediction model is trained using historical used vehicle listings.

### Features

* Vehicle year
* Mileage
* Make
* Model

Following prediction, the estimated price is adjusted using:

* Vehicle condition
* Accident history
* Regional pricing differences
* Currency conversion

The model also performs validation to ensure that selected vehicle models were produced during the specified model year.

---

## Similar Listing Search

To provide additional market context, the application searches Craigslist for comparable vehicles using the selected make, model, year, and location. Returned listings include pricing, mileage, images (when available), and direct links to the original listings.

---

## Project Structure

```text
CarPricePredictor/

├── client/                 # React frontend
├── server/
│   ├── python/
│   │   ├── car_price_model.py
│   │   ├── car_price_model.pkl
│   │   └── label_encoders.pkl
│   ├── routes.ts
│   └── index.ts
├── sample_data/
├── package.json
└── README.md
```

---

## Disclaimer

This project was developed for educational purposes with the utalization of various LLMs. Price estimates are generated using historical data and machine learning techniques and should not be considered professional vehicle appraisals.
