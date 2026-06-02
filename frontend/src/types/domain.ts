export type User = {
  id: number;
  telegram_id: number;
  username: string | null;
  is_premium: boolean;
  premium_until: string | null;
  access_active: boolean;
  created_at: string;
};

export type Item = {
  id: number;
  title: string;
  brand: string;
  country: string;
  platform: string;
  category: string;
  size: string;
  image_url: string;
  purchase_price: number;
  shipping_price: number;
  total_price_rub: number;
  avito_price: number;
  expected_profit: number;
  risk_level: string;
  seller_is_suspicious: boolean;
  authenticity_risk: string;
  source_url: string;
};

export type Filters = {
  country?: string;
  platform?: string;
  category?: string;
};

export type TelegramUser = {
  id: number;
  username?: string;
};
