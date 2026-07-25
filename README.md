# Car Price Predictor

A full-stack web application that uses machine learning to estimate the market value of used vehicles. The project combines a React and TypeScript frontend with a Node.js backend and a Python machine learning pipeline built using scikit-learn.

The goal of this project was to create a practical tool that helps users estimate a reasonable selling price for a used vehicle based on real-world factors such as year, mileage, make, model, location, vehicle condition, and accident history.

## Features

### Machine Learning Price Prediction
- Uses a RandomForestRegressor machine learning model trained on real vehicle sales data.
- Predicts used vehicle prices using important features including:
  - Vehicle year
  - Mileage/odometer reading
  - Manufacturer
  - Vehicle model
- Provides estimated prices with confidence ranges to account for market variation.
- Trained models are generated locally and excluded from version control due to their large file size.

### Vehicle Data Processing
- Supports both US and Canadian vehicle markets.
- Handles different mileage units and converts values when necessary.
- Validates vehicle year and model combinations to reduce unrealistic predictions.
- Applies additional adjustments based on:
  - Vehicle condition
  - Accident history
  - Regional market differences
  - Currency conversion

### Marketplace Comparison
- Includes functionality to find similar vehicle listings for additional market context.
- Compares vehicles based on:
  - Make and model
  - Year
  - Mileage
  - Location
- Provides users with more information than a single predicted price.

### Web Application
- Interactive interface for entering vehicle information.
- Provides real-time price estimates through a user-friendly frontend.
- Connects a machine learning model with a complete full-stack application.

## Dataset

The model was trained using a combination of vehicle listing datasets containing over **437,000 vehicle records**.

The data preparation pipeline includes:
- Cleaning and standardizing vehicle information
- Separating combined make/model data
- Removing invalid listings
- Handling missing values
- Preparing structured data for machine learning training

## Tech Stack

### Frontend
- React with TypeScript
- Tailwind CSS
- shadcn/ui components
- TanStack Query for API state management
- Wouter for routing

### Backend
- Node.js with Express
- REST API architecture
- Python integration through subprocess communication

### Machine Learning
- Python
- scikit-learn
- pandas
- RandomForestRegressor
- Label encoding for categorical vehicle data

## Project Structure

```
CarPricePredictor/
│
├── client/              # React frontend
├── server/              # Express backend
│   └── python/          # Machine learning pipeline
├── sample_data/         # Training datasets
└── shared/              # Shared TypeScript schemas
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.8+
- pip package manager

### Installation

Clone the repository:

```bash
git clone https://github.com/SarpDonmez/CarPricePredictor.git
cd CarPricePredictor
```

Install JavaScript dependencies:

```bash
npm install
```

Install Python dependencies:

```bash
cd server/python
pip install -r requirements.txt
```

### Training the Model

The machine learning model can be trained locally using:

```bash
python car_price_model.py train
```

This generates the trained model files locally.

### Running the Application

Start the development server:

```bash
npm run dev
```

The application will open in your browser and allow users to enter vehicle information and receive price predictions.

## Future Improvements

Possible improvements for future versions include:

- Training more advanced machine learning models
- Adding additional vehicle features such as trim level, engine type, and transmission
- Improving prediction accuracy with more market data
- Deploying the application publicly
- Adding user accounts and saved vehicle estimates

## What I Learned

Building this project helped me gain experience with:

- Connecting a machine learning model to a full-stack web application
- Designing communication between different programming languages
- Cleaning and preparing large real-world datasets
- Building and evaluating machine learning pipelines
- Developing frontend applications with React and TypeScript
- Creating backend APIs using Node.js and Express
- Using Git and GitHub for version control and project documentation
