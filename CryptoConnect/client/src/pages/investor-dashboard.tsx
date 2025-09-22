import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
import { 
  TrendingUp, 
  Home, 
  Coins, 
  DollarSign,
  Search,
  Plus,
  ArrowLeftRight,
  Download
} from "lucide-react";

interface DashboardStats {
  totalInvestment: number;
  totalValue: number;
  propertiesOwned: number;
  monthlyIncome: number;
  totalTokens: number;
  growthPercentage: number;
}

export default function InvestorDashboard() {
  const { user } = useAuth();
  
  const { data: holdings } = useQuery({
    queryKey: ["/api/investor/holdings"],
    queryFn: () => api.getUserHoldings(),
    enabled: !!user && api.isAuthenticated(), // Temporarily remove userType check
  });

  const { data: transactions } = useQuery({
    queryKey: ["/api/investor/transactions"],
    queryFn: () => api.getUserTransactions(),
    enabled: !!user && api.isAuthenticated(), // Temporarily remove userType check
  });

  const { data: incomeHistory } = useQuery({
    queryKey: ["/api/investor/income-statements"],
    queryFn: () => api.getUserIncomeStatements(),
    enabled: !!user && api.isAuthenticated(), // Temporarily remove userType check
  });

  // Calculate dashboard stats from real data with proper field name handling
  const stats: DashboardStats = {
    totalInvestment: Array.isArray(holdings) ? holdings.reduce((sum: number, h: any) => {
      const investment = h.totalInvested || h.total_invested || h.total_investment || 0;
      return sum + investment;
    }, 0) : 0,
    totalValue: Array.isArray(holdings) ? holdings.reduce((sum: number, h: any) => {
      const tokens = h.tokenAmount || h.token_amount || h.tokens || 0;
      const tokenPrice = h.property?.tokenPrice || h.property?.token_price || 0;
      return sum + (tokens * tokenPrice);
    }, 0) : 0,
    propertiesOwned: Array.isArray(holdings) ? holdings.length : 0,
    monthlyIncome: Array.isArray(incomeHistory) ? incomeHistory.reduce((sum: number, income: any) => sum + (income.totalAmount || income.amount || 0), 0) : 0,
    totalTokens: Array.isArray(holdings) ? holdings.reduce((sum: number, h: any) => {
      const tokens = h.tokenAmount || h.token_amount || h.tokens || 0;
      return sum + tokens;
    }, 0) : 0,
    growthPercentage: (() => {
      const totalInvested = Array.isArray(holdings) ? holdings.reduce((sum: number, h: any) => {
        const investment = h.totalInvested || h.total_invested || h.total_investment || 0;
        return sum + investment;
      }, 0) : 0;
      const totalCurrent = Array.isArray(holdings) ? holdings.reduce((sum: number, h: any) => {
        const tokens = h.tokenAmount || h.token_amount || h.tokens || 0;
        const tokenPrice = h.property?.tokenPrice || h.property?.token_price || 0;
        return sum + (tokens * tokenPrice);
      }, 0) : 0;
      return totalInvested > 0 ? ((totalCurrent - totalInvested) / totalInvested) * 100 : 0;
    })()
  };

    // Generate recent income from actual data with safety checks
  const recentIncomeData = Array.isArray(incomeHistory) && incomeHistory.length > 0 
    ? incomeHistory.slice(0, 3).map((income: any) => ({
        propertyName: income.propertyName || income.property_title || `Property ${income.propertyId || income.property_id || 'Unknown'}`,
        propertyId: income.propertyId || income.property_id || 'unknown',
        amount: income.totalAmount || income.amount || 0,
        month: income.period || new Date(income.payment_date || income.created_at || Date.now()).toLocaleDateString('en-US', { 
          month: 'short', 
          year: 'numeric' 
        })
      }))
    : [];

  // Safety function to display numbers without NaN
  const safeNumber = (value: number) => {
    if (isNaN(value) || !isFinite(value)) return 0;
    return value;
  };

  const safePercentage = (value: number) => {
    if (isNaN(value) || !isFinite(value)) return 0;
    return Number(value.toFixed(1));
  };

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm">Total Investment</p>
                <p className="text-2xl font-bold">${safeNumber(stats.totalInvestment).toLocaleString()}</p>
                <p className={`text-sm ${safePercentage(stats.growthPercentage) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {safePercentage(stats.growthPercentage) >= 0 ? '+' : ''}{safePercentage(stats.growthPercentage).toFixed(1)}% portfolio growth
                </p>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm">Properties Owned</p>
                <p className="text-2xl font-bold">{stats.propertiesOwned}</p>
                <p className="text-secondary text-sm">Across multiple cities</p>
              </div>
              <div className="w-12 h-12 bg-secondary/10 rounded-full flex items-center justify-center">
                <Home className="h-6 w-6 text-secondary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm">Monthly Income</p>
                <p className="text-2xl font-bold">${safeNumber(stats.monthlyIncome).toLocaleString()}</p>
                <p className="text-muted-foreground text-sm">
                  {safeNumber(stats.monthlyIncome) > 0 ? "From property distributions" : "Start investing to earn income"}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <Coins className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm">Total Tokens</p>
                <p className="text-2xl font-bold">{safeNumber(stats.totalTokens).toLocaleString()}</p>
                <p className="text-muted-foreground text-sm">Across portfolio</p>
              </div>
              <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-amber-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Portfolio Performance Chart */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Portfolio Performance</CardTitle>
              <select className="text-sm border border-border rounded-lg px-3 py-1">
                <option value="30">Last 30 days</option>
                <option value="90">Last 90 days</option>
                <option value="365">Last year</option>
              </select>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
              <div className="text-center">
                <TrendingUp className="h-12 w-12 text-primary mb-2 mx-auto" />
                <p className="text-muted-foreground">Portfolio Performance</p>
                <p className="text-sm text-muted-foreground">
                  {stats.totalInvestment > 0 
                    ? `Total Growth: ${stats.growthPercentage >= 0 ? '+' : ''}${stats.growthPercentage.toFixed(1)}%`
                    : "Start investing to see your portfolio performance"
                  }
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Income Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Income Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentIncomeData.length > 0 ? (
                recentIncomeData.map((income: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                        <Home className="h-5 w-5 text-green-600" />
                      </div>
                      <div>
                        <p className="font-medium">{income.propertyName}</p>
                        <p className="text-sm text-muted-foreground">Property ID: {income.propertyId}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-green-600">+${income.amount}</p>
                      <p className="text-sm text-muted-foreground">{income.month}</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  <Home className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
                  <p>No recent income distributions</p>
                  <p className="text-sm">Income will appear here once you start earning from your investments</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button 
              variant="outline" 
              className="flex items-center gap-3 p-4 h-auto justify-start"
              data-testid="button-browse-properties"
            >
              <Search className="h-5 w-5 text-primary" />
              <span>Browse Properties</span>
            </Button>
            <Button 
              variant="outline" 
              className="flex items-center gap-3 p-4 h-auto justify-start"
              data-testid="button-make-investment"
            >
              <Plus className="h-5 w-5 text-secondary" />
              <span>Make Investment</span>
            </Button>
            <Button 
              variant="outline" 
              className="flex items-center gap-3 p-4 h-auto justify-start"
              data-testid="button-trade-tokens"
            >
              <ArrowLeftRight className="h-5 w-5 text-accent" />
              <span>Trade Tokens</span>
            </Button>
            <Button 
              variant="outline" 
              className="flex items-center gap-3 p-4 h-auto justify-start"
              data-testid="button-download-report"
            >
              <Download className="h-5 w-5 text-muted-foreground" />
              <span>Download Report</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
