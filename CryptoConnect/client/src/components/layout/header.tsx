import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Menu, Bell, Wallet, Clock, X, Trash2 } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { useQuery } from "@tanstack/react-query";
import type { PageView } from "@/pages/home-page";
import { api } from "@/lib/api";
import { useNotifications } from "@/hooks/use-notifications";
import React from "react";

interface HeaderProps {
  currentPage: PageView;
  onMenuClick: () => void;
}

const pageConfig = {
  dashboard: {
    title: "Investment Dashboard",
    subtitle: "Monitor your real estate investments"
  },
  properties: {
    title: "Available Properties",
    subtitle: "Discover tokenized real estate opportunities"
  },
  portfolio: {
    title: "My Portfolio",
    subtitle: "Track your real estate token holdings"
  },
  market: {
    title: "Secondary Market",
    subtitle: "Trade tokens with other investors"
  },
  income: {
    title: "Income History",
    subtitle: "View your rental income distributions"
  },
  "seller-dashboard": {
    title: "Seller Dashboard",
    subtitle: "Manage your property listings"
  },
  "submit-property": {
    title: "Submit Property",
    subtitle: "List your property for tokenization"
  },
  "my-properties": {
    title: "My Properties",
    subtitle: "Track your submitted properties"
  },
  analytics: {
    title: "Property Analytics",
    subtitle: "Detailed performance insights"
  },
  "admin-dashboard": {
    title: "Admin Dashboard",
    subtitle: "Manage properties and verify users"
  }
} as const;

export default function Header({ currentPage, onMenuClick }: HeaderProps) {
  const { user } = useAuth();
  const { 
    notifications: userNotifications, 
    addNotification, 
    clearNotification, 
    clearAllNotifications, 
    markAsRead 
  } = useNotifications();
  const config = pageConfig[currentPage] || pageConfig.dashboard;

  // Fetch wallet balance dynamically
  const { data: walletData } = useQuery({
    queryKey: ['/api/simple-wallet/info'],
    queryFn: async () => {
      const response = await fetch('/api/simple-wallet/info', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      if (!response.ok) return null;
      return response.json();
    },
    enabled: !!user,
  });

  // Calculate total portfolio value from holdings
  const { data: holdings } = useQuery({
    queryKey: ["/api/investor/holdings"],
    queryFn: async () => {
      const response = await fetch('/api/investor/holdings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      if (!response.ok) return [];
      return response.json();
    },
    enabled: !!user && user.userType === 'investor',
  });

  const portfolioValue = holdings?.reduce((sum: number, holding: any) => {
    const property = holding.property;
    if (!property) return sum;
    const tokenAmount = holding.tokenAmount || holding.token_amount || 0;
    const tokenPrice = property.tokenPrice || property.token_price || 0;
    return sum + (tokenAmount * tokenPrice);
  }, 0) || 0;

  const xrpBalance = walletData?.xrp_balance || 0;
  // Fetch notifications count - temporarily disabled until backend endpoint is implemented
  const { data: notifications } = useQuery({
    queryKey: ['/api/notifications/unread'],
    queryFn: async () => {
      try {
        return await api.getUnreadNotifications();
      } catch (error) {
        // Silently handle 404 - notifications endpoint not implemented yet
        return { count: 0 };
      }
    },
    enabled: false, // Temporarily disabled until backend endpoint is implemented
    retry: false, // Don't retry on failure
    refetchOnWindowFocus: false, // Don't refetch when window gains focus
    refetchOnMount: false, // Don't refetch on component mount
    staleTime: Infinity, // Keep data fresh indefinitely to avoid repeated failed requests
  });

  const hasNotifications = (notifications?.count || 0) > 0;
  
  // Function to add a demo notification (for testing purposes)
  const addDemoNotification = () => {
    const demoTypes: Array<'success' | 'income' | 'info'> = ['success', 'income', 'info'];
    const randomType = demoTypes[Math.floor(Math.random() * demoTypes.length)];
    
    const demoMessages = {
      success: {
        title: "Property Investment Approved",
        message: "Your investment has been successfully processed"
      },
      income: {
        title: "Monthly Income Received",
        message: `You received AED ${Math.floor(Math.random() * 2000 + 500)} from your properties`
      },
      info: {
        title: "New Property Available",
        message: "A new tokenized property is now available for investment"
      }
    };

    addNotification({
      ...demoMessages[randomType],
      type: randomType,
    });
  };
  
  const displayBalance = user?.userType === 'investor' 
    ? portfolioValue 
    : xrpBalance;

  return (
    <header className="bg-card border-b border-border px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onMenuClick}
            className="lg:hidden"
            data-testid="button-menu-toggle"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <div>
            <h2 className="text-2xl font-bold">{config.title}</h2>
            <p className="text-muted-foreground">{config.subtitle}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 bg-muted px-3 py-2 rounded-lg">
            <Wallet className="h-4 w-4 text-secondary" />
            <span className="text-sm font-medium">
              {user?.userType === 'investor' 
                ? `Portfolio: $${displayBalance.toLocaleString()}` 
                : `XRP: ${displayBalance.toFixed(2)}`
              }
            </span>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="h-5 w-5" />
                {userNotifications.some(n => n.unread) && (
                  <span className="absolute -top-1 -right-1 w-3 h-3 bg-destructive rounded-full"></span>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel className="flex items-center justify-between">
                <span>Notifications</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">
                    {userNotifications.filter(n => n.unread).length} unread
                  </span>
                  {userNotifications.length > 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 px-2 text-xs"
                      onClick={clearAllNotifications}
                    >
                      <Trash2 className="h-3 w-3 mr-1" />
                      Clear All
                    </Button>
                  )}
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              {userNotifications.length === 0 ? (
                <DropdownMenuItem disabled>
                  <div className="flex items-center justify-center w-full py-8">
                    <div className="text-center">
                      <Bell className="h-8 w-8 text-muted-foreground mx-auto mb-2 opacity-50" />
                      <p className="text-muted-foreground text-sm">No notifications</p>
                      <p className="text-muted-foreground text-xs mt-1 mb-3">You're all caught up!</p>
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-xs"
                        onClick={(e) => {
                          e.stopPropagation();
                          addDemoNotification();
                        }}
                      >
                        + Add Demo Notification
                      </Button>
                    </div>
                  </div>
                </DropdownMenuItem>
              ) : (
                userNotifications.map((notification) => (
                  <DropdownMenuItem key={notification.id} className="p-0 group">
                    <div className="flex items-start gap-3 w-full p-3">
                      <div className={`mt-1 w-2 h-2 rounded-full flex-shrink-0 ${
                        notification.type === 'success' ? 'bg-green-500' :
                        notification.type === 'income' ? 'bg-blue-500' :
                        notification.type === 'error' ? 'bg-red-500' :
                        'bg-gray-500'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className={`text-sm font-medium ${notification.unread ? 'text-foreground' : 'text-muted-foreground'}`}>
                              {notification.title}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                              {notification.message}
                            </p>
                            <div className="flex items-center gap-1 mt-2">
                              <Clock className="h-3 w-3 text-muted-foreground" />
                              <span className="text-xs text-muted-foreground">{notification.time}</span>
                              {notification.unread && (
                                <span className="ml-2 w-2 h-2 bg-blue-500 rounded-full"></span>
                              )}
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 ml-2 opacity-0 group-hover:opacity-100 hover:bg-destructive/10"
                            onClick={(e) => {
                              e.stopPropagation();
                              clearNotification(notification.id);
                            }}
                          >
                            <X className="h-3 w-3 text-muted-foreground hover:text-destructive" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </DropdownMenuItem>
                ))
              )}
              {userNotifications.length > 0 && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="text-center p-0">
                    <div className="w-full p-2">
                      <Button variant="ghost" size="sm" className="text-xs w-full">
                        View all notifications
                      </Button>
                    </div>
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
