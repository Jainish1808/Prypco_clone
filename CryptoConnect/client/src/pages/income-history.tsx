import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Loader2, Home, TrendingUp, Calendar, DollarSign, ArrowDownToLine } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";

interface IncomeStatement {
  property_id: string;
  property_title: string;
  period: string;
  amount: number;
  tokens: number;
  payment_date: string;
  status: string;
}

interface IncomeHistoryProps {
  onNavigateToPortfolio?: () => void;
}

export default function IncomeHistory({ onNavigateToPortfolio }: IncomeHistoryProps) {
  const { user } = useAuth();

  const { data: incomeStatements, isLoading, error } = useQuery({
    queryKey: ["/api/investor/income-statements"],
    queryFn: () => api.getUserIncomeStatements(),
    enabled: !!user && user.userType === 'investor' && api.isAuthenticated(),
  });

  const { data: transactions } = useQuery({
    queryKey: ["/api/investor/transactions"],
    queryFn: () => api.getUserTransactions(),
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
          <p className="text-destructive">Failed to load income data. Please try again.</p>
          <Button className="mt-4" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Calculate summary stats
  const totalIncome = Array.isArray(incomeStatements) 
    ? incomeStatements.reduce((sum: number, statement: any) => sum + (statement.amount || 0), 0)
    : 0;

  const thisMonthIncome = Array.isArray(incomeStatements)
    ? incomeStatements
        .filter((statement: any) => {
          const statementDate = new Date(statement.payment_date || statement.created_at);
          const now = new Date();
          return statementDate.getMonth() === now.getMonth() && statementDate.getFullYear() === now.getFullYear();
        })
        .reduce((sum: number, statement: any) => sum + (statement.amount || 0), 0)
    : 0;

  const totalPayments = Array.isArray(incomeStatements) ? incomeStatements.length : 0;

  // Get recent rental distribution transactions
  const rentalTransactions = Array.isArray(transactions)
    ? transactions.filter((tx: any) => tx.transaction_type === 'rental_distribution' || tx.transaction_type === 'income_distribution')
    : [];

  if (!incomeStatements || incomeStatements.length === 0) {
    return (
      <div className="space-y-6">
        <Card className="p-8 text-center">
          <CardContent>
            <ArrowDownToLine className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Income History Yet</h3>
            <p className="text-muted-foreground mb-4">
              Start earning rental income by investing in tokenized properties. Income distributions will appear here.
            </p>
            <Button 
              data-testid="button-view-portfolio"
              onClick={onNavigateToPortfolio}
            >
              View My Portfolio
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Income Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Total Income Received</p>
              <p className="text-3xl font-bold text-green-600">${totalIncome.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">From all properties</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">This Month</p>
              <p className="text-3xl font-bold">${thisMonthIncome.toLocaleString()}</p>
              <div className="flex items-center gap-2">
                <Badge variant={thisMonthIncome > 0 ? "default" : "secondary"} className="text-xs">
                  {thisMonthIncome > 0 ? "Active" : "No payments"}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Total Payments</p>
              <p className="text-3xl font-bold">{totalPayments}</p>
              <p className="text-xs text-muted-foreground">Income distributions</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Income History Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-600" />
            Income History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Property</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Period</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Amount</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Tokens</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Payment Date</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Status</th>
                </tr>
              </thead>
              <tbody>
                {incomeStatements.map((statement: any, index: number) => {
                  const paymentDate = new Date(statement.payment_date || statement.created_at);
                  
                  return (
                    <tr key={statement.id || index} className="border-b border-border" data-testid={`income-row-${index}`}>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                            <Home className="h-5 w-5 text-green-600" />
                          </div>
                          <div>
                            <p className="font-medium">{statement.property_title || 'Property'}</p>
                            <p className="text-sm text-muted-foreground">ID: {statement.property_id.slice(-6)}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-muted-foreground" />
                          <span>{statement.period || paymentDate.toLocaleDateString('en-US', { year: 'numeric', month: 'short' })}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <DollarSign className="h-4 w-4 text-green-600" />
                          <span className="font-medium text-green-600">${statement.amount.toLocaleString()}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <p className="font-medium">{statement.tokens.toLocaleString()}</p>
                        <p className="text-sm text-muted-foreground">${(statement.amount / statement.tokens).toFixed(4)}/token</p>
                      </td>
                      <td className="py-4 px-4">
                        <p className="text-sm">{paymentDate.toLocaleDateString()}</p>
                        <p className="text-xs text-muted-foreground">{paymentDate.toLocaleTimeString()}</p>
                      </td>
                      <td className="py-4 px-4">
                        <Badge variant={statement.status === 'completed' ? "default" : "secondary"} className="text-xs">
                          {statement.status || 'completed'}
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Recent Distributions */}
      {rentalTransactions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Distributions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {rentalTransactions.slice(0, 5).map((tx: any, index: number) => (
                <div key={tx.id || index} className="flex items-center justify-between p-4 bg-muted rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <ArrowDownToLine className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium">Rental Income</p>
                      <p className="text-sm text-muted-foreground">
                        {tx.tokens} tokens • {new Date(tx.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-green-600">+${tx.amount.toLocaleString()}</p>
                    {tx.xrpl_tx_hash && (
                      <p className="text-xs text-muted-foreground">TX: {tx.xrpl_tx_hash.slice(0, 8)}...</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}