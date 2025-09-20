import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface XRPLDebugResult {
  status: string;
  network?: string;
  issuer_wallet_configured?: boolean;
  issuer_address?: string;
  connection_test?: string;
  test_token_creation?: string;
  error?: string;
  message?: string;
  server_info?: any;
}

interface TokenizationResult {
  status: string;
  message: string;
  result?: any;
  error?: string;
}

export default function XRPLDebugPage() {
  const [debugResult, setDebugResult] = useState<XRPLDebugResult | null>(null);
  const [tokenizationResult, setTokenizationResult] = useState<TokenizationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [tokenizationLoading, setTokenizationLoading] = useState(false);

  const checkXRPLConfig = async () => {
    setLoading(true);
    setDebugResult(null);
    
    try {
      const response = await fetch('http://localhost:8000/debug/xrpl-config');
      const data = await response.json();
      setDebugResult(data);
    } catch (error) {
      setDebugResult({
        status: 'error',
        error: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        message: 'Failed to connect to backend'
      });
    } finally {
      setLoading(false);
    }
  };

  const testTokenization = async () => {
    setTokenizationLoading(true);
    setTokenizationResult(null);
    
    try {
      const response = await fetch('http://localhost:8000/debug/test-tokenization', {
        method: 'POST'
      });
      const data = await response.json();
      setTokenizationResult(data);
    } catch (error) {
      setTokenizationResult({
        status: 'error',
        message: 'Network error',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      setTokenizationLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'failed':
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'pending':
      case 'checking':
        return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variant = status === 'success' ? 'default' : 
                   status === 'failed' || status === 'error' ? 'destructive' : 
                   'secondary';
    
    return <Badge variant={variant}>{status}</Badge>;
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">XRPL Configuration Debug</h1>
        <div className="space-x-2">
          <Button 
            onClick={checkXRPLConfig}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Checking...
              </>
            ) : (
              'Check XRPL Config'
            )}
          </Button>
          
          <Button 
            onClick={testTokenization}
            disabled={tokenizationLoading || !debugResult || debugResult.connection_test !== 'success'}
            variant="outline"
          >
            {tokenizationLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Testing...
              </>
            ) : (
              'Test Tokenization'
            )}
          </Button>
        </div>
      </div>

      {debugResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {getStatusIcon(debugResult.status)}
              XRPL Configuration Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="font-semibold">Network:</p>
                <p>{debugResult.network || 'N/A'}</p>
              </div>
              <div>
                <p className="font-semibold">Wallet Configured:</p>
                {getStatusBadge(debugResult.issuer_wallet_configured ? 'success' : 'failed')}
              </div>
              <div>
                <p className="font-semibold">Issuer Address:</p>
                <p className="text-sm font-mono">{debugResult.issuer_address || 'N/A'}</p>
              </div>
              <div>
                <p className="font-semibold">Connection Test:</p>
                {getStatusBadge(debugResult.connection_test || 'pending')}
              </div>
            </div>

            {debugResult.message && (
              <Alert>
                <AlertDescription>{debugResult.message}</AlertDescription>
              </Alert>
            )}

            {debugResult.error && (
              <Alert variant="destructive">
                <AlertDescription>
                  <strong>Error:</strong> {debugResult.error}
                </AlertDescription>
              </Alert>
            )}

            {debugResult.server_info && (
              <details className="mt-4">
                <summary className="cursor-pointer font-semibold">Server Info (Click to expand)</summary>
                <pre className="mt-2 p-3 bg-gray-100 rounded text-sm overflow-auto">
                  {JSON.stringify(debugResult.server_info, null, 2)}
                </pre>
              </details>
            )}
          </CardContent>
        </Card>
      )}

      {tokenizationResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {getStatusIcon(tokenizationResult.status)}
              Tokenization Test Result
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="font-semibold">Status:</span>
                {getStatusBadge(tokenizationResult.status)}
              </div>
              
              <Alert variant={tokenizationResult.status === 'success' ? 'default' : 'destructive'}>
                <AlertDescription>{tokenizationResult.message}</AlertDescription>
              </Alert>

              {tokenizationResult.result && (
                <div>
                  <p className="font-semibold mb-2">Token Creation Result:</p>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="font-medium">Token Symbol:</span>
                      <p>{tokenizationResult.result.token_symbol}</p>
                    </div>
                    <div>
                      <span className="font-medium">Total Supply:</span>
                      <p>{tokenizationResult.result.total_supply}</p>
                    </div>
                    <div>
                      <span className="font-medium">Transaction Hash:</span>
                      <p className="font-mono text-xs break-all">{tokenizationResult.result.tx_hash}</p>
                    </div>
                    <div>
                      <span className="font-medium">Explorer URL:</span>
                      <a 
                        href={tokenizationResult.result.explorer_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline text-xs break-all"
                      >
                        View on Explorer
                      </a>
                    </div>
                  </div>
                </div>
              )}

              {tokenizationResult.error && (
                <Alert variant="destructive">
                  <AlertDescription>
                    <strong>Error:</strong> {tokenizationResult.error}
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Instructions</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="list-decimal list-inside space-y-2">
            <li>First, click "Check XRPL Config" to verify the backend configuration</li>
            <li>If the connection test passes, click "Test Tokenization" to create a test token</li>
            <li>If both tests pass, the property investment should work correctly</li>
            <li>If tests fail, check the backend logs and environment configuration</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}