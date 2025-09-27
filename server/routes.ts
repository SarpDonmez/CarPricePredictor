import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { carPredictionSchema, type PredictionResult } from "@shared/schema";
import { spawn } from "child_process";
import path from "path";

export async function registerRoutes(app: Express): Promise<Server> {
  
  // Get available car makes
  app.get("/api/makes", async (req, res) => {
    try {
      const makes = await storage.getCarMakes();
      // If no makes in storage, return common makes
      if (makes.length === 0) {
        const commonMakes = [
          "Toyota", "Honda", "Ford", "Chevrolet", "Nissan", 
          "BMW", "Mercedes-Benz", "Audi", "Volkswagen", "Subaru", 
          "Mazda", "Hyundai", "Kia", "Lexus", "Acura"
        ];
        return res.json(commonMakes);
      }
      res.json(makes);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch car makes" });
    }
  });

  // Get available models filtered by make and year
  app.get("/api/models", async (req, res) => {
    try {
      const { make, year } = req.query;
      
      if (!make || !year) {
        return res.status(400).json({ message: "Make and year are required" });
      }
      
      const models = await getFilteredModels(make as string, parseInt(year as string));
      res.json(models);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch car models" });
    }
  });

  // Predict car price
  app.post("/api/predict", async (req, res) => {
    try {
      const validatedData = carPredictionSchema.parse(req.body);
      
      const prediction = await predictCarPrice(validatedData);
      res.json(prediction);
    } catch (error) {
      if (error instanceof Error) {
        res.status(400).json({ message: error.message });
      } else {
        res.status(500).json({ message: "Prediction failed" });
      }
    }
  });

  // Train model endpoint (for initial setup)
  app.post("/api/train", async (req, res) => {
    try {
      await trainModel();
      res.json({ message: "Model trained successfully" });
    } catch (error) {
      res.status(500).json({ message: "Model training failed" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}

async function predictCarPrice(carData: { year: number; mileage: number; make: string; model: string; location: string; currency: string; accidentHistory: string; condition: string }): Promise<PredictionResult> {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(process.cwd(), "server", "python", "car_price_model.py");
    const args = [
      pythonScript,
      "predict",
      carData.year.toString(),
      carData.mileage.toString(),
      carData.make,
      carData.model,
      carData.location,
      carData.currency,
      carData.accidentHistory,
      carData.condition
    ];

    const python = spawn("python3", args);
    let result = "";
    let error = "";

    python.stdout.on("data", (data) => {
      result += data.toString();
    });

    python.stderr.on("data", (data) => {
      error += data.toString();
    });

    python.on("close", (code) => {
      if (code === 0) {
        try {
          const prediction = JSON.parse(result.trim());
          // Check if the response contains a validation error
          if (prediction.error) {
            reject(new Error(prediction.message));
          } else {
            resolve(prediction);
          }
        } catch (parseError) {
          reject(new Error("Invalid prediction response"));
        }
      } else {
        reject(new Error(error || "Python script failed"));
      }
    });
  });
}

async function getFilteredModels(make: string, year: number): Promise<string[]> {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(process.cwd(), "server", "python", "car_price_model.py");
    const args = [pythonScript, "get_models", make, year.toString()];
    
    const python = spawn("python3", args);
    let result = "";
    let error = "";

    python.stdout.on("data", (data) => {
      result += data.toString();
    });

    python.stderr.on("data", (data) => {
      error += data.toString();
    });

    python.on("close", (code) => {
      if (code === 0) {
        try {
          const models = JSON.parse(result.trim());
          resolve(models);
        } catch (parseError) {
          reject(new Error("Invalid models response"));
        }
      } else {
        reject(new Error(error || "Failed to get models"));
      }
    });
  });
}

async function trainModel(): Promise<void> {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(process.cwd(), "server", "python", "car_price_model.py");
    const python = spawn("python3", [pythonScript, "train"]);
    
    let error = "";

    python.stderr.on("data", (data) => {
      error += data.toString();
    });

    python.on("close", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(error || "Model training failed"));
      }
    });
  });
}
