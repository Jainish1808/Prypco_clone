import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Loader2, TrendingUp, TrendingDown } from "lucide-react";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
import type { MarketOrder, Property } from "@shared/schema";

interface EnrichedMarketOrder extends MarketOrder {
  property: Property | null;
}

export default function SecondaryMarket() {
  const { toast } = useToast();
  const { user } = useAuth();
  const [selectedProperty, setSelectedProperty] = useState<string>("all");
  const [orderType, setOrderType] = useState<"buy" | "sell">("buy");
  const [tokenAmount, setTokenAmount] = useState("");
  const [pricePerToken, setPricePerToken] = useState("");

  const { data: marketOrders, isLoading, error } = useQuery<EnrichedMarketOrder[]>({
    queryKey: ["/api/market/orders", selectedProperty === "all" ? "all" : selectedProperty],
    queryFn: async () => {
      const propertyParam = selectedProperty === "all" ? "" : `?property_id=${selectedProperty}`;
      const response = await apiRequest("GET", `/api/market/orders${propertyParam}`);
      return response.json();
    },
    enabled: !!user && api.isAuthenticated(),
  });

  const { data: properties } = useQuery({
    queryKey: ["/api/properties"],
    queryFn: () => api.getProperties(),
    enabled: !!user && api.isAuthenticated(),
  });

  // Get user's holdings for sell orders - always enabled when sell is selected
  const { data: userHoldings } = useQuery({
    queryKey: ["/api/investor/holdings"],
    queryFn: () => api.getUserHoldings(),
    enabled: !!user && user.userType === 'investor' && api.isAuthenticated(),
  });

  // Get user's portfolio stats for portfolio value display
  const { data: portfolioStats } = useQuery({
    queryKey: ["/api/investor/stats"],
    queryFn: () => api.getInvestorStats(),
    enabled: !!user && user.userType === 'investor' && api.isAuthenticated(),
  });

  // Filter properties based on order type
  const availableProperties = orderType === 'sell' 
    ? userHoldings?.filter((holding: any) => {
        const tokenAmount = holding.tokenAmount || holding.token_amount || 0;
        return tokenAmount > 0;
      }).map((holding: any) => ({
        ...holding.property,
        tokenAmount: holding.tokenAmount || holding.token_amount
      })).filter(Boolean) || []
    : properties || [];

  // Debug logging for troubleshooting
  console.log('🔍 Debug - Order Type:', orderType);
  console.log('🔍 Debug - User Holdings:', userHoldings);
  console.log('🔍 Debug - Available Properties:', availableProperties);
  console.log('🔍 Debug - All Properties:', properties);

  const buyOrders = marketOrders?.filter(order => order.orderType === "buy") || [];
  const sellOrders = marketOrders?.filter(order => order.orderType === "sell") || [];

  const createOrderMutation = useMutation({
    mutationFn: async (orderData: any) => {
      const endpoint = orderType === "buy" ? "/api/market/buy" : "/api/market/sell";
      const res = await apiRequest("POST", endpoint, orderData);
      return res.json();
    },
    onSuccess: () => {
      toast({
        title: "Order Created",
        description: `Your ${orderType} order has been placed successfully.`,
      });
      queryClient.invalidateQueries({ queryKey: ["/api/market/orders"] });
      setTokenAmount("");
      setPricePerToken("");
    },
    onError: (error: Error) => {
      toast({
        title: "Order Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleSubmitOrder = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedProperty || selectedProperty === "all") {
      toast({
        title: "Property Required",
        description: "Please select a property for your order.",
        variant: "destructive",
      });
      return;
    }

    if (!tokenAmount || !pricePerToken) {
      toast({
        title: "Missing Information",
        description: "Please fill in all order details.",
        variant: "destructive",
      });
      return;
    }

    createOrderMutation.mutate({
      propertyId: selectedProperty,
      tokenAmount: parseInt(tokenAmount),
      pricePerToken: parseFloat(pricePerToken),
    });
  };

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
          <p className="text-destructive">Failed to load market data. Please try again.</p>
          <Button className="mt-4" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Calculate market stats dynamically
  const portfolioValue = portfolioStats?.totalInvestment || 0;
  const totalOrders = marketOrders?.length || 0;
  const volume24h = marketOrders?.reduce((sum, order) => {
    return sum + (order.tokenAmount * order.pricePerToken);
  }, 0) || 0;
  const completedToday = marketOrders?.filter(order => order.status === 'filled').length || 0;
  const avgPrice = totalOrders > 0 && marketOrders
    ? marketOrders.reduce((sum, order) => sum + order.pricePerToken, 0) / totalOrders 
    : 0;

  return (
    <div className="space-y-6">
      {/* Market Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-green-600">${portfolioValue.toLocaleString()}</p>
            <p className="text-sm text-muted-foreground">Portfolio</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-primary">{totalOrders}</p>
            <p className="text-sm text-muted-foreground">Active Orders</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-secondary">${volume24h.toLocaleString()}</p>
            <p className="text-sm text-muted-foreground">24h Volume</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-green-600">{completedToday}</p>
            <p className="text-sm text-muted-foreground">Completed Today</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold">${avgPrice.toFixed(2)}</p>
            <p className="text-sm text-muted-foreground">Avg. Price</p>
          </CardContent>
        </Card>
      </div>

      {/* Create Order Form */}
      <Card>
        <CardHeader>
          <CardTitle>Create Order</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmitOrder} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div>
                <Label htmlFor="order-type">Order Type</Label>
                <Select value={orderType} onValueChange={(value: "buy" | "sell") => setOrderType(value)}>
                  <SelectTrigger data-testid="select-order-type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="buy">Buy Order</SelectItem>
                    <SelectItem value="sell">Sell Order</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="property-select">Property</Label>
                <Select value={selectedProperty} onValueChange={setSelectedProperty}>
                  <SelectTrigger data-testid="select-property">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">
                      {orderType === 'sell' && availableProperties.length === 0 
                        ? "No properties with tokens to sell" 
                        : "Select Property"}
                    </SelectItem>
                    {availableProperties.map((property: any) => (
                      <SelectItem key={property.id} value={property.id}>
                        {property.name || property.title} 
                        {orderType === 'sell' && property.tokenAmount && ` (${property.tokenAmount} tokens)`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="token-amount">Token Amount</Label>
                <Input
                  id="token-amount"
                  type="number"
                  value={tokenAmount}
                  onChange={(e) => setTokenAmount(e.target.value)}
                  placeholder="100"
                  min="1"
                  data-testid="input-token-amount"
                />
              </div>

              <div>
                <Label htmlFor="price-per-token">Price per Token</Label>
                <Input
                  id="price-per-token"
                  type="number"
                  step="0.01"
                  value={pricePerToken}
                  onChange={(e) => setPricePerToken(e.target.value)}
                  placeholder="25.00"
                  data-testid="input-price-per-token"
                />
              </div>

              <div className="flex items-end">
                <Button 
                  type="submit" 
                  className="w-full"
                  disabled={createOrderMutation.isPending}
                  data-testid="button-create-order"
                >
                  {createOrderMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    `Create ${orderType} Order`
                  )}
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Order Book */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Buy Orders */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-600">
              <TrendingUp className="h-5 w-5" />
              Buy Orders
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {buyOrders.length === 0 ? (
                <p className="text-center text-muted-foreground py-4">No active buy orders</p>
              ) : (
                buyOrders.map((order) => (
                  <div key={order.id} className="flex items-center justify-between py-2 border-b border-border last:border-b-0">
                    <div>
                      <p className="font-medium">{order.property?.name || 'Unknown Property'}</p>
                      <p className="text-sm text-muted-foreground">
                        {order.tokenAmount.toLocaleString()} tokens
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-green-600">${order.pricePerToken.toFixed(2)}</p>
                      <Badge variant="outline" className="text-xs">
                        {order.status}
                      </Badge>
                    </div>
                    <Button size="sm" variant="outline" data-testid={`button-sell-to-${order.id}`}>
                      Sell
                    </Button>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Sell Orders */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <TrendingDown className="h-5 w-5" />
              Sell Orders
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {sellOrders.length === 0 ? (
                <p className="text-center text-muted-foreground py-4">No active sell orders</p>
              ) : (
                sellOrders.map((order) => (
                  <div key={order.id} className="flex items-center justify-between py-2 border-b border-border last:border-b-0">
                    <div>
                      <p className="font-medium">{order.property?.name || 'Unknown Property'}</p>
                      <p className="text-sm text-muted-foreground">
                        {order.tokenAmount.toLocaleString()} tokens
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-red-600">${order.pricePerToken.toFixed(2)}</p>
                      <Badge variant="outline" className="text-xs">
                        {order.status}
                      </Badge>
                    </div>
                    <Button size="sm" variant="outline" data-testid={`button-buy-from-${order.id}`}>
                      Buy
                    </Button>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
