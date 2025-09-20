import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Home, Percent, Calendar, Loader2, MapPin, Bed, Bath, Car } from "lucide-react";
import { api, Property } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";
import { useNotifications } from "@/hooks/use-notifications";

interface PropertyCardProps {
  property: Property;
}

export default function PropertyCard({ property }: PropertyCardProps) {
  const { showToastAndNotification } = useNotifications();
  const [isInvestmentOpen, setIsInvestmentOpen] = useState(false);
  const [tokenAmount, setTokenAmount] = useState("");

  const investmentMutation = useMutation({
    mutationFn: async (investmentData: { property_id: string; investment_amount: number; tokens_to_purchase: number }) => {
      return await api.investInProperty(property.id, investmentData);
    },
    onSuccess: (data) => {
      showToastAndNotification(
        "Investment Successful",
        `You have successfully purchased ${tokenAmount} tokens!`,
        "success"
      );
      queryClient.invalidateQueries({ queryKey: ["/api/properties"] });
      queryClient.invalidateQueries({ queryKey: ["/api/investor/holdings"] });
      setIsInvestmentOpen(false);
      setTokenAmount("");
    },
    onError: (error: Error) => {
      // Enhanced error handling with more details
      let errorMessage = error.message;
      let errorTitle = "Investment Failed";
      
      if (error.message.includes("Failed to tokenize property")) {
        errorTitle = "Property Tokenization Failed";
        errorMessage = "The property could not be tokenized on the XRP Ledger. This might be due to XRP network issues or backend configuration problems. Please contact support.";
      } else if (error.message.includes("Not enough tokens available")) {
        errorTitle = "Insufficient Token Supply";
        errorMessage = "There are not enough tokens available for your requested investment amount. Please try a smaller amount.";
      } else if (error.message.includes("KYC")) {
        errorTitle = "KYC Verification Required";
        errorMessage = "Please complete your KYC verification before investing in properties.";
      } else if (error.message.includes("wallet")) {
        errorTitle = "Wallet Setup Required";
        errorMessage = "Your XRP wallet setup failed. Please try again or contact support.";
      }
      
      showToastAndNotification(
        errorTitle,
        errorMessage,
        "error"
      );
    },
  });

  const handleInvestment = (e: React.FormEvent) => {
    e.preventDefault();
    
    const tokens = parseInt(tokenAmount);
    if (!tokens || tokens < 100) {
      showToastAndNotification(
        "Invalid Amount",
        "Minimum investment is 100 tokens.",
        "error"
      );
      return;
    }

    const tokensAvailable = property.total_tokens - property.tokens_sold;
    if (tokens > tokensAvailable) {
      showToastAndNotification(
        "Insufficient Supply",
        "Not enough tokens available for this investment amount.",
        "error"
      );
      return;
    }

    const investmentAmount = tokens * property.token_price;

    investmentMutation.mutate({
      property_id: property.id,
      investment_amount: investmentAmount,
      tokens_to_purchase: tokens
    });
  };

  const totalInvestment = tokenAmount ? parseInt(tokenAmount) * property.token_price : 0;
  const ownershipPercent = tokenAmount ? (parseInt(tokenAmount) / property.total_tokens) * 100 : 0;
  
  // Calculate expected yearly income based on rental yield
  const expectedYearlyIncome = property.annual_yield ? totalInvestment * (property.annual_yield / 100) : 0;

  // Status badge color
  const getStatusColor = (status: string) => {
    switch (status) {
      case "listed":
        return "default";
      case "approved":
        return "secondary";
      default:
        return "outline";
    }
  };

  const soldPercentage = (property.tokens_sold / property.total_tokens) * 100;
  const tokensAvailable = property.total_tokens - property.tokens_sold;

  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow" data-testid={`property-card-${property.id}`}>
      {/* Property Image */}
      <div className="h-48 bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center relative">
        {property.images && property.images.length > 0 ? (
          <img
            src={`http://localhost:8000${property.images[0]}`}
            alt={property.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <Home className="h-16 w-16 text-primary/50" />
        )}
        <Badge 
          variant={getStatusColor(property.status)} 
          className="absolute top-2 right-2 text-xs"
        >
          {property.status === "tokenized" ? "Available" : property.status.replace('_', ' ')}
        </Badge>
      </div>
      
      <CardContent className="p-6">
        <h3 className="font-bold text-lg mb-2">{property.title}</h3>
        
        <div className="flex items-center gap-1 text-muted-foreground text-sm mb-3">
          <MapPin className="h-4 w-4" />
          <span>{property.city}, {property.country}</span>
        </div>

        {/* Property Details */}
        {(property.bedrooms || property.bathrooms || property.parking_spaces) && (
          <div className="flex items-center gap-4 mb-3 text-sm text-muted-foreground">
            {property.bedrooms && (
              <div className="flex items-center gap-1">
                <Bed className="h-4 w-4" />
                <span>{property.bedrooms}</span>
              </div>
            )}
            {property.bathrooms && (
              <div className="flex items-center gap-1">
                <Bath className="h-4 w-4" />
                <span>{property.bathrooms}</span>
              </div>
            )}
            {property.parking_spaces && (
              <div className="flex items-center gap-1">
                <Car className="h-4 w-4" />
                <span>{property.parking_spaces}</span>
              </div>
            )}
          </div>
        )}
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-sm text-muted-foreground">Property Value</p>
            <p className="font-bold">AED {property.total_value.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Token Price</p>
            <p className="font-bold text-primary">AED {property.token_price.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Total Tokens</p>
            <p className="font-medium">{property.total_tokens.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Available</p>
            <p className="font-medium text-green-600">{tokensAvailable.toLocaleString()}</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-1">
            <span>Sold</span>
            <span>{soldPercentage.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div 
              className="bg-primary h-2 rounded-full transition-all duration-300" 
              style={{ width: `${soldPercentage}%` }}
            />
          </div>
        </div>

        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Percent className="h-4 w-4 text-secondary" />
            <span className="text-sm">
              {property.annual_yield ? `Yield: ${property.annual_yield.toFixed(2)}%` : 'Yield: TBD'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">
              Listed {new Date(property.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>

        <Dialog open={isInvestmentOpen} onOpenChange={setIsInvestmentOpen}>
          <DialogTrigger asChild>
            <Button 
              className="w-full" 
              disabled={!["approved", "tokenized"].includes(property.status) || tokensAvailable === 0}
              data-testid="button-invest-now"
            >
              {!["approved", "tokenized"].includes(property.status)
                ? "Not Available" 
                : tokensAvailable === 0 
                ? "Sold Out" 
                : "Invest Now"
              }
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Invest in {property.title}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleInvestment} className="space-y-4">
              <div>
                <Label htmlFor="token-amount">Number of Tokens</Label>
                <Input
                  id="token-amount"
                  type="number"
                  min="100"
                  max={tokensAvailable}
                  value={tokenAmount}
                  onChange={(e) => setTokenAmount(e.target.value)}
                  placeholder={`Minimum: 100, Maximum: ${tokensAvailable.toLocaleString()}`}
                  required
                  data-testid="input-investment-tokens"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Minimum investment: 100 tokens (AED {(100 * property.token_price).toFixed(2)})
                </p>
              </div>

              {tokenAmount && (
                <div className="bg-muted p-3 rounded-lg space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Investment Amount:</span>
                    <span className="font-medium">AED {totalInvestment.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Ownership:</span>
                    <span className="font-medium">{ownershipPercent.toFixed(3)}%</span>
                  </div>
                  {expectedYearlyIncome > 0 && (
                    <div className="flex justify-between text-sm">
                      <span>Expected Yearly Income:</span>
                      <span className="font-medium text-green-600">AED {expectedYearlyIncome.toFixed(2)}</span>
                    </div>
                  )}
                </div>
              )}

              <div className="flex gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsInvestmentOpen(false)}
                  className="flex-1"
                  data-testid="button-cancel-investment"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={investmentMutation.isPending}
                  className="flex-1"
                  data-testid="button-confirm-investment"
                >
                  {investmentMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {property.xrplTokenCreated ? 'Processing Investment...' : 'Tokenizing Property...'}
                    </>
                  ) : (
                    `Invest AED ${totalInvestment.toLocaleString()}`
                  )}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
}
