import { useState, useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, Home, TrendingUp, ArrowUpRight, ExternalLink, Clock, CheckCircle, AlertCircle } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";

const getSafe = (obj: any, path: string, defaultValue: any = 0) => {
  return path.split('.').reduce((acc, key) => acc && acc[key] !== undefined ? acc[key] : defaultValue, obj);
};

interface EnrichedHolding {
  id: string;
  userId: string;
  propertyId: string;
  tokenAmount: number;
  totalInvested: number;
  averagePurchasePrice: number;
  lastUpdated: Date;
  property: any;
}

interface PortfolioSummaryProps {
  holdings: EnrichedHolding[];
  incomeHistory: any[]; 
  xrpRate: number | null;
}

const PortfolioSummary: React.FC<PortfolioSummaryProps> = ({ holdings, incomeHistory, xrpRate }) => {
  const { totalValue, totalInvested, totalGainLoss, totalGainLossPercent } = useMemo(() => {
    const totalValue = holdings.reduce((sum, holding) => {
      const tokenAmount = getSafe(holding, 'tokenAmount', getSafe(holding, 'token_amount'));
      const tokenPrice = getSafe(holding, 'property.tokenPrice', getSafe(holding, 'property.token_price'));
      return sum + (tokenAmount * tokenPrice);
    }, 0);

    const totalInvested = holdings.reduce(
      (sum, holding) => sum + (getSafe(holding, 'totalInvested', getSafe(holding, 'total_investment', getSafe(holding, 'total_invested', 0)))),
      0
    );
    const totalGainLoss = totalValue - totalInvested;
    const totalGainLossPercent = totalInvested > 0 ? (totalGainLoss / totalInvested) * 100 : 0;

    return { totalValue, totalInvested, totalGainLoss, totalGainLossPercent };
  }, [holdings]);

  const monthlyIncome = useMemo(() => {
    return Array.isArray(incomeHistory)
      ? incomeHistory.reduce((sum: number, income: any) => sum + getSafe(income, 'totalAmount', getSafe(income, 'amount')), 0)
      : 0;
  }, [incomeHistory]);

  const propertiesCount = holdings?.length || 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Card>
        <CardContent className="p-6">
          <p className="text-sm text-muted-foreground">Total Portfolio Value</p>
          <p className="text-3xl font-bold">${totalValue.toLocaleString()}</p>
          {xrpRate && xrpRate > 0 && (
            <p className="text-lg text-muted-foreground">~{(totalValue / xrpRate).toFixed(4)} XRP</p>
          )}
          <div className="flex items-center gap-2 mt-2">
            <Badge variant={totalGainLoss >= 0 ? "default" : "destructive"}>
              {totalGainLoss >= 0 ? "+" : ""}${totalGainLoss.toLocaleString()} ({totalGainLossPercent.toFixed(1)}%)
            </Badge>
            <span className="text-xs text-muted-foreground">vs invested</span>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-6">
          <p className="text-sm text-muted-foreground">Monthly Income</p>
          <p className="text-3xl font-bold text-green-600">${monthlyIncome.toLocaleString()}</p>
          <div className="flex items-center gap-2 mt-2">
            <Badge variant="outline" className="text-green-600">+5.2% from last month</Badge>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-6">
          <p className="text-sm text-muted-foreground">Properties Owned</p>
          <p className="text-3xl font-bold">{propertiesCount}</p>
          <p className="text-xs text-muted-foreground">Across multiple cities</p>
        </CardContent>
      </Card>
    </div>
  );
};

interface HoldingsTableProps {
  holdings: EnrichedHolding[];
  xrpRate: number | null;
}

const HoldingsTable: React.FC<HoldingsTableProps> = ({ holdings, xrpRate }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Token Holdings</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Property</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Tokens</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Investment</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Current Value</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">P&L</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody>
              {holdings.map((holding, index) => {
                const property = holding.property;
                if (!property) return null;

                const tokenAmount = getSafe(holding, 'tokenAmount', getSafe(holding, 'token_amount'));
                const totalInvested = getSafe(holding, 'totalInvested', getSafe(holding, 'total_investment'));
                const avgPurchasePrice = getSafe(holding, 'averagePurchasePrice', getSafe(holding, 'average_purchase_price'));
                const currentValue = tokenAmount * getSafe(property, 'tokenPrice', getSafe(property, 'token_price'));
                const gainLoss = currentValue - totalInvested;
                const gainLossPercent = totalInvested > 0 ? (gainLoss / totalInvested) * 100 : 0;
                const ownershipPercent = getSafe(property, 'totalTokens', getSafe(property, 'total_tokens')) > 0
                  ? (tokenAmount / getSafe(property, 'totalTokens', getSafe(property, 'total_tokens'))) * 100
                  : 0;

                return (
                  <tr key={holding.id || index} className="border-b" data-testid={`holding-row-${index}`}>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                          <Home className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <p className="font-medium">{getSafe(property, 'name', getSafe(property, 'title'))}</p>
                          <p className="text-sm text-muted-foreground">{property.address}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <p className="font-medium">{tokenAmount.toLocaleString()}</p>
                      <p className="text-sm text-muted-foreground">{ownershipPercent.toFixed(2)}% ownership</p>
                    </td>
                    <td className="py-4 px-4">
                      <p className="font-medium">${totalInvested.toLocaleString()}</p>
                      {xrpRate && xrpRate > 0 && (
                        <p className="text-sm text-muted-foreground">~{(totalInvested / xrpRate).toFixed(4)} XRP</p>
                      )}
                      <p className="text-xs text-muted-foreground">${avgPurchasePrice.toFixed(2)}/token</p>
                    </td>
                    <td className="py-4 px-4">
                      <p className="font-medium">${currentValue.toLocaleString()}</p>
                      <p className="text-sm text-muted-foreground">${getSafe(property, 'tokenPrice', getSafe(property, 'token_price')).toFixed(2)}/token</p>
                    </td>
                    <td className="py-4 px-4">
                      <div className={`flex items-center gap-1 font-medium ${gainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {gainLoss >= 0 ? <ArrowUpRight className="h-4 w-4" /> : null}
                        {gainLoss >= 0 ? '+' : ''}${gainLoss.toLocaleString()} ({gainLossPercent.toFixed(1)}%)
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <Button variant="outline" size="sm" data-testid={`button-trade-${index}`}>Trade</Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

interface TransactionsHistoryProps {
  transactions: any[];
}

const TransactionsHistory: React.FC<TransactionsHistoryProps> = ({ transactions }) => {
  const xrpTransactions = useMemo(() => {
    return (transactions || [])
      .filter((tx) => tx.xrpTxHash || tx.xrpl_tx_hash)
      .slice(0, 10);
  }, [transactions]);

  if (xrpTransactions.length === 0) {
    return (
      <Card>
        <CardHeader><CardTitle>XRP Transaction History</CardTitle></CardHeader>
        <CardContent className="text-center py-8">
          <Home className="h-8 w-8 text-muted-foreground mx-auto mb-3" />
          <p className="text-muted-foreground">No XRP transactions yet.</p>
          <p className="text-sm text-muted-foreground">Your investment transactions will appear here with XRPL details.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader><CardTitle>XRP Transaction History</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        {xrpTransactions.map((tx) => {
          const statusIcon = tx.status === 'completed' ? <CheckCircle className="h-4 w-4 text-green-500" /> :
                             tx.status === 'pending' ? <Clock className="h-4 w-4 text-yellow-500" /> :
                             <AlertCircle className="h-4 w-4 text-red-500" />;

          const createdAt = tx.createdAt || tx.created_at;
          const amount = tx.totalAmount ?? tx.amount ?? 0;
          const tokens = tx.tokenAmount ?? tx.tokens ?? 0;
          const pricePerToken = tx.pricePerToken ?? tx.token_price ?? 0;
          const propertyId = tx.propertyId ?? tx.property_id ?? '';
          const xrpTxHash = tx.xrpTxHash || tx.xrpl_tx_hash;

          return (
            <div key={tx.id} className="border rounded-lg p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {statusIcon}
                  <span className="font-medium">Investment Transaction</span>
                  <Badge variant={tx.status === 'completed' ? 'default' : 'secondary'}>{tx.status}</Badge>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">{createdAt ? new Date(createdAt).toLocaleDateString() : '-'}</p>
                  <p className="text-xs text-muted-foreground">{createdAt ? new Date(createdAt).toLocaleTimeString() : '-'}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Amount (AED)</p>
                  <p className="font-medium">${amount.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Tokens</p>
                  <p className="font-medium">{tokens.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Token Price</p>
                  <p className="font-medium">${Number(pricePerToken).toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Property ID</p>
                  <p className="font-medium text-xs">{String(propertyId).slice(-6)}</p>
                </div>
              </div>
              {xrpTxHash && (
                <div className="border-t pt-3">
                  <p className="text-sm text-muted-foreground mb-2">XRPL Transaction Details</p>
                  <div className="flex items-center justify-between bg-muted/50 rounded-md p-3">
                    <p className="font-mono text-sm break-all flex-1">{xrpTxHash}</p>
                    <Button
                      variant="outline"
                      size="sm"
                      className="ml-3"
                      onClick={() => window.open(`https://testnet.xrpl.org/transactions/${xrpTxHash}`, '_blank')}
                    >
                      <ExternalLink className="h-3 w-3 mr-1" />
                      Explorer
                    </Button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
        {transactions.length > 10 && (
          <div className="text-center pt-4">
            <Button variant="outline" size="sm">View All Transactions</Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

interface PortfolioProps {
  onNavigateToProperties?: () => void;
}

export default function Portfolio({ onNavigateToProperties }: PortfolioProps) {
  const { user } = useAuth();
  const [xrpRate, setXrpRate] = useState<number | null>(null);

  useEffect(() => {
    const fetchXrpRate = async () => {
      try {
        const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=aed');
        const data = await response.json();
        setXrpRate(data.ripple.aed);
      } catch (error) {
        console.error('Failed to fetch XRP rate:', error);
      }
    };
    fetchXrpRate();
  }, []);

  const queryOptions = {
    enabled: !!user && user.userType === 'investor' && api.isAuthenticated(),
  };

  const { data: holdings, isLoading: isLoadingHoldings, error: errorHoldings } = useQuery({
    queryKey: ["/api/investor/holdings"],
    queryFn: async (): Promise<EnrichedHolding[]> => {
      const userHoldings = await api.getUserHoldings();
      // Transform UserHolding[] to EnrichedHolding[] by fetching property data
      const enrichedHoldings = await Promise.all(
        userHoldings.map(async (holding): Promise<EnrichedHolding> => {
          try {
            const property = holding.property_id ? await api.getProperty(holding.property_id) : null;
            const resolvedTokens = Number((holding as any).tokenAmount ?? (holding as any).token_amount ?? (holding as any).tokens ?? (holding as any).tokens_owned ?? 0);
            const resolvedInvested = Number((holding as any).totalInvested ?? (holding as any).total_investment ?? (holding as any).total_invested ?? 0);
            return {
              id: String(holding.property_id),
              userId: String(user?.id || ""),
              propertyId: String(holding.property_id),
              tokenAmount: resolvedTokens,
              totalInvested: resolvedInvested,
              averagePurchasePrice: resolvedTokens > 0
                ? resolvedInvested / resolvedTokens
                : 0,
              lastUpdated: new Date(),
              property
            };
          } catch (error) {
            const resolvedTokens = Number((holding as any).tokenAmount ?? (holding as any).token_amount ?? (holding as any).tokens ?? (holding as any).tokens_owned ?? 0);
            const resolvedInvested = Number((holding as any).totalInvested ?? (holding as any).total_investment ?? (holding as any).total_invested ?? 0);
            return {
              id: String(holding.property_id),
              userId: String(user?.id || ""),
              propertyId: String(holding.property_id),
              tokenAmount: resolvedTokens,
              totalInvested: resolvedInvested,
              averagePurchasePrice: resolvedTokens > 0
                ? resolvedInvested / resolvedTokens
                : 0,
              lastUpdated: new Date(),
              property: null
            };
          }
        })
      );
      return enrichedHoldings;
    },
    ...queryOptions,
  });

  const { data: incomeHistory, isLoading: isLoadingIncome } = useQuery<any[], Error>({
    queryKey: ["/api/investor/income-statements"],
    queryFn: () => api.getUserIncomeStatements(),
    ...queryOptions,
  });

  const { data: transactions, isLoading: isLoadingTransactions } = useQuery<any[], Error>({
    queryKey: ["/api/investor/transactions"],
    queryFn: () => api.getUserTransactions(),
    ...queryOptions,
  });

  const isLoading = isLoadingHoldings || isLoadingIncome || isLoadingTransactions;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (errorHoldings) {
    return (
      <Card className="p-8 text-center">
        <CardContent>
          <p className="text-destructive">Failed to load portfolio data. Please try again.</p>
          <Button className="mt-4" onClick={() => window.location.reload()}>Retry</Button>
        </CardContent>
      </Card>
    );
  }

  if (!holdings || holdings.length === 0) {
    return (
      <div className="space-y-6">
        <Card className="p-8 text-center">
          <CardContent>
            <Home className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Properties in Portfolio</h3>
            <p className="text-muted-foreground mb-4">Start building your real estate portfolio by investing in tokenized properties.</p>
            <Button data-testid="button-browse-properties" onClick={onNavigateToProperties}>
              Browse Available Properties
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PortfolioSummary holdings={holdings} incomeHistory={incomeHistory || []} xrpRate={xrpRate} />
      <HoldingsTable holdings={holdings} xrpRate={xrpRate} />
      <TransactionsHistory transactions={transactions || []} />
      <Card>
        <CardHeader><CardTitle>Portfolio Performance</CardTitle></CardHeader>
        <CardContent>
          <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
            <div className="text-center">
              <TrendingUp className="h-12 w-12 text-primary mb-2 mx-auto" />
              <p className="text-muted-foreground">Performance chart coming soon.</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}