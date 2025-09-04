# Used Car Price Estimator

A fullstack web application that uses machine learning to estimate used car prices. Built with React, Node.js, and Python scikit-learn.

## Features

- **Machine Learning Price Prediction**: RandomForestRegressor model trained on car sales data
- **Interactive Web Interface**: Clean, modern UI for entering car details
- **Real-time Estimates**: Get instant price predictions with confidence ranges
- **Custom Dataset Support**: Upload your own CSV data for training
- **Persistent Model**: Trained model saved as .pkl file for fast predictions

## Tech Stack

### Frontend
- React with TypeScript
- Tailwind CSS + shadcn/ui components
- TanStack Query for API state management
- Wouter for routing

### Backend
- Node.js with Express
- Python integration via subprocess
- scikit-learn for machine learning
- In-memory storage for demo data

## Getting Started

### Prerequisites

- Node.js 18+ 
- Python 3.8+
- pip package manager

### Installation

1. Install Python dependencies:
```bash
cd server/python
pip install -r requirements.txt
