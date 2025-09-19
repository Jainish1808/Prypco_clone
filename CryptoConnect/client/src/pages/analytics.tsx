import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  Building, 
  DollarSign, 
  Users, 
  Coins,
  TrendingUp,
  TrendingDown,
  Eye,
  Calendar,
  BarChart3,
  PieChart
} from "lucide-react";
import { api } from "@/lib/api";
import type { Property } from "@/lib/api";

export default function Analytics() {
  const { data: properties, isLoading } = useQuery({
    queryKey: ["/api/seller/properties"],
    queryFn: () => api.getSellerProperties(),
  });

  // Calculate analytics from properties data
  const analytics = React.useMemo(() => {
    if (!properties || !Array.isArray(properties)) {
      return {
        totalProperties: 0,
        totalValue: 0,
        totalTokens: 0,
        tokensSold: 0,
        totalRaised: 0,
        avgTokenPrice: 0,
        fundingRate: 0,
        statusBreakdown: {},
        monthlyData: []
      };
    }

    const totalProperties = properties.length;
    const totalValue = properties.reduce((sum, p) => sum + p.total_value, 0);
    const totalTokens = properties.reduce((sum, p) => sum + p.total_tokens, 0);
    const tokensSold = properties.reduce((sum, p) => sum + (p.tokens_sold || 0), 0);
    const totalRaised = properties.reduce((sum, p) => sum + ((p.tokens_sold || 0) * p.token_price), 0);
    const avgTokenPrice = totalTokens > 0 ? totalValue / totalTokens : 0;
    const fundingRate = totalTokens > 0 ? (tokensSold / totalTokens) * 100 : 0;

    // Status breakdown
    const statusBreakdown = properties.reduce((acc, p) => {
      acc[p.status] = (acc[p.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // Monthly data (simplified - in real app would be from backend)
    const monthlyData = [
      { month: 'Jan', properties: 0, raised: 0 },
      { month: 'Feb', properties: 0, raised: 0 },
      { month: 'Mar', properties: 1, raised: totalRaised * 0.3 },
      { month: 'Apr', properties: 2, raised: totalRaised * 0.6 },
      { month: 'May', properties: totalProperties, raised: totalRaised },
    ];

    return {
      totalProperties,
      totalValue,
      totalTokens,
      tokensSold,
      totalRaised,
      avgTokenPrice,
      fundingRate,
      statusBreakdown,
      monthlyData
    };
  }, [properties]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Property Analytics</h1>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Property Analytics</h1>
          <p className="text-muted-foreground">Detailed performance insights</p>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm">Total Properties</p>
                <p className="text-2xl font-bold">{analytics.totalProperties}</p>
                <p className="text-green-600 text-sm flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  Active listings
                </p>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                <Building className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm">Total Value</p>
                <p className="text-2xl font-bold">AED {(analytics.totalValue / 1000000).toFixed(1)}M</p>
                <p className="text-blue-600 text-sm">Portfolio value</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm">Tokens Sold</p>
                <p className="text-2xl font-bold">{analytics.tokensSold.toLocaleString()}</p>
                <p className="text-green-600 text-sm">{analytics.fundingRate.toFixed(1)}% funded</p>
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
                <p className="text-muted-foreground text-sm">Total Raised</p>
                <p className="text-2xl font-bold">AED {(analytics.totalRaised / 1000).toFixed(0)}K</p>
                <p className="text-purple-600 text-sm">From token sales</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Property Status Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <PieChart className="h-5 w-5 mr-2" />
              Property Status Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(analytics.statusBreakdown).map(([status, count]) => (
                <div key={status} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      status === 'pending_review' ? 'bg-yellow-500' :
                      status === 'approved' ? 'bg-green-500' :
                      status === 'tokenized' ? 'bg-blue-500' :
                      status === 'sold_out' ? 'bg-purple-500' :
                      'bg-gray-500'
                    }`}></div>
                    <span className="capitalize">{status.replace('_', ' ')}</span>
                  </div>
                  <span className="font-semibold">{count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Performance Metrics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              Performance Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div>
                  <p className="font-medium">Average Token Price</p>
                  <p className="text-sm text-muted-foreground">Across all properties</p>
                </div>
                <p className="text-lg font-bold">${analytics.avgTokenPrice.toFixed(2)}</p>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div>
                  <p className="font-medium">Funding Rate</p>
                  <p className="text-sm text-muted-foreground">Tokens sold vs total</p>
                </div>
                <p className="text-lg font-bold">{analytics.fundingRate.toFixed(1)}%</p>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div>
                  <p className="font-medium">Average Property Value</p>
                  <p className="text-sm text-muted-foreground">Per property</p>
                </div>
                <p className="text-lg font-bold">
                  AED {analytics.totalProperties > 0 ? (analytics.totalValue / analytics.totalProperties / 1000).toFixed(0) : 0}K
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Properties */}
      {properties && properties.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Properties</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {properties.slice(0, 5).map((property: Property) => (
                <div key={property.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                      <Building className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{property.title}</p>
                      <p className="text-sm text-muted-foreground">{property.city}, {property.country}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">AED {property.total_value.toLocaleString()}</p>
                    <p className="text-sm text-muted-foreground">{property.total_tokens.toLocaleString()} tokens</p>
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

