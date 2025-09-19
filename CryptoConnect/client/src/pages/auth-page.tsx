import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { Redirect } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Building, TrendingUp, Users, Shield } from "lucide-react";

export default function AuthPage() {
  const { user, loginMutation, registerMutation } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  
  // Form state
  const [loginData, setLoginData] = useState({ username: "", password: "" });
  const [registerData, setRegisterData] = useState({
    username: "",
    email: "",
    password: "",
    firstName: "",
    lastName: "",
    userType: "investor" as "investor" | "seller",
    isKYCVerified: false
  });

  // Redirect if already logged in
  if (user) {
    return <Redirect to="/" />;
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    loginMutation.mutate(loginData);
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    registerMutation.mutate(registerData);
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left side - Forms */}
      <div className="flex-1 flex items-center justify-center p-8">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                <Building className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <CardTitle className="text-2xl font-bold">RealEstate Token</CardTitle>
                <p className="text-sm text-muted-foreground">Investment Platform</p>
              </div>
            </div>
            
            {/* Toggle Buttons */}
            <div className="flex bg-muted rounded-lg p-1 mb-6">
              <button
                onClick={() => setIsLogin(true)}
                className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
                  isLogin 
                    ? "bg-card text-foreground shadow-sm" 
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => setIsLogin(false)}
                className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
                  !isLogin 
                    ? "bg-card text-foreground shadow-sm" 
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Sign Up
              </button>
            </div>
          </CardHeader>

          <CardContent>
            {isLogin ? (
              /* Login Form */
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <Label htmlFor="login-username">Username or Email</Label>
                  <Input
                    id="login-username"
                    type="text"
                    value={loginData.username}
                    onChange={(e) => setLoginData(prev => ({ ...prev, username: e.target.value }))}
                    placeholder="Enter your username or email"
                    required
                    data-testid="input-login-username"
                  />
                </div>
                
                <div>
                  <Label htmlFor="login-password">Password</Label>
                  <Input
                    id="login-password"
                    type="password"
                    value={loginData.password}
                    onChange={(e) => setLoginData(prev => ({ ...prev, password: e.target.value }))}
                    placeholder="Enter your password"
                    required
                    data-testid="input-login-password"
                  />
                </div>

                <Button 
                  type="submit" 
                  className="w-full"
                  disabled={loginMutation.isPending}
                  data-testid="button-login"
                >
                  {loginMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Signing In...
                    </>
                  ) : (
                    "Sign In"
                  )}
                </Button>
              </form>
            ) : (
              /* Registration Form */
              <form onSubmit={handleRegister} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="register-firstName">First Name</Label>
                    <Input
                      id="register-firstName"
                      type="text"
                      value={registerData.firstName}
                      onChange={(e) => setRegisterData(prev => ({ ...prev, firstName: e.target.value }))}
                      placeholder="John"
                      required
                      data-testid="input-register-firstname"
                    />
                  </div>
                  <div>
                    <Label htmlFor="register-lastName">Last Name</Label>
                    <Input
                      id="register-lastName"
                      type="text"
                      value={registerData.lastName}
                      onChange={(e) => setRegisterData(prev => ({ ...prev, lastName: e.target.value }))}
                      placeholder="Smith"
                      required
                      data-testid="input-register-lastname"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="register-email">Email</Label>
                  <Input
                    id="register-email"
                    type="email"
                    value={registerData.email}
                    onChange={(e) => setRegisterData(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="john@example.com"
                    required
                    data-testid="input-register-email"
                  />
                </div>

                <div>
                  <Label htmlFor="register-username">Username</Label>
                  <Input
                    id="register-username"
                    type="text"
                    value={registerData.username}
                    onChange={(e) => setRegisterData(prev => ({ ...prev, username: e.target.value }))}
                    placeholder="johnsmith"
                    required
                    data-testid="input-register-username"
                  />
                </div>

                <div>
                  <Label htmlFor="register-password">Password</Label>
                  <Input
                    id="register-password"
                    type="password"
                    value={registerData.password}
                    onChange={(e) => setRegisterData(prev => ({ ...prev, password: e.target.value }))}
                    placeholder="Create a secure password"
                    required
                    data-testid="input-register-password"
                  />
                </div>

                <div>
                  <Label htmlFor="register-userType">Account Type</Label>
                  <Select 
                    value={registerData.userType} 
                    onValueChange={(value: "investor" | "seller") => 
                      setRegisterData(prev => ({ ...prev, userType: value }))
                    }
                  >
                    <SelectTrigger data-testid="select-register-usertype">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="investor">Investor - Buy property tokens</SelectItem>
                      <SelectItem value="seller">Seller - List properties</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button 
                  type="submit" 
                  className="w-full"
                  disabled={registerMutation.isPending}
                  data-testid="button-register"
                >
                  {registerMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating Account...
                    </>
                  ) : (
                    "Create Account"
                  )}
                </Button>
              </form>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Right side - Hero Section */}
      <div className="flex-1 bg-gradient-to-br from-primary to-secondary text-primary-foreground p-8 flex items-center justify-center">
        <div className="max-w-lg text-center space-y-6">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold">Tokenized Real Estate Investment</h1>
            <p className="text-xl opacity-90">
              Invest in fractional real estate ownership through blockchain technology
            </p>
          </div>

          <div className="grid grid-cols-2 gap-6 mt-8">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mx-auto">
                <TrendingUp className="h-6 w-6" />
              </div>
              <h3 className="font-semibold">High Yields</h3>
              <p className="text-sm opacity-80">Earn 7-12% annual returns</p>
            </div>
            
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mx-auto">
                <Users className="h-6 w-6" />
              </div>
              <h3 className="font-semibold">Low Minimums</h3>
              <p className="text-sm opacity-80">Start investing with just $100</p>
            </div>
            
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mx-auto">
                <Shield className="h-6 w-6" />
              </div>
              <h3 className="font-semibold">Secure</h3>
              <p className="text-sm opacity-80">Blockchain-backed ownership</p>
            </div>
            
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mx-auto">
                <Building className="h-6 w-6" />
              </div>
              <h3 className="font-semibold">Diversified</h3>
              <p className="text-sm opacity-80">Multiple property types</p>
            </div>
          </div>

          <div className="pt-6">
            <p className="text-sm opacity-80">
              Join thousands of investors already building their real estate portfolios
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
