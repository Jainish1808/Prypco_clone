import { randomUUID } from "crypto";
import session from "express-session";
import createMemoryStore from "memorystore";
import type { 
  User, 
  InsertUser, 
  Property, 
  InsertProperty, 
  Transaction, 
  InsertTransaction,
  Holding,
  InsertHolding,
  MarketOrder,
  InsertMarketOrder,
  IncomeDistribution,
  InsertIncomeDistribution
} from "@shared/schema";

const MemoryStore = createMemoryStore(session);

export interface IStorage {
  sessionStore: any;
  
  // User methods
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  getUserByEmail(email: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  updateUser(id: string, updates: Partial<User>): Promise<User | undefined>;
  
  // Property methods
  getProperty(id: string): Promise<Property | undefined>;
  getProperties(filters?: { 
    status?: string; 
    sellerId?: string; 
    propertyType?: string;
    limit?: number;
    offset?: number;
  }): Promise<Property[]>;
  createProperty(property: InsertProperty & { totalTokens: number; tokenPrice: number }): Promise<Property>;
  updateProperty(id: string, updates: Partial<Property>): Promise<Property | undefined>;
  
  // Transaction methods
  getTransaction(id: string): Promise<Transaction | undefined>;
  getTransactions(filters?: { 
    userId?: string; 
    propertyId?: string; 
    type?: string;
    limit?: number;
    offset?: number;
  }): Promise<Transaction[]>;
  createTransaction(transaction: InsertTransaction): Promise<Transaction>;
  updateTransaction(id: string, updates: Partial<Transaction>): Promise<Transaction | undefined>;
  
  // Holdings methods
  getHolding(userId: string, propertyId: string): Promise<Holding | undefined>;
  getUserHoldings(userId: string): Promise<Holding[]>;
  getPropertyHoldings(propertyId: string): Promise<Holding[]>;
  createOrUpdateHolding(holding: InsertHolding): Promise<Holding>;
  
  // Market Order methods
  getMarketOrders(filters?: {
    propertyId?: string;
    orderType?: "buy" | "sell";
    status?: string;
    limit?: number;
  }): Promise<MarketOrder[]>;
  createMarketOrder(order: InsertMarketOrder): Promise<MarketOrder>;
  updateMarketOrder(id: string, updates: Partial<MarketOrder>): Promise<MarketOrder | undefined>;
  
  // Income Distribution methods
  getIncomeDistributions(propertyId?: string): Promise<IncomeDistribution[]>;
  createIncomeDistribution(distribution: InsertIncomeDistribution): Promise<IncomeDistribution>;
  updateIncomeDistribution(id: string, updates: Partial<IncomeDistribution>): Promise<IncomeDistribution | undefined>;
}

export class MemStorage implements IStorage {
  private users: Map<string, User> = new Map();
  private properties: Map<string, Property> = new Map();
  private transactions: Map<string, Transaction> = new Map();
  private holdings: Map<string, Holding> = new Map();
  private marketOrders: Map<string, MarketOrder> = new Map();
  private incomeDistributions: Map<string, IncomeDistribution> = new Map();
  
  public sessionStore: any;

  constructor() {
    this.sessionStore = new MemoryStore({
      checkPeriod: 86400000,
    });
  }

  // User methods
  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(user => user.username === username);
  }

  async getUserByEmail(email: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(user => user.email === email);
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { 
      ...insertUser, 
      id,
      createdAt: new Date()
    };
    this.users.set(id, user);
    return user;
  }

  async updateUser(id: string, updates: Partial<User>): Promise<User | undefined> {
    const user = this.users.get(id);
    if (!user) return undefined;
    
    const updatedUser = { ...user, ...updates };
    this.users.set(id, updatedUser);
    return updatedUser;
  }

  // Property methods
  async getProperty(id: string): Promise<Property | undefined> {
    return this.properties.get(id);
  }

  async getProperties(filters: { 
    status?: string; 
    sellerId?: string; 
    propertyType?: string;
    limit?: number;
    offset?: number;
  } = {}): Promise<Property[]> {
    let properties = Array.from(this.properties.values());
    
    if (filters.status) {
      properties = properties.filter(p => p.status === filters.status);
    }
    if (filters.sellerId) {
      properties = properties.filter(p => p.sellerId === filters.sellerId);
    }
    if (filters.propertyType) {
      properties = properties.filter(p => p.propertyType === filters.propertyType);
    }
    
    properties = properties.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
    
    if (filters.offset) {
      properties = properties.slice(filters.offset);
    }
    if (filters.limit) {
      properties = properties.slice(0, filters.limit);
    }
    
    return properties;
  }

  async createProperty(property: InsertProperty & { totalTokens: number; tokenPrice: number }): Promise<Property> {
    const id = randomUUID();
    const newProperty: Property = {
      ...property,
      id,
      tokensAvailable: property.totalTokens,
      tokensSold: 0,
      createdAt: new Date()
    };
    this.properties.set(id, newProperty);
    return newProperty;
  }

  async updateProperty(id: string, updates: Partial<Property>): Promise<Property | undefined> {
    const property = this.properties.get(id);
    if (!property) return undefined;
    
    const updatedProperty = { ...property, ...updates };
    this.properties.set(id, updatedProperty);
    return updatedProperty;
  }

  // Transaction methods
  async getTransaction(id: string): Promise<Transaction | undefined> {
    return this.transactions.get(id);
  }

  async getTransactions(filters: { 
    userId?: string; 
    propertyId?: string; 
    type?: string;
    limit?: number;
    offset?: number;
  } = {}): Promise<Transaction[]> {
    let transactions = Array.from(this.transactions.values());
    
    if (filters.userId) {
      transactions = transactions.filter(t => t.userId === filters.userId);
    }
    if (filters.propertyId) {
      transactions = transactions.filter(t => t.propertyId === filters.propertyId);
    }
    if (filters.type) {
      transactions = transactions.filter(t => t.type === filters.type);
    }
    
    transactions = transactions.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
    
    if (filters.offset) {
      transactions = transactions.slice(filters.offset);
    }
    if (filters.limit) {
      transactions = transactions.slice(0, filters.limit);
    }
    
    return transactions;
  }

  async createTransaction(transaction: InsertTransaction): Promise<Transaction> {
    const id = randomUUID();
    const newTransaction: Transaction = {
      ...transaction,
      id,
      createdAt: new Date()
    };
    this.transactions.set(id, newTransaction);
    return newTransaction;
  }

  async updateTransaction(id: string, updates: Partial<Transaction>): Promise<Transaction | undefined> {
    const transaction = this.transactions.get(id);
    if (!transaction) return undefined;
    
    const updatedTransaction = { ...transaction, ...updates };
    this.transactions.set(id, updatedTransaction);
    return updatedTransaction;
  }

  // Holdings methods
  async getHolding(userId: string, propertyId: string): Promise<Holding | undefined> {
    const key = `${userId}-${propertyId}`;
    return this.holdings.get(key);
  }

  async getUserHoldings(userId: string): Promise<Holding[]> {
    return Array.from(this.holdings.values()).filter(h => h.userId === userId);
  }

  async getPropertyHoldings(propertyId: string): Promise<Holding[]> {
    return Array.from(this.holdings.values()).filter(h => h.propertyId === propertyId);
  }

  async createOrUpdateHolding(holding: InsertHolding): Promise<Holding> {
    const key = `${holding.userId}-${holding.propertyId}`;
    const existing = this.holdings.get(key);
    
    if (existing) {
      // Update existing holding
      const totalTokens = existing.tokenAmount + holding.tokenAmount;
      const totalInvested = existing.totalInvested + holding.totalInvested;
      const averagePurchasePrice = totalInvested / totalTokens;
      
      const updated: Holding = {
        ...existing,
        tokenAmount: totalTokens,
        totalInvested,
        averagePurchasePrice,
        lastUpdated: new Date()
      };
      
      this.holdings.set(key, updated);
      return updated;
    } else {
      // Create new holding
      const id = randomUUID();
      const newHolding: Holding = {
        ...holding,
        id,
        averagePurchasePrice: holding.totalInvested / holding.tokenAmount,
        lastUpdated: new Date()
      };
      
      this.holdings.set(key, newHolding);
      return newHolding;
    }
  }

  // Market Order methods
  async getMarketOrders(filters: {
    propertyId?: string;
    orderType?: "buy" | "sell";
    status?: string;
    limit?: number;
  } = {}): Promise<MarketOrder[]> {
    let orders = Array.from(this.marketOrders.values());
    
    if (filters.propertyId) {
      orders = orders.filter(o => o.propertyId === filters.propertyId);
    }
    if (filters.orderType) {
      orders = orders.filter(o => o.orderType === filters.orderType);
    }
    if (filters.status) {
      orders = orders.filter(o => o.status === filters.status);
    }
    
    orders = orders.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
    
    if (filters.limit) {
      orders = orders.slice(0, filters.limit);
    }
    
    return orders;
  }

  async createMarketOrder(order: InsertMarketOrder): Promise<MarketOrder> {
    const id = randomUUID();
    const newOrder: MarketOrder = {
      ...order,
      id,
      createdAt: new Date()
    };
    this.marketOrders.set(id, newOrder);
    return newOrder;
  }

  async updateMarketOrder(id: string, updates: Partial<MarketOrder>): Promise<MarketOrder | undefined> {
    const order = this.marketOrders.get(id);
    if (!order) return undefined;
    
    const updatedOrder = { ...order, ...updates };
    this.marketOrders.set(id, updatedOrder);
    return updatedOrder;
  }

  // Income Distribution methods
  async getIncomeDistributions(propertyId?: string): Promise<IncomeDistribution[]> {
    let distributions = Array.from(this.incomeDistributions.values());
    
    if (propertyId) {
      distributions = distributions.filter(d => d.propertyId === propertyId);
    }
    
    return distributions.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async createIncomeDistribution(distribution: InsertIncomeDistribution): Promise<IncomeDistribution> {
    const id = randomUUID();
    const newDistribution: IncomeDistribution = {
      ...distribution,
      id,
      createdAt: new Date()
    };
    this.incomeDistributions.set(id, newDistribution);
    return newDistribution;
  }

  async updateIncomeDistribution(id: string, updates: Partial<IncomeDistribution>): Promise<IncomeDistribution | undefined> {
    const distribution = this.incomeDistributions.get(id);
    if (!distribution) return undefined;
    
    const updatedDistribution = { ...distribution, ...updates };
    this.incomeDistributions.set(id, updatedDistribution);
    return updatedDistribution;
  }
}

export const storage = new MemStorage();
