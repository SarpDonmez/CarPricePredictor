import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic, log } from "./vite";
import { spawn } from "child_process";

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// Logging middleware
app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }

      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "…";
      }

      log(logLine);
    }
  });

  next();
});

(async () => {

  /*
  ----------------------------------------------------
  FIX: REGISTER SIMILAR-LISTINGS ROUTE FIRST
  ----------------------------------------------------
  */
  app.post("/api/similar-listings", async (req, res) => {
    const { make, model, year, mileage, location } = req.body;

    const py = spawn("python3", [
      "server/python/car_price_model.py",
      "similar",
      make,
      model,
      year.toString(),
      mileage.toString(),
      location
    ]);

    let output = "";
    py.stdout.on("data", (data) => (output += data.toString()));

    py.on("close", () => {
      try {
        res.json(JSON.parse(output));
      } catch (err) {
        res.status(500).json({ error: "Failed to parse scraper response" });
      }
    });
  });

  // Register the rest of the API
  const server = await registerRoutes(app);

  // Error handler
  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";
    res.status(status).json({ message });
    throw err;
  });

  // Vite or static
  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app); // this no longer overrides your API
  }

  const port = parseInt(process.env.PORT || "3001", 10);
  server.listen(port, "localhost", () => {
    log(`serving on http://localhost:${port}`);
  });
})();
