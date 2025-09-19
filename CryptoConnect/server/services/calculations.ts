/**
 * Mathematical Logic Implementation for Tokenized Real Estate
 * Implements the exact formulas specified in the requirements
 */

export class TokenCalculations {
  /**
   * Token Price (P): P = V / N
   * @param propertyValue - V (property value in USD)
   * @param totalTokens - N (total number of tokens)
   * @returns Token price in USD
   */
  static calculateTokenPrice(propertyValue: number, totalTokens: number): number {
    if (totalTokens === 0) throw new Error("Total tokens cannot be zero");
    return propertyValue / totalTokens;
  }

  /**
   * Total Tokens (N): N = S * 10,000
   * @param propertySize - S (property size in square meters)
   * @returns Total number of tokens
   */
  static calculateTotalTokens(propertySize: number): number {
    return propertySize * 10000;
  }

  /**
   * Ownership Fraction (F): F = k / N
   * @param tokensPurchased - k (number of tokens purchased)
   * @param totalTokens - N (total number of tokens)
   * @returns Ownership fraction as decimal (0-1)
   */
  static calculateOwnershipFraction(tokensPurchased: number, totalTokens: number): number {
    if (totalTokens === 0) throw new Error("Total tokens cannot be zero");
    return tokensPurchased / totalTokens;
  }

  /**
   * Rental Income Share (I): I = (k / N) * R
   * @param tokensPurchased - k (number of tokens purchased)
   * @param totalTokens - N (total number of tokens)
   * @param totalRentalIncome - R (total rental income)
   * @returns Individual rental income share
   */
  static calculateRentalIncomeShare(
    tokensPurchased: number, 
    totalTokens: number, 
    totalRentalIncome: number
  ): number {
    const ownershipFraction = this.calculateOwnershipFraction(tokensPurchased, totalTokens);
    return ownershipFraction * totalRentalIncome;
  }

  /**
   * Calculate minimum investment amount (100 tokens minimum)
   * @param tokenPrice - Price per token
   * @returns Minimum investment amount
   */
  static calculateMinimumInvestment(tokenPrice: number): number {
    const MIN_TOKENS = 100;
    return MIN_TOKENS * tokenPrice;
  }

  /**
   * Calculate expected annual yield percentage
   * @param annualRentalIncome - Expected annual rental income
   * @param propertyValue - Total property value
   * @returns Yield percentage
   */
  static calculateYieldPercentage(annualRentalIncome: number, propertyValue: number): number {
    if (propertyValue === 0) throw new Error("Property value cannot be zero");
    return (annualRentalIncome / propertyValue) * 100;
  }

  /**
   * Calculate token distribution for income
   * @param totalIncome - Total income to distribute
   * @param totalTokensInCirculation - Total tokens currently held by investors
   * @returns Income per token
   */
  static calculateIncomePerToken(totalIncome: number, totalTokensInCirculation: number): number {
    if (totalTokensInCirculation === 0) throw new Error("No tokens in circulation");
    return totalIncome / totalTokensInCirculation;
  }

  /**
   * Validate property tokenization parameters
   * @param propertyValue - Property value in USD
   * @param propertySize - Property size in square meters
   * @throws Error if parameters are invalid
   */
  static validateTokenizationParameters(propertyValue: number, propertySize: number): void {
    if (propertyValue <= 0) {
      throw new Error("Property value must be positive");
    }
    if (propertySize <= 0) {
      throw new Error("Property size must be positive");
    }
    if (propertyValue < 100000) {
      throw new Error("Property value must be at least $100,000 for tokenization");
    }
    if (propertySize < 10) {
      throw new Error("Property size must be at least 10 square meters");
    }
  }

  /**
   * Calculate complete tokenization details for a property
   * @param propertyValue - Property value in USD
   * @param propertySize - Property size in square meters
   * @returns Complete tokenization breakdown
   */
  static calculateTokenizationBreakdown(propertyValue: number, propertySize: number) {
    this.validateTokenizationParameters(propertyValue, propertySize);
    
    const totalTokens = this.calculateTotalTokens(propertySize);
    const tokenPrice = this.calculateTokenPrice(propertyValue, totalTokens);
    const minimumInvestment = this.calculateMinimumInvestment(tokenPrice);
    
    return {
      propertyValue,
      propertySize,
      totalTokens,
      tokenPrice: Number(tokenPrice.toFixed(2)),
      minimumInvestment: Number(minimumInvestment.toFixed(2)),
      minimumTokens: 100,
      tokensSold: 0,
      tokensAvailable: totalTokens
    };
  }
}
