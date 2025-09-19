import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import Sidebar from "@/components/layout/sidebar";
import Header from "@/components/layout/header";
import InvestorDashboard from "@/pages/investor-dashboard";
import SellerDashboard from "@/pages/seller-dashboard";
import Properties from "@/pages/properties";
import Portfolio from "@/pages/portfolio";
import SecondaryMarket from "@/pages/secondary-market";
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
  const [currentPanel, setCurrentPanel] = useState<UserPanel>(
    user?.userType === "admin" ? "admin" : user?.userType || "investor"
  );
  const [currentPage, setCurrentPage] = useState<PageView>(
    user?.userType === "admin" ? "admin-dashboard" :
    currentPanel === "investor" ? "dashboard" : "seller-dashboard"
  );
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

  const handlePanelSwitch = (panel: UserPanel) => {
    setCurrentPanel(panel);
    if (panel === "admin") {
      setCurrentPage("admin-dashboard");
    } else {
      setCurrentPage(panel === "investor" ? "dashboard" : "seller-dashboard");
    }
  };

  const handlePageChange = (page: PageView) => {
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
        return <Portfolio />;
      case "market":
        return <SecondaryMarket />;
      case "income":
        return <div>Income History - Coming Soon</div>;
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
        onPanelSwitch={handlePanelSwitch}
        onPageChange={handlePageChange}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      
      <div className="flex-1 lg:ml-0">
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
