import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  MapPin, 
  Home, 
  Calendar, 
  DollarSign, 
  Coins, 
  Bed, 
  Bath, 
  Car,
  Building,
  TrendingUp
} from "lucide-react";
import { api, Property } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface PropertyDetailsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  propertyId: string;
  isAdmin?: boolean;
}

export function PropertyDetailsDialog({ open, onOpenChange, propertyId, isAdmin = false }: PropertyDetailsDialogProps) {
  const { toast } = useToast();

  const { data: property, isLoading, error } = useQuery({
    queryKey: [isAdmin ? `/api/admin/properties/${propertyId}` : `/api/seller/property/${propertyId}`],
    queryFn: async () => {
      const endpoint = isAdmin ? `/api/admin/properties/${propertyId}` : `/api/seller/property/${propertyId}`;
      const response = await fetch(endpoint, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error('Failed to fetch property');
      return response.json();
    },
    enabled: open && !!propertyId,
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending_review":
        return "bg-yellow-100 text-yellow-800";
      case "approved":
        return "bg-green-100 text-green-800";
      case "rejected":
        return "bg-red-100 text-red-800";
      case "tokenized":
        return "bg-blue-100 text-blue-800";
      case "sold_out":
        return "bg-purple-100 text-purple-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "pending_review":
        return "Pending Review";
      case "approved":
        return "Approved";
      case "rejected":
        return "Rejected";
      case "tokenized":
        return "Tokenized";
      case "sold_out":
        return "Sold Out";
      default:
        return status;
    }
  };

  if (isLoading) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>Loading Property Details...</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-48 bg-gray-200 rounded"></div>
            <div className="space-y-2">
              <div className="h-3 bg-gray-200 rounded"></div>
              <div className="h-3 bg-gray-200 rounded w-2/3"></div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  if (error) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Error Loading Property</DialogTitle>
          </DialogHeader>
          <div className="text-center">
            <p className="text-red-600 mb-4">Failed to load property details</p>
            <Button onClick={() => onOpenChange(false)}>Close</Button>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  if (!property) {
    return null;
  }

  const soldPercentage = (property.tokens_sold / property.total_tokens) * 100;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh]">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div>
              <DialogTitle className="text-xl">{property.title}</DialogTitle>
              <div className="flex items-center text-muted-foreground mt-1">
                <MapPin className="h-4 w-4 mr-1" />
                {property.address}, {property.city}, {property.country}
              </div>
            </div>
            <Badge className={getStatusColor(property.status)}>
              {getStatusText(property.status)}
            </Badge>
          </div>
        </DialogHeader>

        <ScrollArea className="max-h-[60vh] pr-4">
          <div className="space-y-6">
            {/* Property Images */}
            {property.images && property.images.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold">Property Images</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {property.images.map((image, index) => (
                    <img
                      key={index}
                      src={`http://localhost:8000${image}`}
                      alt={`${property.title} - Image ${index + 1}`}
                      className="w-full h-48 object-cover rounded-lg border"
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Property Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="font-semibold flex items-center">
                  <Building className="h-4 w-4 mr-2" />
                  Property Information
                </h4>
                
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Type:</span>
                    <span className="font-medium capitalize">{property.property_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Size:</span>
                    <span className="font-medium">{property.size_sqm} sq m</span>
                  </div>
                  {property.year_built && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Year Built:</span>
                      <span className="font-medium">{property.year_built}</span>
                    </div>
                  )}
                  {(property.bedrooms || property.bathrooms || property.parking_spaces) && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Features:</span>
                      <div className="flex items-center gap-3">
                        {property.bedrooms && (
                          <div className="flex items-center gap-1">
                            <Bed className="h-3 w-3" />
                            <span>{property.bedrooms}</span>
                          </div>
                        )}
                        {property.bathrooms && (
                          <div className="flex items-center gap-1">
                            <Bath className="h-3 w-3" />
                            <span>{property.bathrooms}</span>
                          </div>
                        )}
                        {property.parking_spaces && (
                          <div className="flex items-center gap-1">
                            <Car className="h-3 w-3" />
                            <span>{property.parking_spaces}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold flex items-center">
                  <DollarSign className="h-4 w-4 mr-2" />
                  Financial Details
                </h4>
                
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Property Value:</span>
                    <span className="font-medium">AED {property.total_value.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Total Tokens:</span>
                    <span className="font-medium">{property.total_tokens.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Token Price:</span>
                    <span className="font-medium">AED {property.token_price.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Tokens Sold:</span>
                    <span className="font-medium">{property.tokens_sold.toLocaleString()}</span>
                  </div>
                  {property.monthly_rent && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Monthly Rent:</span>
                      <span className="font-medium">AED {property.monthly_rent.toLocaleString()}</span>
                    </div>
                  )}
                  {property.annual_yield && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Annual Yield:</span>
                      <span className="font-medium text-green-600">{property.annual_yield.toFixed(2)}%</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            {property.tokens_sold > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold flex items-center">
                  <Coins className="h-4 w-4 mr-2" />
                  Token Sales Progress
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Tokens Sold</span>
                    <span>{soldPercentage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-primary h-3 rounded-full transition-all duration-300" 
                      style={{ width: `${soldPercentage}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{property.tokens_sold.toLocaleString()} sold</span>
                    <span>{(property.total_tokens - property.tokens_sold).toLocaleString()} remaining</span>
                  </div>
                </div>
              </div>
            )}

            {/* Description */}
            {property.description && (
              <div className="space-y-2">
                <h4 className="font-semibold">Description</h4>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {property.description}
                </p>
              </div>
            )}

            {/* Timestamps */}
            <div className="space-y-2">
              <h4 className="font-semibold flex items-center">
                <Calendar className="h-4 w-4 mr-2" />
                Timeline
              </h4>
              <div className="space-y-2 text-xs text-muted-foreground">
                <div className="flex justify-between">
                  <span>Submitted:</span>
                  <span>{new Date(property.created_at).toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}