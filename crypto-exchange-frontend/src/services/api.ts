import axios from 'axios';

// Use environment variable or fallback to localhost
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export const getExchanges = async (): Promise<Exchange[]> => {
  const response = await apiClient.get('/exchanges');
  return response.data;
};

export const getCoins = async (): Promise<Coin[]> => {
  const response = await apiClient.get('/coins');
  return response.data;
};

export const getComparison = async (coinId: string, amount?: number): Promise<ComparisonResult> => {
  const url = amount ? `/compare/${coinId}?amount=${amount}` : `/compare/${coinId}`;
  const response = await apiClient.get(url);
  return response.data;
};

export const getExchangeFees = async (exchangeId: number): Promise<any[]> => {
  const response = await apiClient.get(`/compare/fees/${exchangeId}`);
  return response.data;
}; 