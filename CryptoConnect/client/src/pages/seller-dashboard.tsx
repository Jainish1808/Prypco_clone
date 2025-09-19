import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
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
  FileDown
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
    enabled: !!user && user.userType === 'seller' && api.isAuthenticated(),
  });

  const stats = {
    propertiesListed: Array.isArray(sellerProperties) ? sellerProperties.length : 3,
    totalRaised: 1200000,
    activeInvestors: 127,
    avgTokenPrice: 28.50,
    targetPercentage: 85
  };

  const recentActivities = [
    {
      type: "approval",
      title: "Property NYC001 approved for listing",
      description: "Manhattan Apartment • 2 hours ago",
      status: "Approved",
      icon: Check,
      iconColor: "text-green-600",
      bgColor: "bg-green-100"
    },
    {
      type: "sale",
      title: "250 tokens sold for MIA001", 
      description: "Miami Beach Condo • 4 hours ago",
      status: "Token Sale",
      icon: Coins,
      iconColor: "text-blue-600",
      bgColor: "bg-blue-100"
    },
    {
      type: "review",
      title: "New property submission under review",
      description: "Brooklyn Loft • 1 day ago", 
      status: "Pending",
      icon: Clock,
      iconColor: "text-amber-600",
      bgColor: "bg-amber-100"
    }
  ];

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm">Properties Listed</p>
                <p className="text-2xl font-bold">{stats.propertiesListed}</p>
                <p className="text-green-600 text-sm">2 active, 1 pending</p>
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
                <p className="text-2xl font-bold">${(stats.totalRaised / 1000000).toFixed(1)}M</p>
                <p className="text-green-600 text-sm">{stats.targetPercentage}% of target</p>
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
                <p className="text-muted-foreground text-sm">Active Investors</p>
                <p className="text-2xl font-bold">{stats.activeInvestors}</p>
                <p className="text-secondary text-sm">Across all properties</p>
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
                <p className="text-muted-foreground text-sm">Avg. Token Price</p>
                <p className="text-2xl font-bold">${stats.avgTokenPrice}</p>
                <p className="text-green-600 text-sm">+5.2% this week</p>
              </div>
              <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center">
                <Coins className="h-6 w-6 text-amber-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivities.map((activity, index) => (
              <div key={index} className="flex items-center gap-4 p-3 bg-muted rounded-lg">
                <div className={`w-10 h-10 ${activity.bgColor} rounded-full flex items-center justify-center`}>
                  <activity.icon className={`h-5 w-5 ${activity.iconColor}`} />
                </div>
                <div className="flex-1">
                  <p className="font-medium">{activity.title}</p>
                  <p className="text-sm text-muted-foreground">{activity.description}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  activity.status === "Approved" 
                    ? "bg-green-100 text-green-800"
                    : activity.status === "Token Sale"
                    ? "bg-blue-100 text-blue-800"
                    : "bg-amber-100 text-amber-800"
                }`}>
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
