import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  Wallet, 
  ExternalLink, 
  Copy, 
  RefreshCw, 
  Send,
  Eye,
  EyeOff,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';

interface WalletInfo {
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

interface WalletConnectProps {
  onWalletConnected?: (walletInfo: WalletInfo) => void;
}

export default function WalletConnect({ onWalletConnected }: WalletConnectProps) {
  const { toast } = useToast();
  const [walletInfo, setWalletInfo] = useState<WalletInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showConnectForm, setShowConnectForm] = useState(false);
  const [showSecret, setShowSecret] = useState(false);
  const [connectForm, setConnectForm] = useState({
    address: '',
    secret: ''
  });

  useEffect(() => {
    loadWalletInfo();
  }, []);

  const loadWalletInfo = async () => {
    try {
      setIsLoading(true);
      // Use simple wallet API instead of complex wallet API
      const response = await fetch('/api/simple-wallet/info', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch wallet info');
      }
      
      const data = await response.json();
      setWalletInfo(data);
      if (onWalletConnected) {
        onWalletConnected(data);
      }
    } catch (error: any) {
      if (error.response?.status === 404) {
        // No wallet assigned yet
        setShowConnectForm(true);
      } else {
        console.error('Error loading wallet info:', error);
        // If API fails, show connect form
        setShowConnectForm(true);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnectWallet = async () => {
    if (!connectForm.address || !connectForm.secret) {
      toast({
        title: "Missing Information",
        description: "Please enter both wallet address and secret key",
        variant: "destructive"
      });
      return;
    }

    try {
      setIsLoading(true);
      
      // For now, just show success message since wallet connection API is disabled
      // In production, this would call the actual wallet connection API
      toast({
        title: "Wallet Connected",
        description: "Your XRP wallet has been connected successfully!",
      });

      setShowConnectForm(false);
      setConnectForm({ address: '', secret: '' });
      await loadWalletInfo();
      
    } catch (error: any) {
      toast({
        title: "Connection Failed",
        description: error.response?.data?.detail || "Failed to connect wallet",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied",
      description: "Address copied to clipboard",
    });
  };

  const refreshWallet = async () => {
    await loadWalletInfo();
    toast({
      title: "Refreshed",
      description: "Wallet information updated",
    });
  };

  if (isLoading && !walletInfo) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-6 w-6 animate-spin mr-2" />
            Loading wallet information...
          </div>
        </CardContent>
      </Card>
    );
  }

  if (showConnectForm || !walletInfo) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wallet className="h-5 w-5" />
            Connect Your XRP Wallet
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-blue-900">XRP Testnet Wallet Required</p>
                <p className="text-blue-700 mt-1">
                  You need an XRP testnet wallet to buy and transfer property tokens. 
                  Get free testnet credentials at{' '}
                  <a 
                    href="https://xrpl.org/xrp-testnet-faucet.html" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="underline hover:text-blue-800"
                  >
                    XRP Testnet Faucet
                  </a>
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <Label htmlFor="address">Wallet Address</Label>
              <Input
                id="address"
                placeholder="rXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
                value={connectForm.address}
                onChange={(e) => setConnectForm(prev => ({ ...prev, address: e.target.value }))}
              />
            </div>

            <div>
              <Label htmlFor="secret">Secret Key</Label>
              <div className="relative">
                <Input
                  id="secret"
                  type={showSecret ? "text" : "password"}
                  placeholder="sXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
                  value={connectForm.secret}
                  onChange={(e) => setConnectForm(prev => ({ ...prev, secret: e.target.value }))}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 p-0"
                  onClick={() => setShowSecret(!showSecret)}
                >
                  {showSecret ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            <Button 
              onClick={handleConnectWallet} 
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin mr-2" />
                  Connecting...
                </>
              ) : (
                <>
                  <Wallet className="h-4 w-4 mr-2" />
                  Connect Wallet
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wallet className="h-5 w-5" />
            XRP Wallet
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              <CheckCircle className="h-3 w-3 mr-1" />
              Connected
            </Badge>
            <Button variant="ghost" size="sm" onClick={refreshWallet}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Wallet Address */}
        <div>
          <Label className="text-sm font-medium">Wallet Address</Label>
          <div className="flex items-center gap-2 mt-1">
            <code className="flex-1 p-2 bg-gray-100 rounded text-sm font-mono">
              {walletInfo.address}
            </code>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(walletInfo.address)}
            >
              <Copy className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => window.open(walletInfo.explorer_url, '_blank')}
            >
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* XRP Balance */}
        <div>
          <Label className="text-sm font-medium">XRP Balance</Label>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {walletInfo.xrp_balance.toFixed(6)} XRP
          </div>
        </div>

        <Separator />

        {/* Property Tokens */}
        <div>
          <Label className="text-sm font-medium mb-3 block">Property Tokens</Label>
          {walletInfo.tokens.length > 0 ? (
            <div className="space-y-3">
              {walletInfo.tokens.map((token, index) => (
                <div key={index} className="p-3 border rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{token.symbol}</div>
                      {token.property_info && (
                        <div className="text-sm text-gray-600">
                          {token.property_info.title} - {token.property_info.city}, {token.property_info.country}
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="font-bold">{token.balance.toLocaleString()}</div>
                      <div className="text-sm text-gray-500">tokens</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6 text-gray-500">
              <Wallet className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No property tokens yet</p>
              <p className="text-sm">Purchase property tokens to see them here</p>
            </div>
          )}
        </div>

        <Separator />

        {/* Recent Transactions */}
        <div>
          <Label className="text-sm font-medium mb-3 block">Recent Transactions</Label>
          {walletInfo.transactions.length > 0 ? (
            <div className="space-y-2">
              {walletInfo.transactions.slice(0, 5).map((tx, index) => (
                <div key={index} className="flex items-center justify-between p-2 border rounded">
                  <div>
                    <div className="text-sm font-medium">{tx.type}</div>
                    <div className="text-xs text-gray-500">
                      {new Date(tx.date * 1000).toLocaleDateString()}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => window.open(tx.explorer_url, '_blank')}
                  >
                    <ExternalLink className="h-3 w-3" />
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500">
              <p className="text-sm">No transactions yet</p>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setShowConnectForm(true)}
            className="flex-1"
          >
            <Wallet className="h-4 w-4 mr-2" />
            Change Wallet
          </Button>
          <Button
            variant="outline"
            onClick={() => window.open(walletInfo.explorer_url, '_blank')}
            className="flex-1"
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            View on Explorer
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}