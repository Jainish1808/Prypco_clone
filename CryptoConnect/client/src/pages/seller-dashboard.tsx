import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
import WalletWidget from "@/components/dashboard/WalletWidget";
import {
  Building,
  DollarSign,
  Users,
  Coins,
  Check,
  Clock,
  Plus,
  Eye,
  BarChart3,
  FileDown,
} from "lucide-react";
import type { PageView } from "@/pages/home-page";

interface SellerDashboardProps {
  onNavigate: (page: PageView) => void;
}

export default function SellerDashboard({ onNavigate }: SellerDashboardProps) {
  const { user } = useAuth();

  const { data: sellerProperties } = useQuery({
    queryKey: ["/api/seller/properties"],
    queryFn: () => api.getSellerProperties(),
    enabled: !!user && user.userType === "seller" && api.isAuthenticated(),
  });

  // Calculate real stats from actual data
  const stats = {
    propertiesListed: Array.isArray(sellerProperties)
      ? sellerProperties.length
      : 0,
    totalRaised: Array.isArray(sellerProperties)
      ? sellerProperties.reduce(
          (total, prop) => total + (prop.total_value || 0),
          0
        )
      : 0,
    activeInvestors: Array.isArray(sellerProperties)
      ? sellerProperties.reduce(
          (total, prop) => total + ((prop as any).investor_count || 0),
          0
        )
      : 0,
    avgTokenPrice:
      Array.isArray(sellerProperties) && sellerProperties.length > 0
        ? sellerProperties.reduce((total, prop) => {
            const tokenPrice =
              (prop as any).token_price ||
              (prop.total_value && prop.size_sqm
                ? prop.total_value / (prop.size_sqm * 10000)
                : 0);
            return total + tokenPrice;
          }, 0) / sellerProperties.length
        : 0,
    targetPercentage:
      Array.isArray(sellerProperties) && sellerProperties.length > 0
        ? Math.round(
            (sellerProperties.filter((prop) => prop.status === "approved")
              .length /
              sellerProperties.length) *
              100
          )
        : 0,
  };

  // Generate real activities from actual properties
  const recentActivities = Array.isArray(sellerProperties)
    ? sellerProperties.slice(0, 3).map((property) => ({
        type:
          property.status === "approved"
            ? "approval"
            : property.status === "pending"
            ? "review"
            : "sale",
        title:
          property.status === "approved"
            ? `Property ${property.title} approved for listing`
            : property.status === "pending"
            ? `Property ${property.title} under review`
            : `Tokens available for ${property.title}`,
        description: `${property.city}, ${property.country} • ${new Date(
          property.created_at || Date.now()
        ).toLocaleDateString()}`,
        status:
          property.status === "approved"
            ? "Approved"
            : property.status === "pending"
            ? "Pending"
            : "Active",
        icon:
          property.status === "approved"
            ? Check
            : property.status === "pending"
            ? Clock
            : Coins,
        iconColor:
          property.status === "approved"
            ? "text-green-600"
            : property.status === "pending"
            ? "text-amber-600"
            : "text-blue-600",
        bgColor:
          property.status === "approved"
            ? "bg-green-100"
            : property.status === "pending"
            ? "bg-amber-100"
            : "bg-blue-100",
      }))
    : [
        {
          type: "info",
          title: "No properties yet",
          description: "Submit your first property to see activities here",
          status: "Get Started",
          icon: Building,
          iconColor: "text-gray-600",
          bgColor: "bg-gray-100",
        },
      ];

  return (
    <div className="space-y-6">
      {/* Wallet Widget */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <WalletWidget />
        </div>

        {/* Stats Cards */}
        <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">
                    Properties Listed
                  </p>
                  <p className="text-2xl font-bold">{stats.propertiesListed}</p>
                  <p className="text-green-600 text-sm">
                    {Array.isArray(sellerProperties)
                      ? `${
                          sellerProperties.filter(
                            (p) => p.status === "approved"
                          ).length
                        } active, ${
                          sellerProperties.filter((p) => p.status === "pending")
                            .length
                        } pending`
                      : "No properties yet"}
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
                  <p className="text-muted-foreground text-sm">Total Raised</p>
                  <p className="text-2xl font-bold">
                    {stats.totalRaised > 1000000
                      ? `$${(stats.totalRaised / 1000000).toFixed(1)}M`
                      : stats.totalRaised > 1000
                      ? `$${(stats.totalRaised / 1000).toFixed(0)}K`
                      : `$${stats.totalRaised.toLocaleString()}`}
                  </p>
                  <p className="text-green-600 text-sm">
                    {stats.targetPercentage}% of target
                  </p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <DollarSign className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">
                    Active Investors
                  </p>
                  <p className="text-2xl font-bold">{stats.activeInvestors}</p>
                  <p className="text-secondary text-sm">
                    Across all properties
                  </p>
                </div>
                <div className="w-12 h-12 bg-secondary/10 rounded-full flex items-center justify-center">
                  <Users className="h-6 w-6 text-secondary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">
                    Avg. Token Price
                  </p>
                  <p className="text-2xl font-bold">${stats.avgTokenPrice}</p>
                  <p className="text-green-600 text-sm">
                    {stats.avgTokenPrice > 0
                      ? `$${stats.avgTokenPrice.toFixed(2)} avg`
                      : "No tokens yet"}
                  </p>
                </div>
                <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center">
                  <Coins className="h-6 w-6 text-amber-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivities.map((activity, index) => (
              <div
                key={index}
                className="flex items-center gap-4 p-3 bg-muted rounded-lg"
              >
                <div
                  className={`w-10 h-10 ${activity.bgColor} rounded-full flex items-center justify-center`}
                >
                  <activity.icon className={`h-5 w-5 ${activity.iconColor}`} />
                </div>
                <div className="flex-1">
                  <p className="font-medium">{activity.title}</p>
                  <p className="text-sm text-muted-foreground">
                    {activity.description}
                  </p>
                </div>
                <span
                  className={`text-xs px-2 py-1 rounded-full ${
                    activity.status === "Approved"
                      ? "bg-green-100 text-green-800"
                      : activity.status === "Token Sale"
                      ? "bg-blue-100 text-blue-800"
                      : "bg-amber-100 text-amber-800"
                  }`}
                >
                  {activity.status}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

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
              onClick={() => onNavigate("submit-property")}
              data-testid="button-submit-property"
            >
              <Plus className="h-5 w-5 text-primary" />
              <span>Submit Property</span>
            </Button>
            <Button
              variant="outline"
              className="flex items-center gap-3 p-4 h-auto justify-start"
              onClick={() => onNavigate("my-properties")}
              data-testid="button-view-properties"
            >
              <Eye className="h-5 w-5 text-secondary" />
              <span>View Properties</span>
            </Button>
            <Button
              variant="outline"
              className="flex items-center gap-3 p-4 h-auto justify-start"
              onClick={() => onNavigate("analytics")}
              data-testid="button-view-analytics"
            >
              <BarChart3 className="h-5 w-5 text-accent" />
              <span>View Analytics</span>
            </Button>
            <Button
              variant="outline"
              className="flex items-center gap-3 p-4 h-auto justify-start"
              data-testid="button-download-reports"
            >
              <FileDown className="h-5 w-5 text-muted-foreground" />
              <span>Download Reports</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
