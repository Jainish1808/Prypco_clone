import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CheckCircle, XCircle, Eye, Edit, Users, Building, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { api, Property, User } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";

interface AdminDashboardProps {
  onPropertyView: (propertyId: string) => void;
  onPropertyEdit: (propertyId: string) => void;
}

export default function AdminDashboard({ onPropertyView, onPropertyEdit }: AdminDashboardProps) {
  const { user } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Check if user is admin
  if (user?.userType !== 'admin') {
    return (
      <Card className="p-8 text-center">
        <CardContent>
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Access Denied</h3>
          <p className="text-muted-foreground">You don't have permission to access the admin dashboard.</p>
        </CardContent>
      </Card>
    );
  }

  // Fetch all properties for admin
  const { data: allProperties, isLoading: propertiesLoading } = useQuery({
    queryKey: ["/api/admin/properties"],
    queryFn: async () => {
      const response = await fetch('/api/admin/properties', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error('Failed to fetch properties');
      return response.json();
    },
  });

  // Fetch all users for admin
  const { data: allUsers, isLoading: usersLoading } = useQuery({
    queryKey: ["/api/admin/users"],
    queryFn: async () => {
      const response = await fetch('/api/admin/users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error('Failed to fetch users');
      return response.json();
    },
  });

  // Property approval mutation
  const propertyApprovalMutation = useMutation({
    mutationFn: async ({ propertyId, action }: { propertyId: string; action: 'approve' | 'reject' }) => {
      const response = await fetch(`/api/admin/properties/${propertyId}/${action}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error(`Failed to ${action} property`);
      return response.json();
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/properties"] });
      toast({
        title: `Property ${variables.action}d`,
        description: `Property has been ${variables.action}d successfully.`,
      });
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "An error occurred",
        variant: "destructive",
      });
    },
  });

  // KYC verification mutation
  const kycVerificationMutation = useMutation({
    mutationFn: async ({ userId, action }: { userId: string; action: 'verify' | 'reject' }) => {
      const response = await fetch(`/api/admin/users/${userId}/kyc/${action}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error(`Failed to ${action} KYC`);
      return response.json();
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/users"] });
      toast({
        title: `KYC ${variables.action}d`,
        description: `User KYC has been ${variables.action}d successfully.`,
      });
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "An error occurred",
        variant: "destructive",
      });
    },
  });

  const getStatusColor = (status: string) => {
    const normalizedStatus = status.toLowerCase().replace('propertystatus.', '');
    switch (normalizedStatus) {
      case 'pending_review':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'approved':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'rejected':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'tokenized':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusText = (status: string) => {
    const normalizedStatus = status.toLowerCase().replace('propertystatus.', '');
    switch (normalizedStatus) {
      case 'pending_review': return 'Pending Review';
      case 'approved': return 'Approved';
      case 'rejected': return 'Rejected';
      case 'tokenized': return 'Live';
      default: return status;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Admin Dashboard</h2>
          <p className="text-muted-foreground">Manage properties and verify users</p>
        </div>
      </div>

      <Tabs defaultValue="properties" className="space-y-6">
        <TabsList>
          <TabsTrigger value="properties" className="flex items-center gap-2">
            <Building className="h-4 w-4" />
            Property Management
          </TabsTrigger>
          <TabsTrigger value="users" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            User Management
          </TabsTrigger>
        </TabsList>

        <TabsContent value="properties" className="space-y-4">
          <div className="grid gap-4">
            {propertiesLoading ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <p>Loading properties...</p>
                </CardContent>
              </Card>
            ) : allProperties?.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <Building className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No properties found.</p>
                </CardContent>
              </Card>
            ) : (
              allProperties?.map((property: Property) => (
                <Card key={property.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <CardTitle className="text-lg">{property.title}</CardTitle>
                        <p className="text-sm text-muted-foreground">
                          {property.address} • {property.city}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          Seller: {property.seller_name}
                        </p>
                      </div>
                      <Badge className={`${getStatusColor(property.status)} border`}>
                        {getStatusText(property.status)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <p className="text-sm font-medium">Property Value</p>
                        <p className="text-sm text-muted-foreground">
                          AED {property.total_value.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm font-medium">Size</p>
                        <p className="text-sm text-muted-foreground">{property.size_sqm} sq m</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium">Total Tokens</p>
                        <p className="text-sm text-muted-foreground">
                          {property.total_tokens.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm font-medium">Token Price</p>
                        <p className="text-sm text-muted-foreground">AED {property.token_price}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onPropertyView(property.id)}
                        className="flex items-center gap-2"
                      >
                        <Eye className="h-4 w-4" />
                        View
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onPropertyEdit(property.id)}
                        className="flex items-center gap-2"
                      >
                        <Edit className="h-4 w-4" />
                        Edit
                      </Button>
                      
                      {(property.status.toLowerCase().replace('propertystatus.', '') === 'pending_review') && (
                        <>
                          <Button
                            variant="default"
                            size="sm"
                            onClick={() => propertyApprovalMutation.mutate({ 
                              propertyId: property.id, 
                              action: 'approve' 
                            })}
                            disabled={propertyApprovalMutation.isPending}
                            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700"
                          >
                            <CheckCircle className="h-4 w-4" />
                            Approve
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => propertyApprovalMutation.mutate({ 
                              propertyId: property.id, 
                              action: 'reject' 
                            })}
                            disabled={propertyApprovalMutation.isPending}
                            className="flex items-center gap-2"
                          >
                            <XCircle className="h-4 w-4" />
                            Reject
                          </Button>
                        </>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        <TabsContent value="users" className="space-y-4">
          <div className="grid gap-4">
            {usersLoading ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <p>Loading users...</p>
                </CardContent>
              </Card>
            ) : allUsers?.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No users found.</p>
                </CardContent>
              </Card>
            ) : (
              allUsers?.map((user: User) => (
                <Card key={user.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <CardTitle className="text-lg">
                          {user.firstName} {user.lastName}
                        </CardTitle>
                        <p className="text-sm text-muted-foreground">{user.email}</p>
                        <p className="text-sm text-muted-foreground">
                          Role: {user.userType} • Username: {user.username}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={`${
                          user.isKYCVerified 
                            ? 'bg-emerald-100 text-emerald-800 border-emerald-200' 
                            : 'bg-amber-100 text-amber-800 border-amber-200'
                        } border`}>
                          {user.isKYCVerified ? 'KYC Verified' : 'Pending KYC'}
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  {!user.isKYCVerified && (
                    <CardContent>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="default"
                          size="sm"
                          onClick={() => kycVerificationMutation.mutate({ 
                            userId: user.id, 
                            action: 'verify' 
                          })}
                          disabled={kycVerificationMutation.isPending}
                          className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700"
                        >
                          <CheckCircle className="h-4 w-4" />
                          Verify KYC
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => kycVerificationMutation.mutate({ 
                            userId: user.id, 
                            action: 'reject' 
                          })}
                          disabled={kycVerificationMutation.isPending}
                          className="flex items-center gap-2"
                        >
                          <XCircle className="h-4 w-4" />
                          Reject KYC
                        </Button>
                      </div>
                    </CardContent>
                  )}
                </Card>
              ))
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}