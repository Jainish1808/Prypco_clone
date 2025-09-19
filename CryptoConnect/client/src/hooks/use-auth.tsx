import { createContext, ReactNode, useContext } from "react";
import {
  useQuery,
  useMutation,
  UseMutationResult,
} from "@tanstack/react-query";
import { api, User } from "../lib/api";
import { queryClient } from "../lib/queryClient";
import { useToast } from "@/hooks/use-toast";

type AuthContextType = {
  user: User | null;
  isLoading: boolean;
  error: Error | null;
  loginMutation: UseMutationResult<{ access_token: string; token_type: string; user: User }, Error, LoginData>;
  logoutMutation: UseMutationResult<{ message: string }, Error, void>;
  registerMutation: UseMutationResult<User, Error, RegisterData>;
  kycSubmitMutation: UseMutationResult<{ message: string; status: string }, Error, KYCData>;
};

type LoginData = {
  username: string;
  password: string;
};

type RegisterData = {
  email: string;
  username: string;
  password: string;
  firstName?: string;
  lastName?: string;
  userType: string;
};

type KYCData = {
  first_name: string;
  last_name: string;
  phone: string;
  address: string;
  date_of_birth: string;
  document_type: string;
  document_number: string;
};

export const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { toast } = useToast();
  const {
    data: user,
    error,
    isLoading,
  } = useQuery<User | null, Error>({
    queryKey: ["/api/user"],
    queryFn: async () => {
      try {
        // Only make request if we have a token
        if (!api.isAuthenticated()) {
          console.log('🚫 No token available, skipping user fetch');
          return null;
        }
        return await api.getCurrentUser();
      } catch (error) {
        console.error('Auth error:', error);
        // If unauthorized, return null instead of throwing
        if (error instanceof Error && (error.message.includes('401') || error.message.includes('Unauthorized'))) {
          console.log('🚫 401 error, clearing token and returning null');
          api.clearToken();
          return null;
        }
        throw error;
      }
    },
    retry: false,
    // Only run if we have a token
    enabled: typeof window !== 'undefined' && !!localStorage.getItem('token'),
  });

  const loginMutation = useMutation({
    mutationFn: async (credentials: LoginData) => {
      return await api.login(credentials);
    },
    onSuccess: (data) => {
      queryClient.setQueryData(["/api/user"], data.user);
      toast({
        title: "Login successful",
        description: `Welcome back, ${data.user.firstName || data.user.username}!`,
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Login failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const registerMutation = useMutation({
    mutationFn: async (credentials: RegisterData) => {
      return await api.register(credentials);
    },
    onSuccess: (user: User) => {
      queryClient.setQueryData(["/api/user"], user);
      toast({
        title: "Registration successful",
        description: `Welcome to CryptoConnect, ${user.firstName || user.username}!`,
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Registration failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const logoutMutation = useMutation({
    mutationFn: async () => {
      return await api.logout();
    },
    onSuccess: () => {
      queryClient.setQueryData(["/api/user"], null);
      toast({
        title: "Logged out",
        description: "You have been successfully logged out.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Logout failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const kycSubmitMutation = useMutation({
    mutationFn: async (kycData: KYCData) => {
      return await api.submitKYC(kycData);
    },
    onSuccess: () => {
      // Refetch user data to get updated KYC status
      queryClient.invalidateQueries({ queryKey: ["/api/user"] });
      toast({
        title: "KYC Verification Complete",
        description: "Your identity has been verified successfully.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "KYC Submission Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  return (
    <AuthContext.Provider
      value={{
        user: user ?? null,
        isLoading,
        error,
        loginMutation,
        logoutMutation,
        registerMutation,
        kycSubmitMutation,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
