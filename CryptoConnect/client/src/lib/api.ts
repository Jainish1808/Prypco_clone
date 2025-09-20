// Use environment variable for API base URL with fallback
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.DEV ? '' : (import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'));

// Types
export interface User {
  id: string;
  email: string;
  username: string;
  firstName?: string;
  lastName?: string;
  walletAddress?: string;
  isKYCVerified: boolean;
  userType: 'investor' | 'seller' | 'admin';
  createdAt: string;
}

export interface Property {
  id: string;
  title: string;
  description: string;
  address: string;
  city: string;
  country: string;
  property_type: string;
  total_value: number;
  size_sqm: number;
  total_tokens: number;
  token_price: number;
  tokens_sold: number;
  bedrooms?: number;
  bathrooms?: number;
  parking_spaces?: number;
  year_built?: number;
  monthly_rent?: number;
  annual_yield?: number;
  seller_name: string;
  seller_id?: string;
  status: string;
  images: string[];
  created_at: string;
}

export interface Transaction {
  id: string;
  transaction_type: string;
  status: string;
  user_id: string;
  property_id: string;
  amount: number;
  tokens: number;
  token_price: number;
  xrpl_tx_hash?: string;
  created_at: string;
  completed_at?: string;
}

export interface UserHolding {
  property_id: string;
  property_title: string;
  tokens_owned: number;
  total_investment: number;
  current_value: number;
  ownership_percentage: number;
  monthly_rental_income: number;
}

export interface MarketOrder {
  id: string;
  user_id: string;
  property_id: string;
  property_title: string;
  order_type: 'buy' | 'sell';
  tokens: number;
  price_per_token: number;
  total_amount: number;
  tokens_filled: number;
  tokens_remaining: number;
  status: string;
  created_at: string;
}

// API Client class
class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    // Initialize token from localStorage if available
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token');
    }
  }

  private refreshToken() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token');
    }
  }

  isAuthenticated(): boolean {
    this.refreshToken();
    return !!this.token;
  }

  private getHeaders(): HeadersInit {
    // Always get fresh token from localStorage
    this.refreshToken();
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
      console.log('🔑 Token added to headers:', this.token.substring(0, 30) + '...');
    } else {
      console.log('❌ No token available for request');
    }

    return headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      headers: this.getHeaders(),
      ...options,
    };

    console.log('API Request:', {
      url,
      method: config.method || 'GET',
      headers: config.headers,
      hasBody: !!config.body
    });

    try {
      const response = await fetch(url, config);
      
      console.log('API Response:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        url: response.url
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
        }
        
        console.error('API Error Response:', errorData);
        
        // Handle 401 Unauthorized
        if (response.status === 401) {
          console.log('🚨 401 Unauthorized - clearing token');
          this.clearToken();
          throw new Error('Unauthorized - please login again');
        }
        
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('API Success Response:', data);
      return data;
    } catch (error) {
      console.error('API Request Failed:', error);
      throw error;
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
    console.log('🔑 Token set in API client:', token.substring(0, 30) + '...');
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
    console.log('🗑️ Token cleared from API client');
  }

  // Auth endpoints
  async register(userData: {
    email: string;
    username: string;
    password: string;
    firstName?: string;
    lastName?: string;
    userType: string;
  }): Promise<User> {
    return this.request<User>('/api/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(credentials: {
    username: string;
    password: string;
  }): Promise<{ access_token: string; token_type: string; user: User }> {
    const response = await this.request<{
      access_token: string;
      token_type: string;
      user: User;
    }>('/api/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    this.setToken(response.access_token);
    return response;
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/user');
  }

  async submitKYC(kycData: {
    first_name: string;
    last_name: string;
    phone: string;
    address: string;
    date_of_birth: string;
    document_type: string;
    document_number: string;
  }): Promise<{ message: string; status: string }> {
    return this.request('/api/kyc-submit', {
      method: 'POST',
      body: JSON.stringify(kycData),
    });
  }

  async logout(): Promise<{ message: string }> {
    const response = await this.request<{ message: string }>('/api/logout', {
      method: 'POST',
    });
    this.clearToken();
    return response;
  }

  // Property endpoints
  async getProperties(): Promise<Property[]> {
    return this.request<Property[]>('/api/properties');
  }

  async getProperty(id: string): Promise<Property> {
    return this.request<Property>(`/api/properties/${id}`);
  }

  async investInProperty(propertyId: string, data: {
    property_id: string;
    investment_amount: number;
    tokens_to_purchase: number;
  }): Promise<{
    message: string;
    transaction_id: string;
    tokens_purchased: number;
    amount_invested: number;
    xrpl_tx_hash?: string;
  }> {
    return this.request(`/api/properties/${propertyId}/invest`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Seller endpoints
  async submitProperty(propertyData: {
    title: string;
    description: string;
    address: string;
    city: string;
    country: string;
    property_type: string;
    total_value: number;
    size_sqm: number;
    bedrooms?: number;
    bathrooms?: number;
    parking_spaces?: number;
    year_built?: number;
    monthly_rent?: number;
    images?: string[];
  }): Promise<Property> {
    console.log('API: Submitting property data:', propertyData);
    console.log('API: Current token:', this.token ? 'exists' : 'missing');
    console.log('API: Base URL:', this.baseURL);
    
    try {
      const result = await this.request<Property>('/api/seller/property/submit', {
        method: 'POST',
        body: JSON.stringify(propertyData),
      });
      console.log('API: Property submission successful:', result);
      return result;
    } catch (error) {
      console.error('API: Property submission failed:', error);
      throw error;
    }
  }

  async getSellerProperties(): Promise<Property[]> {
    return this.request<Property[]>('/api/seller/properties');
  }

  async getSellerProperty(id: string): Promise<Property> {
    return this.request<Property>(`/api/seller/property/${id}`);
  }

  async updateSellerProperty(id: string, propertyData: Partial<{
    title: string;
    description: string;
    address: string;
    city: string;
    country: string;
    property_type: string;
    total_value: number;
    size_sqm: number;
    bedrooms?: number;
    bathrooms?: number;
    parking_spaces?: number;
    year_built?: number;
    monthly_rent?: number;
    images?: string[];
  }>): Promise<Property> {
    return this.request<Property>(`/api/seller/property/${id}`, {
      method: 'PUT',
      body: JSON.stringify(propertyData),
    });
  }

  // Investor endpoints
  async getUserHoldings(): Promise<UserHolding[]> {
    return this.request<UserHolding[]>('/api/investor/holdings');
  }

  async getUserTransactions(): Promise<Transaction[]> {
    return this.request<Transaction[]>('/api/investor/transactions');
  }

  async getUserIncomeStatements(): Promise<any[]> {
    return this.request<any[]>('/api/investor/income-statements');
  }

  async getPortfolioSummary(): Promise<{
    total_investment: number;
    total_current_value: number;
    total_monthly_income: number;
    annual_income: number;
    portfolio_yield: number;
    properties_count: number;
    recent_transactions: any[];
  }> {
    return this.request('/api/investor/portfolio-summary');
  }

  // Upload endpoints
  async uploadImages(files: File[]): Promise<{
    uploaded_files: Array<{
      filename: string;
      original_name: string;
      url: string;
    }>;
  }> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await fetch(`${this.baseURL}/api/upload/images`, {
      method: 'POST',
      headers: {
        Authorization: this.token ? `Bearer ${this.token}` : '',
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Market endpoints
  async getMarketOrders(propertyId?: string, orderType?: 'buy' | 'sell'): Promise<MarketOrder[]> {
    const params = new URLSearchParams();
    if (propertyId) params.append('property_id', propertyId);
    if (orderType) params.append('order_type', orderType);
    
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<MarketOrder[]>(`/api/market/orders${query}`);
  }

  async getMyOrders(): Promise<MarketOrder[]> {
    return this.request<MarketOrder[]>('/api/market/orders/my');
  }

  async createMarketOrder(orderData: {
    property_id: string;
    order_type: 'buy' | 'sell';
    tokens: number;
    price_per_token: number;
  }): Promise<{
    message: string;
    order_id: string;
    status: string;
  }> {
    return this.request('/api/market/orders', {
      method: 'POST',
      body: JSON.stringify(orderData),
    });
  }

  async cancelOrder(orderId: string): Promise<{ message: string }> {
    return this.request(`/api/market/orders/${orderId}`, {
      method: 'DELETE',
    });
  }

  // Admin endpoints
  async getPendingProperties(): Promise<Property[]> {
    return this.request<Property[]>('/api/admin/properties/pending');
  }

  async updatePropertyStatus(propertyId: string, data: {
    status?: string;
    admin_notes?: string;
  }): Promise<{ message: string }> {
    return this.request(`/api/admin/properties/${propertyId}/status`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async tokenizeProperty(propertyId: string): Promise<{
    message: string;
    token_symbol: string;
    xrpl_tx_hash: string;
  }> {
    return this.request(`/api/admin/properties/${propertyId}/tokenize`, {
      method: 'POST',
    });
  }

  async distributeRentalIncome(propertyId: string, rentalIncome: number): Promise<{
    message: string;
  }> {
    return this.request(`/api/admin/properties/${propertyId}/distribute-income`, {
      method: 'POST',
      body: JSON.stringify({ rental_income: rentalIncome }),
    });
  }

  async getAdminDashboard(): Promise<{
    properties: {
      pending_review: number;
      approved: number;
      tokenized: number;
      sold_out: number;
      total: number;
    };
    users: {
      total: number;
      verified: number;
      unverified: number;
    };
  }> {
    return this.request('/api/admin/dashboard');
  }

  // Notification methods
  async getUnreadNotifications(): Promise<{ count: number }> {
    return this.request('/api/notifications/unread');
  }
}

// Create and export API client instance
export const api = new ApiClient(API_BASE_URL);
export default api;