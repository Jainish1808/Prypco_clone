import { z } from "zod";

// User Schema
export const userSchema = z.object({
  id: z.string(),
  username: z.string().min(3),
  email: z.string().email(),
  password: z.string(),
  firstName: z.string(),
  lastName: z.string(),
  walletAddress: z.string().optional(),
  isKYCVerified: z.boolean().default(false),
  userType: z.enum(["investor", "seller"]).default("investor"),
  createdAt: z.date().default(() => new Date()),
});

export const insertUserSchema = userSchema.omit({ id: true, createdAt: true });

export type User = z.infer<typeof userSchema>;
export type InsertUser = z.infer<typeof insertUserSchema>;

// Property Schema
export const propertySchema = z.object({
  id: z.string(),
  sellerId: z.string(),
  name: z.string(),
  description: z.string(),
  address: z.string(),
  propertyType: z.enum(["residential", "commercial", "mixed"]),
  propertyValue: z.number().positive(),
  propertySize: z.number().positive(), // in square meters
  expectedYield: z.number().positive(),
  monthlyRent: z.number().positive().optional(),
  yearBuilt: z.number().optional(),
  units: z.number().default(1),
  propertyManager: z.string().optional(),
  occupancyStatus: z.enum(["occupied", "vacant", "partially-occupied"]),
  
  // Tokenization details
  totalTokens: z.number().positive(),
  tokenPrice: z.number().positive(),
  tokensAvailable: z.number().min(0),
  tokensSold: z.number().min(0).default(0),
  
  // Status and approval
  status: z.enum(["pending", "approved", "rejected", "listed"]).default("pending"),
  approvedAt: z.date().optional(),
  listedAt: z.date().optional(),
  
  // Documents and media
  images: z.array(z.string()).default([]),
  documents: z.array(z.object({
    type: z.string(),
    filename: z.string(),
    url: z.string(),
  })).default([]),
  
  createdAt: z.date().default(() => new Date()),
});

export const insertPropertySchema = propertySchema.omit({ 
  id: true, 
  createdAt: true,
  totalTokens: true,
  tokenPrice: true,
  tokensAvailable: true,
  tokensSold: true,
  approvedAt: true,
  listedAt: true,
});

export type Property = z.infer<typeof propertySchema>;
export type InsertProperty = z.infer<typeof insertPropertySchema>;

// Transaction Schema
export const transactionSchema = z.object({
  id: z.string(),
  userId: z.string(),
  propertyId: z.string(),
  type: z.enum(["purchase", "sale", "income_distribution", "secondary_market"]),
  tokenAmount: z.number().positive(),
  pricePerToken: z.number().positive(),
  totalAmount: z.number().positive(),
  xrpTxHash: z.string().optional(),
  status: z.enum(["pending", "completed", "failed"]).default("pending"),
  createdAt: z.date().default(() => new Date()),
});

export const insertTransactionSchema = transactionSchema.omit({ id: true, createdAt: true });

export type Transaction = z.infer<typeof transactionSchema>;
export type InsertTransaction = z.infer<typeof transactionSchema>;

// Holdings Schema
export const holdingSchema = z.object({
  id: z.string(),
  userId: z.string(),
  propertyId: z.string(),
  tokenAmount: z.number().min(0),
  averagePurchasePrice: z.number().positive(),
  totalInvested: z.number().positive(),
  lastUpdated: z.date().default(() => new Date()),
});

export const insertHoldingSchema = holdingSchema.omit({ id: true, lastUpdated: true });

export type Holding = z.infer<typeof holdingSchema>;
export type InsertHolding = z.infer<typeof insertHoldingSchema>;

// Market Order Schema
export const marketOrderSchema = z.object({
  id: z.string(),
  userId: z.string(),
  propertyId: z.string(),
  orderType: z.enum(["buy", "sell"]),
  tokenAmount: z.number().positive(),
  pricePerToken: z.number().positive(),
  status: z.enum(["active", "filled", "cancelled"]).default("active"),
  createdAt: z.date().default(() => new Date()),
});

export const insertMarketOrderSchema = marketOrderSchema.omit({ id: true, createdAt: true });

export type MarketOrder = z.infer<typeof marketOrderSchema>;
export type InsertMarketOrder = z.infer<typeof insertMarketOrderSchema>;

// Income Distribution Schema
export const incomeDistributionSchema = z.object({
  id: z.string(),
  propertyId: z.string(),
  totalIncome: z.number().positive(),
  distributionDate: z.date().default(() => new Date()),
  distributionPerToken: z.number().positive(),
  recipients: z.array(z.object({
    userId: z.string(),
    tokenAmount: z.number().positive(),
    incomeAmount: z.number().positive(),
  })),
  status: z.enum(["calculated", "distributed"]).default("calculated"),
  createdAt: z.date().default(() => new Date()),
});

export const insertIncomeDistributionSchema = incomeDistributionSchema.omit({ id: true, createdAt: true });

export type IncomeDistribution = z.infer<typeof incomeDistributionSchema>;
export type InsertIncomeDistribution = z.infer<typeof insertIncomeDistributionSchema>;
