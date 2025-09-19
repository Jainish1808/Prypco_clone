import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Building, 
  MapPin, 
  DollarSign, 
  Users, 
  Coins,
  Eye,
  Edit,
  Calendar,
  TrendingUp
} from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import type { Property } from "@/lib/api";
import { PropertyDetailsDialog } from "@/components/property/property-details-dialog";
import { PropertyEditDialog } from "@/components/property/property-edit-dialog";

export default function MyProperties() {
  const { user } = useAuth();
  const [selectedPropertyId, setSelectedPropertyId] = useState<string | null>(null);
  const [editingProperty, setEditingProperty] = useState<Property | null>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);

  const { data: properties, isLoading, error } = useQuery({
    queryKey: ["/api/seller/properties"],
    queryFn: () => api.getSellerProperties(),
  });

  const handleViewProperty = (propertyId: string) => {
    setSelectedPropertyId(propertyId);
    setViewDialogOpen(true);
  };

  const handleEditProperty = (property: Property) => {
    setEditingProperty(property);
    setEditDialogOpen(true);
  };

  // Check if user can edit a specific property
  const canEditProperty = (property: Property) => {
    // Admin can edit any property
    if (user?.userType === 'admin') return true;
    
    // Sellers can only edit their own properties (since this is MyProperties page, they're all owned by current seller)
    if (user?.userType === 'seller') {
      return true;
    }
    
    // Investors cannot edit properties
    return false;
  };

  // Check if property is in editable state
  const isPropertyEditable = (property: Property) => {
    return property.status === "pending_review" || property.status === "rejected";
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending_review":
        return "bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100";
      case "approved":
        return "bg-green-50 text-green-700 border-green-200 hover:bg-green-100";
      case "rejected":
        return "bg-red-50 text-red-700 border-red-200 hover:bg-red-100";
      case "tokenized":
        return "bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100";
      case "sold_out":
        return "bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100";
      default:
        return "bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "pending_review":
        return "Under Review";
      case "approved":
        return "Approved";
      case "rejected":
        return "Rejected";
      case "tokenized":
        return "Live";
      case "sold_out":
        return "Fully Funded";
      default:
        return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">My Properties</h1>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">My Properties</h1>
        </div>
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-red-600 mb-4">Error loading properties: {error.message}</p>
            <Button onClick={() => window.location.reload()}>Retry</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">My Properties</h1>
          <p className="text-muted-foreground">Track your submitted properties</p>
        </div>
        <div className="text-sm text-muted-foreground">
          {Array.isArray(properties) ? properties.length : 0} properties
        </div>
      </div>

      {!properties || properties.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Building className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Properties Yet</h3>
            <p className="text-muted-foreground mb-4">
              You haven't submitted any properties for tokenization yet.
            </p>
            <Button>Submit Your First Property</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {properties.map((property: Property) => (
            <Card key={property.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg line-clamp-1">{property.title}</CardTitle>
                    <div className="flex items-center text-sm text-muted-foreground mt-1">
                      <MapPin className="h-3 w-3 mr-1" />
                      {property.city}, {property.country}
                    </div>
                  </div>
                  <Badge 
                    className={`${getStatusColor(property.status)} border font-medium px-2.5 py-0.5 text-xs rounded-full transition-colors`}
                    variant="outline"
                  >
                    {getStatusText(property.status)}
                  </Badge>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Property Value</p>
                    <p className="font-semibold">AED {property.total_value.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Size</p>
                    <p className="font-semibold">{property.size_sqm} sq m</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Total Tokens</p>
                    <p className="font-semibold">{property.total_tokens.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Token Price</p>
                    <p className="font-semibold">${property.token_price.toFixed(2)}</p>
                  </div>
                </div>

                {property.tokens_sold > 0 && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Tokens Sold</span>
                      <span>{property.tokens_sold.toLocaleString()} / {property.total_tokens.toLocaleString()}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary h-2 rounded-full" 
                        style={{ width: `${(property.tokens_sold / property.total_tokens) * 100}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {((property.tokens_sold / property.total_tokens) * 100).toFixed(1)}% funded
                    </p>
                  </div>
                )}

                <div className="flex items-center justify-between pt-2 border-t">
                  <div className="flex items-center text-xs text-muted-foreground">
                    <Calendar className="h-3 w-3 mr-1" />
                    {new Date(property.created_at).toLocaleDateString()}
                  </div>
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleViewProperty(property.id)}
                    >
                      <Eye className="h-3 w-3 mr-1" />
                      View
                    </Button>
                    {canEditProperty(property) && isPropertyEditable(property) && (
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleEditProperty(property)}
                      >
                        <Edit className="h-3 w-3 mr-1" />
                        Edit
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Dialogs */}
      {selectedPropertyId && (
        <PropertyDetailsDialog
          open={viewDialogOpen}
          onOpenChange={setViewDialogOpen}
          propertyId={selectedPropertyId}
        />
      )}
      
      {editingProperty && (
        <PropertyEditDialog
          open={editDialogOpen}
          onOpenChange={setEditDialogOpen}
          property={editingProperty}
        />
      )}
    </div>
  );
}