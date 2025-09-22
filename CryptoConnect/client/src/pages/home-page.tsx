import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/sidebar";
import Header from "@/components/layout/header";
import InvestorDashboard from "@/pages/investor-dashboard";
import SellerDashboard from "@/pages/seller-dashboard";
import Properties from "@/pages/properties";
import Portfolio from "@/pages/portfolio";
import SecondaryMarket from "@/pages/secondary-market";
import IncomeHistory from "@/pages/income-history";
import PropertySubmission from "@/pages/property-submission";
import MyProperties from "@/pages/my-properties";
import Analytics from "@/pages/analytics";
import AdminDashboard from "@/components/AdminDashboard";
import { PropertyDetailsDialog } from "@/components/property/property-details-dialog";
import { PropertyEditDialog } from "@/components/property/property-edit-dialog";

export type UserPanel = "investor" | "seller" | "admin";
export type PageView = 
  | "dashboard" 
  | "properties" 
  | "portfolio" 
  | "market" 
  | "income"
  | "seller-dashboard" 
  | "submit-property" 
  | "my-properties" 
  | "analytics"
  | "admin-dashboard";

export default function HomePage() {
  const { user } = useAuth();
  
  // Role-based panel determination - NO MANUAL SWITCHING
  const getUserPanel = (): UserPanel => {
    if (!user) return "investor";
    switch (user.userType) {
      case "admin":
        return "admin";
      case "seller":
        return "seller";
      case "investor":
      default:
        return "investor";
    }
  };
  
  // Role-based default page
  const getDefaultPage = (): PageView => {
    if (!user) return "dashboard";
    switch (user.userType) {
      case "admin":
        return "admin-dashboard";
      case "seller":
        return "seller-dashboard";
      case "investor":
      default:
        return "dashboard";
    }
  };
  
  const [currentPanel] = useState<UserPanel>(getUserPanel());
  const [currentPage, setCurrentPage] = useState<PageView>(getDefaultPage());
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [viewPropertyId, setViewPropertyId] = useState<string | null>(null);
  const [editPropertyId, setEditPropertyId] = useState<string | null>(null);
  const [propertyDetailsOpen, setPropertyDetailsOpen] = useState(false);
  const [propertyEditOpen, setPropertyEditOpen] = useState(false);

  // Fetch property data for editing
  const { data: editProperty } = useQuery({
    queryKey: [`/api/admin/properties/${editPropertyId}`],
    queryFn: async () => {
      if (!editPropertyId) return null;
      const response = await fetch(`/api/admin/properties/${editPropertyId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error('Failed to fetch property');
      return response.json();
    },
    enabled: !!editPropertyId,
  });

  // Role-based page validation - prevent access to unauthorized pages
  const isPageAllowedForRole = (page: PageView, userType: string): boolean => {
    const investorPages: PageView[] = ["dashboard", "properties", "portfolio", "market", "income"];
    const sellerPages: PageView[] = ["seller-dashboard", "submit-property", "my-properties", "analytics"];
    const adminPages: PageView[] = ["admin-dashboard"];
    
    switch (userType) {
      case "admin":
        return [...investorPages, ...sellerPages, ...adminPages].includes(page);
      case "seller":
        return sellerPages.includes(page);
      case "investor":
      default:
        return investorPages.includes(page);
    }
  };

  const handlePageChange = (page: PageView) => {
    // Validate user has access to this page
    if (!user || !isPageAllowedForRole(page, user.userType)) {
      console.warn(`Access denied: ${user?.userType || 'unknown'} cannot access ${page}`);
      return;
    }
    
    setCurrentPage(page);
    setSidebarOpen(false); // Close mobile sidebar after navigation
  };

  const handlePropertyView = (propertyId: string) => {
    setViewPropertyId(propertyId);
    setPropertyDetailsOpen(true);
  };

  const handlePropertyEdit = (propertyId: string) => {
    setEditPropertyId(propertyId);
    setPropertyEditOpen(true);
  };

  const renderContent = () => {
    switch (currentPage) {
      case "dashboard":
        return <InvestorDashboard />;
      case "properties":
        return <Properties />;
      case "portfolio":
        return <Portfolio onNavigateToProperties={() => handlePageChange("properties")} />;
      case "market":
        return <SecondaryMarket />;
      case "income":
        return <IncomeHistory onNavigateToPortfolio={() => handlePageChange("portfolio")} />;
      case "seller-dashboard":
        return <SellerDashboard onNavigate={handlePageChange} />;
      case "submit-property":
        return <PropertySubmission onNavigate={handlePageChange} />;
      case "my-properties":
        return <MyProperties />;
      case "analytics":
        return <Analytics />;
      case "admin-dashboard":
        return (
          <AdminDashboard 
            onPropertyView={handlePropertyView}
            onPropertyEdit={handlePropertyEdit}
          />
        );
      default:
        return user?.userType === "admin" ? (
          <AdminDashboard 
            onPropertyView={handlePropertyView}
            onPropertyEdit={handlePropertyEdit}
          />
        ) : <InvestorDashboard />;
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
        <Sidebar
          currentPanel={currentPanel}
          currentPage={currentPage}
          onPageChange={handlePageChange}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />      <div className="flex-1 lg:ml-0">
        <Header 
          currentPage={currentPage}
          onMenuClick={() => setSidebarOpen(true)}
        />
        
        <main className="p-6 space-y-6">
          {renderContent()}
        </main>
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Property Details Dialog */}
      {viewPropertyId && (
        <PropertyDetailsDialog
          open={propertyDetailsOpen}
          onOpenChange={(open) => {
            setPropertyDetailsOpen(open);
            if (!open) {
              setViewPropertyId(null);
            }
          }}
          propertyId={viewPropertyId}
          isAdmin={user?.userType === 'admin'}
        />
      )}

      {/* Property Edit Dialog */}
      {editProperty && (
        <PropertyEditDialog
          open={propertyEditOpen}
          onOpenChange={(open) => {
            setPropertyEditOpen(open);
            if (!open) {
              setEditPropertyId(null);
            }
          }}
          property={editProperty}
        />
      )}
    </div>
  );
}
