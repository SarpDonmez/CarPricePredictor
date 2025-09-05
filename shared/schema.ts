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
  year: z.number().int().min(1990).max(2024),
  mileage: z.number().int().min(0),
  make: z.string().min(1),
  model: z.string().min(1),
  location: z.enum(["US", "Canada"]).default("US"),
  currency: z.enum(["USD", "CAD"]).default("USD"),
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
}
