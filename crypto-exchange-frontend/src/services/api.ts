import axios from 'axios';

// Inside Docker, the frontend container uses VITE_API_URL=http://api:8000
// But browser requests from user's machine need to use localhost
// We need to handle this difference for development mode
const isDevelopment = import.meta.env.MODE === 'development';
const browserBaseUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : import.meta.env.VITE_API_URL;

// Use proper base URL depending on context
const BASE_URL = browserBaseUrl || 'http://localhost:8000';

console.log('API base URL:', BASE_URL);

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
});

// Add request/response interceptors for debugging
apiClient.interceptors.request.use(request => {
  console.log('API Request:', request.method?.toUpperCase(), request.url);
  return request;
});

apiClient.interceptors.response.use(
  response => {
    console.log('API Response:', response.status, response.config.url);
    
    // Check if response is HTML instead of JSON
    if (typeof response.data === 'string' && response.data.includes('<!doctype html>')) {
      console.error('Received HTML response instead of JSON:', response.data.substring(0, 100) + '...');
      return Promise.reject(new Error('Received HTML response instead of JSON data'));
    }
    
    return response;
  },
  error => {
    console.error('API Error:', error.response?.status, error.response?.data, error.config?.url);
    return Promise.reject(error);
  }
);

export interface Exchange {
  id: number;
  name: string;
  website: string | null;
  api_url: string | null;
  logo_url: string | null;
  has_trading_fees: boolean;
  has_withdrawal_fees: boolean;
  created_at: string;
  updated_at: string;
}

export interface Coin {
  id: number;
  coingecko_id: string;
  symbol: string;
  name: string;
  logo_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExchangePrice {
  exchange_name: string;
  price_usd: number;
  volume_24h: number | null;
  bid_price: number | null;
  ask_price: number | null;
  trading_fee: number | null;
  withdrawal_fee: number | null;
  last_updated: string;
  spread: number | null;
}

export interface ComparisonResult {
  coin: string;
  exchanges: ExchangePrice[];
  best_price: ExchangePrice;
  best_for_large_orders: ExchangePrice | null;
}

export interface CoinGeckoListItem {
  id: string;
  symbol: string;
  name: string;
  has_market_data: boolean;
  current_price?: number;
  market_cap?: number;
  image?: string;
  price_change_24h?: number;
}

export const getExchanges = async (): Promise<Exchange[]> => {
  try {
    const response = await apiClient.get('/exchanges/');
    return response.data;
  } catch (error) {
    console.error('Failed to get exchanges:', error);
    return [];
  }
};

export const getCoins = async (): Promise<Coin[]> => {
  try {
    console.log('Calling getCoins API');
    const response = await apiClient.get('/coins/');
    console.log('Coins API response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get coins:', error);
    return [];
  }
};

export const getComparison = async (coinId: string, amount?: number): Promise<any> => {
  try {
    console.log(`Fetching comparison data for ${coinId}...`);
    const url = amount ? `/compare/${coinId}?amount=${amount}` : `/compare/${coinId}`;
    const response = await apiClient.get(url);
    
    // Additional validation
    if (!response.data || typeof response.data !== 'object') {
      console.error('Invalid comparison data format:', response.data);
      return null;
    }
    
    return response.data;
  } catch (error) {
    console.error('Failed to get comparison:', error);
    return null;
  }
};

export const createCoin = async (coin: { coingecko_id: string, symbol: string, name: string, logo_url?: string }): Promise<Coin> => {
  try {
    const response = await apiClient.post('/coins/', coin);
    return response.data;
  } catch (error) {
    console.error('Failed to create coin:', error);
    throw error;
  }
};

export const deleteCoin = async (coinId: number): Promise<Coin> => {
  try {
    const response = await apiClient.delete(`/coins/${coinId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to delete coin:', error);
    throw error;
  }
};

export const getExchangeFees = async (exchangeId: number): Promise<any[]> => {
  try {
    const response = await apiClient.get(`/compare/fees/${exchangeId}/`);
    return response.data;
  } catch (error) {
    console.error('Failed to get exchange fees:', error);
    return [];
  }
};

export const searchAvailableCoins = async (query: string): Promise<CoinGeckoListItem[]> => {
  try {
    if (!query || query.length < 2) return [];
    
    const response = await apiClient.get('/coins/search', {
      params: { query }
    });
    return response.data || [];
  } catch (error) {
    console.error('Failed to search coins:', error);
    return [];
  }
}; 