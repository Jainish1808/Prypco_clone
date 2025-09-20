import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Wallet,
  ExternalLink,
  Copy,
  RefreshCw,
  Eye,
  TrendingUp,
  ArrowUpRight,
  ArrowDownLeft,
  Clock,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";

interface WalletData {
  address: string;
  xrp_balance: number;
  tokens: Array<{
    symbol: string;
    balance: number;
    issuer: string;
    property_info?: {
      id: string;
      title: string;
      city: string;
      country: string;
    };
  }>;
  transactions: Array<{
    hash: string;
    type: string;
    date: number;
    amount: any;
    destination: string;
    explorer_url: string;
  }>;
  explorer_url: string;
}

export default function WalletWidget() {
  const { toast } = useToast();
  const [walletData, setWalletData] = useState<WalletData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWalletData();
  }, []);

  const loadWalletData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Get real wallet info from API
      const response = await fetch('/api/simple-wallet/info', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        if (response.status === 404) {
          setError('No wallet assigned to user');
          return;
        }
        throw new Error('Failed to fetch wallet data');
      }
      
      const walletData = await response.json();
      setWalletData(walletData);
    } catch (error: any) {
      console.error("Error loading wallet data:", error);
      setError("Failed to load wallet data");
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied!",
      description: "Address copied to clipboard",
    });
  };

  const formatAddress = (address: string) => {
    if (!address) return "";
    return `${address.slice(0, 8)}...${address.slice(-8)}`;
  };

  const formatTime = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-6 w-6 animate-spin mr-2" />
            Loading wallet...
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center">
            <Wallet className="h-12 w-12 mx-auto mb-2 text-gray-400" />
            <p className="text-gray-500">{error}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={loadWalletData}
              className="mt-2"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!walletData) return null;

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wallet className="h-5 w-5" />
            XRP Wallet
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              Connected
            </Badge>
            <Button variant="ghost" size="sm" onClick={loadWalletData}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Wallet Address */}
        <div>
          <label className="text-sm font-medium text-gray-600">
            Wallet Address
          </label>
          <div className="flex items-center gap-2 mt-1">
            <code className="flex-1 p-2 bg-gray-100 rounded text-sm font-mono">
              {formatAddress(walletData.address)}
            </code>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(walletData.address)}
            >
              <Copy className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => window.open(walletData.explorer_url, "_blank")}
            >
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Balance Section */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center gap-2 text-blue-600 mb-1">
              <TrendingUp className="h-4 w-4" />
              <span className="text-sm font-medium">XRP Balance</span>
            </div>
            <div className="text-2xl font-bold text-blue-700">
              {walletData.xrp_balance.toFixed(6)}
            </div>
            <div className="text-xs text-blue-600">XRP</div>
          </div>

          <div className="p-4 bg-green-50 rounded-lg">
            <div className="flex items-center gap-2 text-green-600 mb-1">
              <Wallet className="h-4 w-4" />
              <span className="text-sm font-medium">Property Tokens</span>
            </div>
            <div className="text-2xl font-bold text-green-700">
              {walletData.tokens.length}
            </div>
            <div className="text-xs text-green-600">Types</div>
          </div>
        </div>

        {/* Property Tokens */}
        {walletData.tokens.length > 0 && (
          <div>
            <h4 className="font-medium mb-3">Property Tokens</h4>
            <div className="space-y-2">
              {walletData.tokens.map((token, index) => (
                <div key={index} className="p-3 border rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{token.symbol}</div>
                      {token.property_info && (
                        <div className="text-sm text-gray-600">
                          {token.property_info.title}
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="font-bold">
                        {token.balance.toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-500">tokens</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Transactions */}
        <div>
          <h4 className="font-medium mb-3">Recent Transactions</h4>
          {walletData.transactions.length > 0 ? (
            <div className="space-y-2">
              {walletData.transactions.slice(0, 3).map((tx, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-100 rounded-full">
                      {tx.type === "Payment" ? (
                        <ArrowUpRight className="h-4 w-4 text-red-600" />
                      ) : (
                        <ArrowDownLeft className="h-4 w-4 text-green-600" />
                      )}
                    </div>
                    <div>
                      <div className="font-medium">{tx.type}</div>
                      <div className="text-sm text-gray-600 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatTime(tx.date)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-right">
                      <div className="font-medium">{tx.amount}</div>
                      <div className="text-sm text-gray-500">XRP</div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => window.open(tx.explorer_url, "_blank")}
                    >
                      <ExternalLink className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500">
              <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No transactions yet</p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => window.open(walletData.explorer_url, "_blank")}
            className="flex-1"
          >
            <Eye className="h-4 w-4 mr-2" />
            View on Explorer
          </Button>
          <Button variant="outline" onClick={loadWalletData} className="flex-1">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
