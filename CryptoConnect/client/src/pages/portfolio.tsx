import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, Home, TrendingUp, ArrowUpRight } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
import type { Holding, Property } from "@shared/schema";

interface EnrichedHolding extends Holding {
  property: Property | null;
}

export default function Portfolio() {
  const { user } = useAuth();
  
  const { data: holdings, isLoading, error } = useQuery({
    queryKey: ["/api/investor/holdings"],
    queryFn: () => api.getUserHoldings(),
    enabled: !!user && user.userType === 'investor' && api.isAuthenticated(),
  });

  const { data: incomeHistory } = useQuery({
    queryKey: ["/api/investor/income-statements"],
    queryFn: () => api.getUserIncomeStatements(),
    enabled: !!user && user.userType === 'investor' && api.isAuthenticated(),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-8 text-center">
        <CardContent>
          <p className="text-destructive">Failed to load portfolio data. Please try again.</p>
          <Button className="mt-4" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  const totalValue = holdings?.reduce((sum, holding) => {
    if (!(holding as any).property) return sum;
    const tokenAmount = (holding as any).tokenAmount || (holding as any).token_amount || 0;
    return sum + (tokenAmount * (holding as any).property.tokenPrice);
  }, 0) || 0;

  const totalInvested = holdings?.reduce((sum, holding) => sum + holding.total_investment, 0) || 0;
  const totalGainLoss = totalValue - totalInvested;
  const totalGainLossPercent = totalInvested > 0 ? (totalGainLoss / totalInvested) * 100 : 0;

  const monthlyIncome = Array.isArray(incomeHistory) 
    ? incomeHistory.reduce((sum: number, income: any) => sum + (income.totalAmount || income.amount || 0), 0) 
    : 0;
  const properties = holdings?.length || 0;

  if (!holdings || holdings.length === 0) {
    return (
      <div className="space-y-6">
        <Card className="p-8 text-center">
          <CardContent>
            <Home className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Properties in Portfolio</h3>
            <p className="text-muted-foreground mb-4">
              Start building your real estate portfolio by investing in tokenized properties.
            </p>
            <Button data-testid="button-browse-properties">
              Browse Available Properties
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Total Portfolio Value</p>
              <p className="text-3xl font-bold">${totalValue.toLocaleString()}</p>
              <div className="flex items-center gap-2">
                <Badge variant={totalGainLoss >= 0 ? "default" : "destructive"} className="text-xs">
                  {totalGainLoss >= 0 ? "+" : ""}${totalGainLoss.toLocaleString()} ({totalGainLossPercent.toFixed(1)}%)
                </Badge>
                <span className="text-xs text-muted-foreground">vs invested</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Monthly Income</p>
              <p className="text-3xl font-bold text-green-600">${monthlyIncome.toLocaleString()}</p>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs text-green-600">
                  +8.2% from last month
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Properties Owned</p>
              <p className="text-3xl font-bold">{properties}</p>
              <p className="text-xs text-muted-foreground">Across multiple cities</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Holdings Table */}
      <Card>
        <CardHeader>
          <CardTitle>Token Holdings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Property</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Tokens</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Investment</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Current Value</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">P&L</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((holding: any, index) => {
                  const property = holding.property;
                  if (!property) return null;
                  
                  const tokenAmount = holding.tokenAmount || holding.token_amount || 0;
                  const totalInvested = holding.totalInvested || holding.total_invested || 0;
                  const averagePurchasePrice = holding.averagePurchasePrice || holding.average_purchase_price || 0;
                  const currentValue = tokenAmount * (property.tokenPrice || property.token_price || 0);
                  const gainLoss = currentValue - totalInvested;
                  const gainLossPercent = totalInvested > 0 ? (gainLoss / totalInvested) * 100 : 0;
                  const ownershipPercent = (property.totalTokens || property.total_tokens) > 0 
                    ? (tokenAmount / (property.totalTokens || property.total_tokens)) * 100 
                    : 0;

                  return (
                    <tr key={holding.id || index} className="border-b border-border" data-testid={`holding-row-${index}`}>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                            <Home className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <p className="font-medium">{property.name || property.title}</p>
                            <p className="text-sm text-muted-foreground">{property.address}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div>
                          <p className="font-medium">{tokenAmount.toLocaleString()}</p>
                          <p className="text-sm text-muted-foreground">{ownershipPercent.toFixed(2)}% ownership</p>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <p className="font-medium">${totalInvested.toLocaleString()}</p>
                        <p className="text-sm text-muted-foreground">
                          ${averagePurchasePrice.toFixed(2)}/token
                        </p>
                      </td>
                      <td className="py-4 px-4">
                        <p className="font-medium">${currentValue.toLocaleString()}</p>
                        <p className="text-sm text-muted-foreground">
                          ${(property.tokenPrice || property.token_price || 0).toFixed(2)}/token
                        </p>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-1">
                          <p className={`font-medium ${gainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {gainLoss >= 0 ? '+' : ''}${gainLoss.toLocaleString()}
                          </p>
                          {gainLoss >= 0 ? (
                            <ArrowUpRight className="h-4 w-4 text-green-600" />
                          ) : null}
                        </div>
                        <p className={`text-sm ${gainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {gainLossPercent.toFixed(1)}%
                        </p>
                      </td>
                      <td className="py-4 px-4">
                        <Button 
                          variant="outline" 
                          size="sm"
                          data-testid={`button-trade-${index}`}
                        >
                          Trade
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Performance Chart Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Portfolio Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
            <div className="text-center">
              <TrendingUp className="h-12 w-12 text-primary mb-2 mx-auto" />
              <p className="text-muted-foreground">Portfolio Performance</p>
              <p className="text-sm text-muted-foreground">
                {totalInvested > 0 
                  ? `Growth: ${totalGainLossPercent >= 0 ? '+' : ''}${totalGainLossPercent.toFixed(1)}%`
                  : "Performance tracking will appear after you make investments"
                }
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
