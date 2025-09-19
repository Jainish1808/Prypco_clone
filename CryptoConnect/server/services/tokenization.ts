import { storage } from "../storage";
import { blockchainService } from "./blockchain";
import { TokenCalculations } from "./calculations";
import type { Property, InsertTransaction, InsertIncomeDistribution } from "@shared/schema";

/**
 * Tokenization Orchestrator Service
 * Handles the complete tokenization workflow for properties
 */
export class TokenizationService {
  /**
   * Process property tokenization after approval
   * @param propertyId - Property to tokenize
   * @returns Tokenization result
   */
  async processPropertyTokenization(propertyId: string): Promise<{
    success: boolean;
    tokenSymbol?: string;
    mintTxHash?: string;
    error?: string;
  }> {
    try {
      const property = await storage.getProperty(propertyId);
      if (!property) {
        return { success: false, error: "Property not found" };
      }

      if (property.status !== "approved") {
        return { success: false, error: "Property not approved for tokenization" };
      }

      // Calculate tokenization details
      const tokenBreakdown = TokenCalculations.calculateTokenizationBreakdown(
        property.propertyValue,
        property.propertySize
      );

      // Generate token symbol
      const tokenSymbol = blockchainService.generateTokenSymbol(propertyId);

      // Mint tokens on XRP Ledger
      const mintTxHash = await blockchainService.mintPropertyTokens(
        propertyId,
        tokenSymbol,
        tokenBreakdown.totalTokens
      );

      // Update property with tokenization details
      const updatedProperty = await storage.updateProperty(propertyId, {
        status: "listed",
        totalTokens: tokenBreakdown.totalTokens,
        tokenPrice: tokenBreakdown.tokenPrice,
        tokensAvailable: tokenBreakdown.totalTokens,
        tokensSold: 0,
        listedAt: new Date()
      });

      if (!updatedProperty) {
        return { success: false, error: "Failed to update property" };
      }

      // Record tokenization transaction
      await blockchainService.recordTransaction(mintTxHash, {
        type: "mint",
        amount: tokenBreakdown.totalTokens,
        tokenSymbol,
        propertyId
      });

      return {
        success: true,
        tokenSymbol,
        mintTxHash
      };
    } catch (error) {
      console.error("Tokenization failed:", error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Handle token purchase transaction
   * @param userId - Buyer user ID
   * @param propertyId - Property to invest in
   * @param tokenAmount - Number of tokens to purchase
   * @param investorWalletAddress - Investor's XRP wallet address
   * @returns Purchase result
   */
  async processTokenPurchase(
    userId: string,
    propertyId: string,
    tokenAmount: number,
    investorWalletAddress: string
  ): Promise<{
    success: boolean;
    transactionId?: string;
    transferTxHash?: string;
    error?: string;
  }> {
    try {
      const property = await storage.getProperty(propertyId);
      if (!property) {
        return { success: false, error: "Property not found" };
      }

      if (property.status !== "listed") {
        return { success: false, error: "Property not available for investment" };
      }

      if (tokenAmount < 100) {
        return { success: false, error: "Minimum investment is 100 tokens" };
      }

      if (tokenAmount > property.tokensAvailable) {
        return { success: false, error: "Insufficient tokens available" };
      }

      // Validate wallet address
      if (!blockchainService.validateWalletAddress(investorWalletAddress)) {
        return { success: false, error: "Invalid wallet address" };
      }

      const totalAmount = tokenAmount * property.tokenPrice;
      const tokenSymbol = blockchainService.generateTokenSymbol(propertyId);

      // Establish trust line if needed (first-time investor)
      const trustLineTxHash = await blockchainService.establishTrustLine(
        investorWalletAddress,
        tokenSymbol,
        tokenAmount * 2 // Allow for future purchases
      );

      // Transfer tokens to investor
      const transferTxHash = await blockchainService.transferTokens(
        investorWalletAddress,
        tokenSymbol,
        tokenAmount,
        `Investment in property ${propertyId}`
      );

      // Create transaction record
      const transaction = await storage.createTransaction({
        userId,
        propertyId,
        type: "purchase",
        tokenAmount,
        pricePerToken: property.tokenPrice,
        totalAmount,
        xrpTxHash: transferTxHash,
        status: "completed"
      } as InsertTransaction);

      // Update property token availability
      await storage.updateProperty(propertyId, {
        tokensAvailable: property.tokensAvailable - tokenAmount,
        tokensSold: property.tokensSold + tokenAmount
      });

      // Update or create user holding
      await storage.createOrUpdateHolding({
        userId,
        propertyId,
        tokenAmount,
        averagePurchasePrice: property.tokenPrice,
        totalInvested: totalAmount
      });

      // Update user wallet address if not set
      const user = await storage.getUser(userId);
      if (user && !user.walletAddress) {
        await storage.updateUser(userId, { walletAddress: investorWalletAddress });
      }

      return {
        success: true,
        transactionId: transaction.id,
        transferTxHash
      };
    } catch (error) {
      console.error("Token purchase failed:", error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Calculate and distribute rental income
   * @param propertyId - Property generating income
   * @param totalIncome - Total rental income to distribute
   * @returns Distribution result
   */
  async distributeRentalIncome(
    propertyId: string,
    totalIncome: number
  ): Promise<{
    success: boolean;
    distributionId?: string;
    txHashes?: string[];
    error?: string;
  }> {
    try {
      const property = await storage.getProperty(propertyId);
      if (!property) {
        return { success: false, error: "Property not found" };
      }

      const holdings = await storage.getPropertyHoldings(propertyId);
      if (holdings.length === 0) {
        return { success: false, error: "No token holders found" };
      }

      // Calculate income per token
      const totalTokensHeld = holdings.reduce((sum, h) => sum + h.tokenAmount, 0);
      const incomePerToken = TokenCalculations.calculateIncomePerToken(totalIncome, totalTokensHeld);

      // Prepare distribution details
      const recipients = await Promise.all(
        holdings.map(async (holding) => {
          const user = await storage.getUser(holding.userId);
          const incomeAmount = TokenCalculations.calculateRentalIncomeShare(
            holding.tokenAmount,
            totalTokensHeld,
            totalIncome
          );

          return {
            userId: holding.userId,
            tokenAmount: holding.tokenAmount,
            incomeAmount,
            walletAddress: user?.walletAddress
          };
        })
      );

      // Create income distribution record
      const distribution = await storage.createIncomeDistribution({
        propertyId,
        totalIncome,
        distributionDate: new Date(),
        distributionPerToken: incomePerToken,
        status: "calculated",
        recipients: recipients.map(r => ({
          userId: r.userId,
          tokenAmount: r.tokenAmount,
          incomeAmount: r.incomeAmount
        }))
      } as InsertIncomeDistribution);

      // Distribute income via blockchain (only to users with wallet addresses)
      const walletsToDistribute = recipients
        .filter(r => r.walletAddress)
        .map(r => ({
          walletAddress: r.walletAddress!,
          amount: r.incomeAmount
        }));

      const txHashes = await blockchainService.distributeIncome(
        walletsToDistribute,
        totalIncome
      );

      // Create transaction records for each recipient
      for (let i = 0; i < recipients.length; i++) {
        const recipient = recipients[i];
        const txHash = i < txHashes.length ? txHashes[i] : undefined;

        await storage.createTransaction({
          userId: recipient.userId,
          propertyId,
          type: "income_distribution",
          tokenAmount: recipient.tokenAmount,
          pricePerToken: incomePerToken,
          totalAmount: recipient.incomeAmount,
          xrpTxHash: txHash,
          status: txHash ? "completed" : "pending"
        } as InsertTransaction);
      }

      // Mark distribution as completed
      await storage.updateIncomeDistribution(distribution.id, { status: "distributed" });

      return {
        success: true,
        distributionId: distribution.id,
        txHashes
      };
    } catch (error) {
      console.error("Income distribution failed:", error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Process secondary market trade
   * @param buyOrderId - Buy order ID
   * @param sellOrderId - Sell order ID
   * @returns Trade result
   */
  async processSecondaryMarketTrade(
    buyOrderId: string,
    sellOrderId: string
  ): Promise<{
    success: boolean;
    tradeId?: string;
    error?: string;
  }> {
    try {
      // Implementation for matching buy/sell orders
      // This would handle token transfers between investors
      console.log(`Processing trade: Buy ${buyOrderId}, Sell ${sellOrderId}`);
      
      // Mock implementation for now
      return {
        success: true,
        tradeId: `TRADE_${Date.now()}`
      };
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : "Trade processing failed"
      };
    }
  }
}

export const tokenizationService = new TokenizationService();
