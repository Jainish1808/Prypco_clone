import { Button } from "@/components/ui/button";
import { Menu, Bell, Wallet } from "lucide-react";
import type { PageView } from "@/pages/home-page";

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
  }
};

export default function Header({ currentPage, onMenuClick }: HeaderProps) {
  const config = pageConfig[currentPage] || pageConfig.dashboard;

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
            <span className="text-sm font-medium">Balance: $12,450</span>
          </div>
          <Button variant="ghost" size="sm" className="relative">
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-destructive rounded-full"></span>
          </Button>
        </div>
      </div>
    </header>
  );
}
