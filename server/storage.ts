import { type User, type InsertUser, type Car, type InsertCar } from "@shared/schema";
import { randomUUID } from "crypto";

export interface IStorage {
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  getCars(): Promise<Car[]>;
  createCar(car: InsertCar): Promise<Car>;
  getCarMakes(): Promise<string[]>;
}

export class MemStorage implements IStorage {
  private users: Map<string, User>;
  private cars: Map<string, Car>;

  constructor() {
    this.users = new Map();
    this.cars = new Map();
  }

  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async getCars(): Promise<Car[]> {
    return Array.from(this.cars.values());
  }

  async createCar(insertCar: InsertCar): Promise<Car> {
    const id = randomUUID();
    const car: Car = { ...insertCar, id };
    this.cars.set(id, car);
    return car;
  }

  async getCarMakes(): Promise<string[]> {
    const makes = Array.from(this.cars.values()).map(car => car.make);
    return [...new Set(makes)].sort();
  }
}

export const storage = new MemStorage();
