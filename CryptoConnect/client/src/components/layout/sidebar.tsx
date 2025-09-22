import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { 
  Home, 
  TrendingUp, 
  Wallet, 
  ArrowLeftRight, 
  Coins,
  Building,
  PlusCircle,
  List,
  BarChart3,
  Settings,
  LogOut,
  Shield,
  Users,
  CheckCircle
} from "lucide-react";
import type { UserPanel, PageView } from "@/pages/home-page";

interface SidebarProps {
  currentPanel: UserPanel;
  currentPage: PageView;
  onPageChange: (page: PageView) => void;
  isOpen: boolean;
  onClose: () => void;
}

export default function Sidebar({ 
  currentPanel,
  currentPage, 
  onPageChange,
  isOpen,
  onClose
}: SidebarProps) {
  const { user, logoutMutation } = useAuth();  const investorNavItems = [
    { id: "dashboard" as PageView, label: "Dashboard", icon: TrendingUp },
    { id: "properties" as PageView, label: "Properties", icon: Home },
    { id: "portfolio" as PageView, label: "My Portfolio", icon: Wallet },
    { id: "market" as PageView, label: "Secondary Market", icon: ArrowLeftRight },
    { id: "income" as PageView, label: "Income History", icon: Coins },
  ];

  const sellerNavItems = [
    { id: "seller-dashboard" as PageView, label: "Dashboard", icon: TrendingUp },
    { id: "submit-property" as PageView, label: "Submit Property", icon: PlusCircle },
    { id: "my-properties" as PageView, label: "My Properties", icon: List },
    { id: "analytics" as PageView, label: "Analytics", icon: BarChart3 },
  ];

  const adminNavItems = [
    { id: "admin-dashboard" as PageView, label: "Admin Dashboard", icon: Shield },
  ];

  const getCurrentNavItems = () => {
    if (currentPanel === "admin") return adminNavItems;
    return currentPanel === "investor" ? investorNavItems : sellerNavItems;
  };

  const currentNavItems = getCurrentNavItems();

  const handleLogout = () => {
    logoutMutation.mutate();
  };

  return (
    <>
      <div 
        className={`sidebar-transition fixed lg:static inset-y-0 left-0 z-50 w-64 bg-card border-r border-border shadow-lg lg:shadow-none ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0`}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 p-6 border-b border-border">
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <Home className="text-primary-foreground text-lg" />
          </div>
          <div>
            <h1 className="font-bold text-lg">RealEstate Token</h1>
            <p className="text-sm text-muted-foreground">Investment Platform</p>
          </div>
        </div>

        {/* User Role Display */}
        <div className="p-4 border-b border-border">
          <div className="bg-muted rounded-lg p-3">
            <div className="flex items-center justify-center gap-2">
              {currentPanel === "investor" && <TrendingUp className="h-4 w-4" />}
              {currentPanel === "seller" && <Building className="h-4 w-4" />}
              {currentPanel === "admin" && <Shield className="h-4 w-4" />}
              <span className="text-sm font-medium capitalize">
                {currentPanel} Dashboard
              </span>
            </div>
            <p className="text-xs text-muted-foreground text-center mt-1">
              Role: {user?.userType || 'Unknown'}
            </p>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="p-4 space-y-2">
          {currentNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => onPageChange(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-left ${
                  isActive 
                    ? "bg-primary text-primary-foreground" 
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                }`}
                data-testid={`nav-${item.id}`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* User Profile */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border bg-card">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
              <span className="text-sm font-medium">
                {user?.firstName?.[0]}{user?.lastName?.[0]}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">
                {user?.firstName} {user?.lastName}
              </p>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full transition-colors ${
                  user?.isKYCVerified 
                    ? 'bg-emerald-500 shadow-sm' 
                    : 'bg-amber-500 animate-pulse'
                }`} />
                <span className={`text-xs font-medium transition-colors ${
                  user?.isKYCVerified 
                    ? 'text-emerald-700 dark:text-emerald-400' 
                    : 'text-amber-700 dark:text-amber-400'
                }`}>
                  {user?.isKYCVerified ? 'KYC Verified' : 'Pending Verification'}
                </span>
              </div>
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="flex-1">
              <Settings className="h-4 w-4" />
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleLogout}
              disabled={logoutMutation.isPending}
              className="flex-1"
              data-testid="button-logout"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </>
  );
}
