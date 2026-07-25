import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { carPredictionSchema, type PredictionResult } from "@shared/schema";
import { spawn } from "child_process";
import { z } from "zod";
import path from "path";
import fs from "fs";

const similarListingsSchema = z.object({
  year: z.coerce.number().int().min(1900).max(2030),
  mileage: z.coerce.number().min(0),
  mileageUnit: z.enum(["miles", "km"]).default("miles"),
  make: z.string().min(1),
  model: z.string().min(1),
  location: z.string().min(1).default("US"),
});

type SimilarListingsRequest = z.infer<typeof similarListingsSchema>;

function getPythonCommand() {
  if (process.env.PYTHON_BIN) {
    return process.env.PYTHON_BIN;
  }

  const venvPython = path.join(process.cwd(), ".venv", "bin", "python");
  return fs.existsSync(venvPython) ? venvPython : "python3";
}

export async function registerRoutes(app: Express): Promise<Server> {

  // -----------------------------
  // Get available car makes
  // -----------------------------
  app.get("/api/makes", async (_req, res) => {
    try {
      const makes = await storage.getCarMakes();

      if (makes.length === 0) {
        const commonMakes = [
          "Toyota","Honda","Ford","Chevrolet","Nissan","BMW","Mercedes-Benz",
          "Audi","Volkswagen","Subaru","Mazda","Hyundai","Kia","Tesla","Rivian",
          "Lucid","Polestar","Fisker","NIO","BYD","Xpeng","Volvo","Genesis"
        ];
        return res.json(commonMakes);
      }
      res.json(makes);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch car makes" });
    }
  });

  // -----------------------------
  // Get models filtered by make and year
  // -----------------------------
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

  // -----------------------------
  // Predict car price
  // -----------------------------
  app.post("/api/predict", async (req, res) => {
    try {
      // Validate request and allow optional link/image
      const validatedData = carPredictionSchema
        .extend({ link: z.string().optional(), image: z.string().optional() })
        .parse(req.body);
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

  // -----------------------------
  // Train model
  // -----------------------------
  app.post("/api/train", async (_req, res) => {
    try {
      await trainModel();
      res.json({ message: "Model trained successfully" });
    } catch (error) {
      res.status(500).json({ message: "Model training failed" });
    }
  });

  // -----------------------------
  // Get similar listings from Craigslist
  // -----------------------------
  app.post("/api/similar-listings", async (req, res) => {
    try {
      const request = similarListingsSchema.parse(req.body);
      const listings = await getSimilarListings(request);
      res.json(listings);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: error.message });
      }
      res.status(500).json({ message: "Failed to fetch similar listings" });
    }
  });

  // -----------------------------
  // Create HTTP server
  // -----------------------------
  const httpServer = createServer(app);
  return httpServer;
}

// -----------------------------
// Helper: Get similar listings
// -----------------------------
async function getSimilarListings(carData: SimilarListingsRequest): Promise<unknown[]> {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(process.cwd(), "server", "python", "car_price_model.py");
    const python = spawn(getPythonCommand(), [
      pythonScript,
      "similar",
      carData.make,
      carData.model,
      carData.year.toString(),
      carData.mileage.toString(),
      carData.mileageUnit,
      carData.location,
    ]);

    let result = "";
    let error = "";
    let timedOut = false;

    const timeout = setTimeout(() => {
      timedOut = true;
      python.kill("SIGTERM");
    }, 20000);

    python.stdout.on("data", (data) => { result += data.toString(); });
    python.stderr.on("data", (data) => { error += data.toString(); });

    python.on("close", (code) => {
      clearTimeout(timeout);

      if (timedOut) {
        reject(new Error("Similar listings request timed out"));
        return;
      }

      if (code !== 0) {
        reject(new Error(error || "Similar listings script failed"));
        return;
      }

      try {
        const listings = JSON.parse(result.trim() || "[]");
        if (!Array.isArray(listings)) {
          reject(new Error("Similar listings response was not an array"));
          return;
        }
        resolve(listings);
      } catch {
        reject(new Error(error || "Invalid similar listings response"));
      }
    });
  });
}

// -----------------------------
// Helper: Predict car price
// -----------------------------
async function predictCarPrice(carData: any): Promise<PredictionResult> {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(process.cwd(), "server", "python", "car_price_model.py");
    const args = [
      pythonScript,
      "predict",
      carData.year.toString(),
      carData.mileage.toString(),
      carData.mileageUnit,
      carData.make,
      carData.model,
      carData.location,
      carData.currency,
      carData.accidentHistory,
      carData.condition
    ];

    const python = spawn(getPythonCommand(), args);
    let result = "";
    let error = "";

    python.stdout.on("data", (data) => { result += data.toString(); });
    python.stderr.on("data", (data) => { error += data.toString(); });

    python.on("close", (code) => {
      if (code === 0) {
        try {
          const prediction = JSON.parse(result.trim());
          if (prediction.error) reject(new Error(prediction.message));
          else resolve(prediction);
        } catch {
          reject(new Error("Invalid prediction response"));
        }
      } else {
        reject(new Error(error || "Python script failed"));
      }
    });
  });
}

// -----------------------------
// Helper: Get filtered models
// -----------------------------
async function getFilteredModels(make: string, year: number): Promise<string[]> {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(process.cwd(), "server", "python", "car_price_model.py");
    const args = [pythonScript, "get_models", make, year.toString()];

    const python = spawn(getPythonCommand(), args);
    let result = "";
    let error = "";

    python.stdout.on("data", (data) => { result += data.toString(); });
    python.stderr.on("data", (data) => { error += data.toString(); });

    python.on("close", (code) => {
      if (code === 0) {
        try { resolve(JSON.parse(result.trim())); }
        catch { reject(new Error("Invalid models response")); }
      } else { reject(new Error(error || "Failed to get models")); }
    });
  });
}

// -----------------------------
// Helper: Train model
// -----------------------------
async function trainModel(): Promise<void> {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(process.cwd(), "server", "python", "car_price_model.py");
    const python = spawn(getPythonCommand(), [pythonScript, "train"]);

    let error = "";
    python.stderr.on("data", (data) => { error += data.toString(); });

    python.on("close", (code) => {
      if (code === 0) resolve();
      else reject(new Error(error || "Model training failed"));
    });
  });
}
