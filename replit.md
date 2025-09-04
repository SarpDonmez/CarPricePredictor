# Used Car Price Estimator

## Overview

This is a fullstack web application that uses machine learning to estimate used car prices. The application combines a React frontend with a Node.js/Express backend that integrates with Python scikit-learn for machine learning predictions. Users can input car details (year, mileage, make, model) and receive instant price estimates with confidence ranges powered by a RandomForestRegressor model.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React with TypeScript for type safety and better development experience
- **Styling**: Tailwind CSS with shadcn/ui component library for consistent, modern UI components
- **State Management**: TanStack Query for API state management, caching, and server synchronization
- **Routing**: Wouter as a lightweight client-side routing solution
- **Build Tool**: Vite for fast development and optimized production builds

### Backend Architecture
- **Runtime**: Node.js with Express.js framework for RESTful API endpoints
- **Language Integration**: Python subprocess integration for machine learning model execution
- **Data Storage**: In-memory storage using Map data structures for demo purposes, with Drizzle ORM configured for potential PostgreSQL integration
- **Model Persistence**: Trained ML models saved as .pkl files for fast loading and predictions

### API Design
- **RESTful Endpoints**: 
  - GET `/api/makes` - Retrieves available car manufacturers
  - POST `/api/predict` - Accepts car details and returns price prediction
  - POST `/api/train` - Triggers model training (for initial setup)
- **Data Validation**: Zod schemas for runtime type checking and API request validation
- **Error Handling**: Centralized error handling middleware with structured error responses

### Machine Learning Pipeline
- **Algorithm**: RandomForestRegressor for robust price predictions with confidence intervals
- **Data Processing**: Pandas for data manipulation and preprocessing
- **Feature Engineering**: Label encoding for categorical variables (make, model)
- **Model Training**: scikit-learn with train/test split for model validation
- **Prediction Output**: Estimated price with low/high confidence bounds

### Development Environment
- **Monorepo Structure**: Single repository with shared TypeScript schemas between frontend and backend
- **Hot Reloading**: Vite development server with HMR for frontend, tsx for backend development
- **Type Safety**: Shared types and schemas ensure consistency across the full stack

## External Dependencies

### Frontend Dependencies
- **UI Components**: Radix UI primitives via shadcn/ui for accessible, customizable components
- **HTTP Client**: Native fetch API with custom wrapper for API communication
- **Form Management**: React Hook Form with Zod resolvers for type-safe form validation
- **Icons**: Lucide React for consistent iconography

### Backend Dependencies
- **Web Framework**: Express.js for HTTP server and middleware
- **Database ORM**: Drizzle ORM configured for PostgreSQL (with @neondatabase/serverless for cloud database)
- **Process Management**: Node.js child_process for Python script execution
- **Session Management**: Connect-pg-simple for PostgreSQL session storage

### Python/ML Dependencies
- **Machine Learning**: scikit-learn for RandomForestRegressor and preprocessing utilities
- **Data Analysis**: pandas for data manipulation and CSV handling
- **Numerical Computing**: numpy for mathematical operations and array handling
- **Model Persistence**: pickle for saving and loading trained models

### Development Tools
- **Build System**: Vite with React plugin and TypeScript support
- **Code Quality**: TypeScript compiler for static type checking
- **Database Migrations**: Drizzle Kit for schema management and migrations
- **Development Server**: tsx for running TypeScript files directly in development

### Cloud/Deployment
- **Database Provider**: Neon (serverless PostgreSQL) for production database
- **Asset Handling**: Vite's asset pipeline for optimized static file serving
- **Environment Configuration**: Environment variables for database URLs and API keys