import { sql } from "drizzle-orm";
import { pgTable, text, varchar, integer, real } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const cars = pgTable("cars", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  year: integer("year").notNull(),
  mileage: integer("mileage").notNull(),
  make: text("make").notNull(),
  model: text("model").notNull(),
  price: real("price").notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export const insertCarSchema = createInsertSchema(cars).omit({
  id: true,
});

export const carPredictionSchema = z.object({
  year: z.number({
    required_error: "Please enter the year of your car",
    invalid_type_error: "Year must be a valid number"
  }).int().min(1990, "Year must be 1990 or later").max(2024, "Year cannot be later than 2024"),
  
  mileage: z.number({
    required_error: "Please enter your car's mileage",
    invalid_type_error: "Mileage must be a valid number"
  }).int().min(0, "Mileage cannot be negative"),
  
  make: z.string({
    required_error: "Please select your car's make"
  }).min(1, "Please choose a car make from the dropdown"),
  
  model: z.string({
    required_error: "Please select your car's model"
  }).min(1, "Please choose a car model from the dropdown"),
  
  location: z.enum(["US", "Canada"], {
    required_error: "Please select a location"
  }).default("US"),
  
  currency: z.enum(["USD", "CAD"], {
    required_error: "Please select a currency"
  }).default("USD"),
  
  accidentHistory: z.enum(["None", "Minor (1-2)", "Major (3+)", "Serious/Total Loss"], {
    required_error: "Please select accident history"
  }).default("None"),
  
  condition: z.enum(["Excellent", "Good", "Fair", "Poor", "Parts only/Salvage"], {
    required_error: "Please select vehicle condition"
  }).default("Good"),
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
export type InsertCar = z.infer<typeof insertCarSchema>;
export type Car = typeof cars.$inferSelect;
export type CarPrediction = z.infer<typeof carPredictionSchema>;

export interface PredictionResult {
  estimated_price: number;
  low_estimate: number;
  high_estimate: number;
  confidence: string;
  currency: string;
  location: string;
  condition: string;
  accident_history: string;
}
