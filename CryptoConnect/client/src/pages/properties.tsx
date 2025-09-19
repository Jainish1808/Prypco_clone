import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2 } from "lucide-react";
import PropertyCard from "@/components/property/property-card";
import { api, Property } from "@/lib/api";

export default function Properties() {
  const [locationFilter, setLocationFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");

  const { data: properties, isLoading, error } = useQuery<Property[]>({
    queryKey: ["/api/properties", { type: typeFilter === "all" ? undefined : typeFilter }],
    queryFn: () => api.getProperties(),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-8 text-center">
        <CardContent>
          <p className="text-destructive">Failed to load properties. Please try again.</p>
          <Button className="mt-4" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  const filteredProperties = properties?.filter(property => {
    if (locationFilter !== "all") {
      // Simple location filtering based on city
      const locationMatch = property.city.toLowerCase().includes(locationFilter.toLowerCase());
      if (!locationMatch) return false;
    }
    if (typeFilter !== "all") {
      if (property.property_type !== typeFilter) return false;
    }
    return true;
  }) || [];

  return (
    <div className="space-y-6">
      {/* Header and Filters */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">Available Properties</h2>
          <p className="text-muted-foreground">Discover tokenized real estate investment opportunities</p>
        </div>
        
        <div className="flex items-center gap-3">
          <Select value={locationFilter} onValueChange={setLocationFilter}>
            <SelectTrigger className="w-40" data-testid="select-location-filter">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Locations</SelectItem>
              <SelectItem value="dubai">Dubai</SelectItem>
              <SelectItem value="abu dhabi">Abu Dhabi</SelectItem>
              <SelectItem value="sharjah">Sharjah</SelectItem>
              <SelectItem value="ajman">Ajman</SelectItem>
            </SelectContent>
          </Select>
          
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-40" data-testid="select-type-filter">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="apartment">Apartment</SelectItem>
              <SelectItem value="villa">Villa</SelectItem>
              <SelectItem value="office">Office</SelectItem>
              <SelectItem value="retail">Retail</SelectItem>
              <SelectItem value="warehouse">Warehouse</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Properties Grid */}
      {filteredProperties.length === 0 ? (
        <Card className="p-8 text-center">
          <CardContent>
            <p className="text-muted-foreground">No properties found matching your criteria.</p>
            <p className="text-sm text-muted-foreground mt-2">Try adjusting your filters or check back later for new listings.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredProperties.map((property) => (
            <PropertyCard key={property.id} property={property} />
          ))}
        </div>
      )}

      {/* Load More Button (if needed for pagination) */}
      {filteredProperties.length > 0 && properties && properties.length >= 20 && (
        <div className="text-center">
          <Button variant="outline" data-testid="button-load-more">
            Load More Properties
          </Button>
        </div>
      )}
    </div>
  );
}
