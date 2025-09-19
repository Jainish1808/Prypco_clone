import type { Express } from "express";
import { createServer, type Server } from "http";
import { setupAuth } from "./auth";
import { storage } from "./storage";
import { tokenizationService } from "./services/tokenization";
import { TokenCalculations } from "./services/calculations";
import { insertPropertySchema, insertMarketOrderSchema } from "@shared/schema";

export async function registerRoutes(app: Express): Promise<Server> {
  // Setup authentication routes
  setupAuth(app);

  // Property Endpoints (For Investors)
  
  // GET /api/properties - List all approved properties
  app.get("/api/properties", async (req, res) => {
    try {
      const { type, limit, offset } = req.query;
      const properties = await storage.getProperties({
        status: "listed",
        propertyType: type as string,
        limit: limit ? parseInt(limit as string) : undefined,
        offset: offset ? parseInt(offset as string) : undefined
      });
      res.json(properties);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch properties", error });
    }
  });

  // GET /api/properties/:id - Get specific property details
  app.get("/api/properties/:id", async (req, res) => {
    try {
      const property = await storage.getProperty(req.params.id);
      if (!property) {
        return res.status(404).json({ message: "Property not found" });
      }
      res.json(property);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch property", error });
    }
  });

  // POST /api/properties/:id/invest - Initiate token purchase
  app.post("/api/properties/:id/invest", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    try {
      const { tokenAmount, walletAddress } = req.body;
      
      if (!tokenAmount || tokenAmount < 100) {
        return res.status(400).json({ message: "Minimum investment is 100 tokens" });
      }
      
      if (!walletAddress) {
        return res.status(400).json({ message: "Wallet address is required" });
      }

      const result = await tokenizationService.processTokenPurchase(
        req.user!.id,
        req.params.id,
        tokenAmount,
        walletAddress
      );

      if (result.success) {
        res.json({ 
          message: "Investment successful", 
          transactionId: result.transactionId,
          txHash: result.transferTxHash
        });
      } else {
        res.status(400).json({ message: result.error });
      }
    } catch (error) {
      res.status(500).json({ message: "Investment failed", error });
    }
  });

  // Seller Endpoints

  // POST /api/seller/property/submit - Submit property for review
  app.post("/api/seller/property/submit", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    try {
      const validatedData = insertPropertySchema.parse(req.body);
      
      // Calculate tokenization details
      const tokenBreakdown = TokenCalculations.calculateTokenizationBreakdown(
        validatedData.propertyValue,
        validatedData.propertySize
      );

      const property = await storage.createProperty({
        ...validatedData,
        sellerId: req.user!.id,
        totalTokens: tokenBreakdown.totalTokens,
        tokenPrice: tokenBreakdown.tokenPrice
      });

      res.status(201).json({
        message: "Property submitted for review",
        property,
        tokenization: tokenBreakdown
      });
    } catch (error) {
      res.status(400).json({ message: "Invalid property data", error });
    }
  });

  // GET /api/seller/properties - List seller's properties
  app.get("/api/seller/properties", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    try {
      const properties = await storage.getProperties({
        sellerId: req.user!.id
      });
      res.json(properties);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch properties", error });
    }
  });

  // GET /api/seller/property/:id - Get seller's specific property
  app.get("/api/seller/property/:id", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    try {
      const property = await storage.getProperty(req.params.id);
      if (!property || property.sellerId !== req.user!.id) {
        return res.status(404).json({ message: "Property not found" });
      }
      res.json(property);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch property", error });
    }
  });

  // Investor Portfolio Endpoints

  // GET /api/investor/holdings - Get user's token holdings
  app.get("/api/investor/holdings", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    try {
      const holdings = await storage.getUserHoldings(req.user!.id);
      
      // Enrich with property details
      const enrichedHoldings = await Promise.all(
        holdings.map(async (holding) => {
          const property = await storage.getProperty(holding.propertyId);
          return {
            ...holding,
            property
          };
        })
      );
      
      res.json(enrichedHoldings);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch holdings", error });
    }
  });

  // GET /api/investor/transactions - Get user's transaction history
  app.get("/api/investor/transactions", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    try {
      const { limit, offset } = req.query;
      const transactions = await storage.getTransactions({
        userId: req.user!.id,
        limit: limit ? parseInt(limit as string) : 50,
        offset: offset ? parseInt(offset as string) : 0
      });

      // Enrich with property details
      const enrichedTransactions = await Promise.all(
        transactions.map(async (transaction) => {
          const property = await storage.getProperty(transaction.propertyId);
          return {
            ...transaction,
            property
          };
        })
      );

      res.json(enrichedTransactions);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch transactions", error });
    }
  });

  // GET /api/investor/income-statements - Get rental income history
  app.get("/api/investor/income-statements", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    try {
      const incomeTransactions = await storage.getTransactions({
        userId: req.user!.id,
        type: "income_distribution"
      });

      // Group by property and month
      const groupedIncome = incomeTransactions.reduce((acc, transaction) => {
        const key = `${transaction.propertyId}-${transaction.createdAt.getMonth()}-${transaction.createdAt.getFullYear()}`;
        if (!acc[key]) {
          acc[key] = {
            propertyId: transaction.propertyId,
            month: transaction.createdAt.getMonth(),
            year: transaction.createdAt.getFullYear(),
            totalAmount: 0,
            transactions: []
          };
        }
        acc[key].totalAmount += transaction.totalAmount;
        acc[key].transactions.push(transaction);
        return acc;
      }, {} as any);

      res.json(Object.values(groupedIncome));
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch income statements", error });
    }
  });

  // Secondary Market Endpoints

  // GET /api/market/orders - Get active market orders
  app.get("/api/market/orders", async (req, res) => {
    try {
      const { propertyId, orderType } = req.query;
      const orders = await storage.getMarketOrders({
        propertyId: propertyId as string,
        orderType: orderType as "buy" | "sell",
        status: "active",
        limit: 50
      });

      // Enrich with property details
      const enrichedOrders = await Promise.all(
        orders.map(async (order) => {
          const property = await storage.getProperty(order.propertyId);
          return {
            ...order,
            property
          };
        })
      );

      res.json(enrichedOrders);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch market orders", error });
    }
  });

  // POST /api/market/buy - Submit buy order
  app.post("/api/market/buy", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    try {
      const validatedData = insertMarketOrderSchema.parse({
        ...req.body,
        userId: req.user!.id,
        orderType: "buy"
      });

      const order = await storage.createMarketOrder(validatedData);
      res.status(201).json({ message: "Buy order created", order });
    } catch (error) {
      res.status(400).json({ message: "Invalid order data", error });
    }
  });

  // POST /api/market/sell - Submit sell order
  app.post("/api/market/sell", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    try {
      const validatedData = insertMarketOrderSchema.parse({
        ...req.body,
        userId: req.user!.id,
        orderType: "sell"
      });

      // Verify user has enough tokens to sell
      const holding = await storage.getHolding(req.user!.id, validatedData.propertyId);
      if (!holding || holding.tokenAmount < validatedData.tokenAmount) {
        return res.status(400).json({ message: "Insufficient tokens to sell" });
      }

      const order = await storage.createMarketOrder(validatedData);
      res.status(201).json({ message: "Sell order created", order });
    } catch (error) {
      res.status(400).json({ message: "Invalid order data", error });
    }
  });

  // Admin/Management Endpoints

  // POST /api/admin/property/:id/approve - Approve property for listing
  app.post("/api/admin/property/:id/approve", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    try {
      const property = await storage.updateProperty(req.params.id, {
        status: "approved",
        approvedAt: new Date()
      });

      if (!property) {
        return res.status(404).json({ message: "Property not found" });
      }

      // Trigger tokenization process
      const tokenizationResult = await tokenizationService.processPropertyTokenization(req.params.id);
      
      res.json({ 
        message: "Property approved and tokenized", 
        property,
        tokenization: tokenizationResult
      });
    } catch (error) {
      res.status(500).json({ message: "Failed to approve property", error });
    }
  });

  // POST /api/admin/property/:id/income - Distribute rental income
  app.post("/api/admin/property/:id/income", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    try {
      const { totalIncome } = req.body;
      
      if (!totalIncome || totalIncome <= 0) {
        return res.status(400).json({ message: "Invalid income amount" });
      }

      const result = await tokenizationService.distributeRentalIncome(
        req.params.id,
        totalIncome
      );

      if (result.success) {
        res.json({ 
          message: "Income distributed successfully", 
          distributionId: result.distributionId,
          txHashes: result.txHashes
        });
      } else {
        res.status(400).json({ message: result.error });
      }
    } catch (error) {
      res.status(500).json({ message: "Failed to distribute income", error });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
