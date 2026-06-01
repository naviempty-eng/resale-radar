import type { Filters, Item, TelegramUser, User } from "../types/domain";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

function headers(user: TelegramUser): HeadersInit {
  return {
    "Content-Type": "application/json",
    "X-Telegram-Id": String(user.id),
    "X-Telegram-Username": user.username ?? ""
  };
}

async function request<T>(path: string, user: TelegramUser, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...headers(user),
      ...(options.headers ?? {})
    }
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function getMe(user: TelegramUser): Promise<User> {
  return request<User>("/api/users/me", user);
}

export function enableDemoPremium(user: TelegramUser): Promise<User> {
  return request<User>("/api/users/me/premium-demo", user, { method: "POST" });
}

export async function getItems(user: TelegramUser, filters: Filters): Promise<Item[]> {
  const params = new URLSearchParams();
  if (filters.country) params.set("country", filters.country);
  if (filters.platform) params.set("platform", filters.platform);
  if (filters.category) params.set("category", filters.category);

  const data = await request<{ items: Item[] }>(`/api/items?${params.toString()}`, user);
  return data.items;
}

export function requestInstruction(user: TelegramUser, itemId: number): Promise<{ sent: boolean; content: string }> {
  return request(`/api/items/${itemId}/instruction`, user, { method: "POST" });
}
