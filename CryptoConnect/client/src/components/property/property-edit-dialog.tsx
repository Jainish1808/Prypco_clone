import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Plus, X } from "lucide-react";
import { api, Property } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface PropertyEditDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  property: Property;
}

export function PropertyEditDialog({ open, onOpenChange, property }: PropertyEditDialogProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState({
    title: property.title,
    description: property.description,
    address: property.address,
    city: property.city,
    country: property.country,
    property_type: property.property_type,
    total_value: property.total_value,
    size_sqm: property.size_sqm,
    bedrooms: property.bedrooms || "",
    bathrooms: property.bathrooms || "",
    parking_spaces: property.parking_spaces || "",
    year_built: property.year_built || "",
    monthly_rent: property.monthly_rent || "",
  });

  const updateMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const cleanData = {
        ...data,
        bedrooms: data.bedrooms ? parseInt(data.bedrooms.toString()) : undefined,
        bathrooms: data.bathrooms ? parseInt(data.bathrooms.toString()) : undefined,
        parking_spaces: data.parking_spaces ? parseInt(data.parking_spaces.toString()) : undefined,
        year_built: data.year_built ? parseInt(data.year_built.toString()) : undefined,
        monthly_rent: data.monthly_rent ? parseFloat(data.monthly_rent.toString()) : undefined,
      };
      return api.updateSellerProperty(property.id, cleanData);
    },
    onSuccess: () => {
      toast({
        title: "Property Updated",
        description: "Your property has been updated successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/seller/properties"] });
      queryClient.invalidateQueries({ queryKey: [`/api/seller/property/${property.id}`] });
      onOpenChange(false);
    },
    onError: (error: Error) => {
      toast({
        title: "Update Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!formData.title.trim() || !formData.address.trim()) {
      toast({
        title: "Validation Error",
        description: "Title and address are required.",
        variant: "destructive",
      });
      return;
    }

    if (formData.total_value <= 0 || formData.size_sqm <= 0) {
      toast({
        title: "Validation Error",
        description: "Total value and size must be positive numbers.",
        variant: "destructive",
      });
      return;
    }

    updateMutation.mutate(formData);
  };

  const handleInputChange = (field: string, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>Edit Property</DialogTitle>
          <p className="text-sm text-muted-foreground">
            Update your property details. Note: Only properties with "Pending Review" status can be edited.
          </p>
        </DialogHeader>

        <ScrollArea className="max-h-[60vh] pr-4">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="font-semibold">Basic Information</h3>
              
              <div>
                <Label htmlFor="title">Property Title *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  placeholder="Enter property title"
                  required
                />
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Describe your property"
                  rows={3}
                />
              </div>

              <div>
                <Label htmlFor="property_type">Property Type</Label>
                <Select
                  value={formData.property_type}
                  onValueChange={(value) => handleInputChange('property_type', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select property type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="apartment">Apartment</SelectItem>
                    <SelectItem value="villa">Villa</SelectItem>
                    <SelectItem value="office">Office</SelectItem>
                    <SelectItem value="retail">Retail</SelectItem>
                    <SelectItem value="warehouse">Warehouse</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Location */}
            <div className="space-y-4">
              <h3 className="font-semibold">Location</h3>
              
              <div>
                <Label htmlFor="address">Address *</Label>
                <Input
                  id="address"
                  value={formData.address}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                  placeholder="Enter full address"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    value={formData.city}
                    onChange={(e) => handleInputChange('city', e.target.value)}
                    placeholder="City"
                  />
                </div>
                <div>
                  <Label htmlFor="country">Country</Label>
                  <Input
                    id="country"
                    value={formData.country}
                    onChange={(e) => handleInputChange('country', e.target.value)}
                    placeholder="Country"
                  />
                </div>
              </div>
            </div>

            {/* Financial Details */}
            <div className="space-y-4">
              <h3 className="font-semibold">Financial Details</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="total_value">Total Value (AED) *</Label>
                  <Input
                    id="total_value"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.total_value}
                    onChange={(e) => handleInputChange('total_value', parseFloat(e.target.value) || 0)}
                    placeholder="0"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="size_sqm">Size (sq m) *</Label>
                  <Input
                    id="size_sqm"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.size_sqm}
                    onChange={(e) => handleInputChange('size_sqm', parseFloat(e.target.value) || 0)}
                    placeholder="0"
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="monthly_rent">Monthly Rent (AED)</Label>
                <Input
                  id="monthly_rent"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.monthly_rent}
                  onChange={(e) => handleInputChange('monthly_rent', e.target.value)}
                  placeholder="Optional - for yield calculation"
                />
              </div>
            </div>

            {/* Property Features */}
            <div className="space-y-4">
              <h3 className="font-semibold">Property Features</h3>
              
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="bedrooms">Bedrooms</Label>
                  <Input
                    id="bedrooms"
                    type="number"
                    min="0"
                    value={formData.bedrooms}
                    onChange={(e) => handleInputChange('bedrooms', e.target.value)}
                    placeholder="0"
                  />
                </div>
                <div>
                  <Label htmlFor="bathrooms">Bathrooms</Label>
                  <Input
                    id="bathrooms"
                    type="number"
                    min="0"
                    value={formData.bathrooms}
                    onChange={(e) => handleInputChange('bathrooms', e.target.value)}
                    placeholder="0"
                  />
                </div>
                <div>
                  <Label htmlFor="parking_spaces">Parking Spaces</Label>
                  <Input
                    id="parking_spaces"
                    type="number"
                    min="0"
                    value={formData.parking_spaces}
                    onChange={(e) => handleInputChange('parking_spaces', e.target.value)}
                    placeholder="0"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="year_built">Year Built</Label>
                <Input
                  id="year_built"
                  type="number"
                  min="1800"
                  max={new Date().getFullYear()}
                  value={formData.year_built}
                  onChange={(e) => handleInputChange('year_built', e.target.value)}
                  placeholder="YYYY"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-6 border-t">
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={updateMutation.isPending}
                className="flex-1"
              >
                {updateMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Updating...
                  </>
                ) : (
                  'Update Property'
                )}
              </Button>
            </div>
          </form>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}