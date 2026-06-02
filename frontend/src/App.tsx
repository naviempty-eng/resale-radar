import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  Copy,
  ExternalLink,
  Gem,
  Loader2,
  MessageCircle,
  ScanSearch,
  ShieldAlert,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { createPaymentRequest, getItems, getMe, requestInstruction } from "./api/client";
import type { Filters, Item, TelegramUser, User } from "./types/domain";

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        ready: () => void;
        expand: () => void;
        initDataUnsafe?: {
          user?: TelegramUser;
        };
      };
    };
  }
}

const COUNTRIES = ["Китай", "Япония"];
const CATEGORIES = ["Обувь", "Верх", "Низ", "Аксессуары"];
const PLANS = [
  { title: "Пробный день", days: "1 день", price: 99, note: "Быстро посмотреть механику" },
  { title: "Неделя", days: "7 дней", price: 399, note: "Проверить категории и спрос" },
  { title: "Месяц", days: "30 дней", price: 990, note: "Оптимально для работы" },
  { title: "Год", days: "365 дней", price: 7990, note: "Лучшая цена за месяц" }
];
const PLATFORMS_BY_COUNTRY: Record<string, string[]> = {
  Китай: ["Goofish"],
  Япония: ["Mercari", "Yahoo Auctions"]
};

function getTelegramUser(): TelegramUser {
  const telegramUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
  if (telegramUser?.id) {
    return telegramUser;
  }

  const params = new URLSearchParams(window.location.search);
  return {
    id: Number(params.get("telegram_id") ?? 1001),
    username: params.get("username") ?? "dev_user"
  };
}

function rub(value: number): string {
  return new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(value);
}

function RiskBadge({ risk }: { risk: string }) {
  const label = risk === "high" ? "Высокий" : risk === "medium" ? "Средний" : "Низкий";
  return <span className={`risk risk-${risk}`}>{label} риск</span>;
}

function Paywall({
  telegramId,
  onBuy,
  onCopyId,
  loading
}: {
  telegramId: number;
  onBuy: () => void;
  onCopyId: () => void;
  loading: boolean;
}) {
  return (
    <section className="paywall">
      <div className="paywall-hero">
        <div className="hero-mark">
          <ScanSearch size={24} />
        </div>
        <p className="eyebrow">Resale Radar</p>
        <h1>Подборки с расчетом маржи</h1>
        <p>Товары из Китая и Японии, фильтр рисковых продавцов, оценка Авито и инструкция по выкупу.</p>
      </div>

      <div className="plans-grid">
        {PLANS.map((plan) => (
          <article className={plan.title === "Месяц" ? "plan-card featured" : "plan-card"} key={plan.title}>
            <div>
              <span>{plan.days}</span>
              <h2>{plan.title}</h2>
              <p>{plan.note}</p>
            </div>
            <strong>{rub(plan.price)}</strong>
          </article>
        ))}
      </div>

      <div className="buyer-id">
        <div>
          <span>Твой Telegram ID</span>
          <strong>{telegramId}</strong>
        </div>
        <button className="icon-button" onClick={onCopyId} aria-label="Скопировать Telegram ID">
          <Copy size={18} />
        </button>
      </div>

      <button className="primary-button" onClick={onBuy} disabled={loading}>
        {loading ? <Loader2 className="spin" size={18} /> : <MessageCircle size={18} />}
        Купить доступ
      </button>
      <p className="pay-note">После оплаты отправь ID и тариф в поддержку. Доступ включается вручную.</p>
    </section>
  );
}

function StepOptions({
  title,
  options,
  value,
  onChange
}: {
  title: string;
  options: string[];
  value?: string;
  onChange: (value: string) => void;
}) {
  return (
    <section className="filter-block">
      <h2>{title}</h2>
      <div className="segmented">
        {options.map((option) => (
          <button
            key={option}
            className={value === option ? "active" : ""}
            type="button"
            onClick={() => onChange(option)}
          >
            {option}
          </button>
        ))}
      </div>
    </section>
  );
}

function ItemCard({ item, onOpen }: { item: Item; onOpen: (item: Item) => void }) {
  return (
    <article className="item-card">
      <button className="image-button" onClick={() => onOpen(item)} aria-label={`Открыть ${item.title}`}>
        <img src={item.image_url} alt={item.title} loading="lazy" />
        <span>{item.platform}</span>
      </button>
      <div className="item-body">
        <div className="item-title-row">
          <div>
            <p className="brand">{item.brand}</p>
            <h3>{item.title}</h3>
          </div>
          <RiskBadge risk={item.risk_level} />
        </div>
        <div className="meta-grid">
          <span>{item.country}</span>
          <span>{item.platform}</span>
          <span>{item.category}</span>
          <span>{item.size}</span>
        </div>
        <div className="profit-row">
          <div>
            <span>Итого</span>
            <strong>{rub(item.total_price_rub)}</strong>
          </div>
          <div>
            <span>Авито</span>
            <strong>{rub(item.avito_price)}</strong>
          </div>
          <div className="profit">
            <span>Прибыль</span>
            <strong>{rub(item.expected_profit)}</strong>
          </div>
        </div>
        <button className="secondary-button" onClick={() => onOpen(item)}>
          <Gem size={17} />
          Смотреть расчет
        </button>
      </div>
    </article>
  );
}

function ItemDetails({
  item,
  onBack,
  onInstruction,
  instructionLoading
}: {
  item: Item;
  onBack: () => void;
  onInstruction: () => void;
  instructionLoading: boolean;
}) {
  return (
    <main className="details">
      <button className="icon-text-button" onClick={onBack}>
        <ArrowLeft size={18} />
        Назад
      </button>
      <img className="details-image" src={item.image_url} alt={item.title} />
      <div className="details-head">
        <div>
          <p className="brand">{item.brand}</p>
          <h1>{item.title}</h1>
        </div>
        <RiskBadge risk={item.risk_level} />
      </div>
      <div className="details-grid">
        <Info label="Страна" value={item.country} />
        <Info label="Площадка" value={item.platform} />
        <Info label="Категория" value={item.category} />
        <Info label="Размер" value={item.size} />
        <Info label="Цена покупки" value={rub(item.purchase_price)} />
        <Info label="Доставка" value={rub(item.shipping_price)} />
        <Info label="Итоговая цена" value={rub(item.total_price_rub)} />
        <Info label="Средняя Авито" value={rub(item.avito_price)} />
        <Info label="Прибыль" value={rub(item.expected_profit)} highlight />
        <Info label="Риск оригинальности" value={item.authenticity_risk} />
      </div>
      <div className="details-actions">
        <a className="secondary-button" href={item.source_url} target="_blank" rel="noreferrer">
          <ExternalLink size={17} />
          Ссылка на товар
        </a>
        <button className="primary-button" onClick={onInstruction} disabled={instructionLoading}>
          {instructionLoading ? <Loader2 className="spin" size={18} /> : <MessageCircle size={18} />}
          Получить инструкцию
        </button>
      </div>
    </main>
  );
}

function Info({ label, value, highlight = false }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className={highlight ? "info highlight" : "info"}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default function App() {
  const [telegramUser] = useState<TelegramUser>(() => getTelegramUser());
  const [user, setUser] = useState<User | null>(null);
  const [filters, setFilters] = useState<Filters>({});
  const [items, setItems] = useState<Item[]>([]);
  const [selectedItem, setSelectedItem] = useState<Item | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const platforms = useMemo(() => (filters.country ? PLATFORMS_BY_COUNTRY[filters.country] : []), [filters.country]);
  const filtersComplete = Boolean(filters.country && filters.platform && filters.category);

  useEffect(() => {
    window.Telegram?.WebApp?.ready();
    window.Telegram?.WebApp?.expand();
    getMe(telegramUser)
      .then(setUser)
      .finally(() => setLoading(false));
  }, [telegramUser]);

  useEffect(() => {
    if (!user?.access_active || !filtersComplete) {
      setItems([]);
      return;
    }

    setLoading(true);
    getItems(telegramUser, filters)
      .then(setItems)
      .catch((error) => setMessage(error.message))
      .finally(() => setLoading(false));
  }, [filters, filtersComplete, telegramUser, user?.access_active]);

  function updateCountry(country: string) {
    setSelectedItem(null);
    setFilters({ country, platform: undefined, category: undefined });
  }

  function updatePlatform(platform: string) {
    setSelectedItem(null);
    setFilters((current) => ({ ...current, platform, category: undefined }));
  }

  function updateCategory(category: string) {
    setSelectedItem(null);
    setFilters((current) => ({ ...current, category }));
  }

  async function startManualPurchase() {
    setActionLoading(true);
    try {
      const updated = await createPaymentRequest(telegramUser);
      setUser(updated);
      setMessage("Напиши боту /buy или отправь свой Telegram ID в поддержку.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Не удалось создать заявку.");
    } finally {
      setActionLoading(false);
    }
  }

  async function copyTelegramId() {
    await navigator.clipboard?.writeText(String(telegramUser.id));
    setMessage("Telegram ID скопирован.");
  }

  async function sendInstruction() {
    if (!selectedItem) return;
    setActionLoading(true);
    try {
      const result = await requestInstruction(telegramUser, selectedItem.id);
      setMessage(result.sent ? "Инструкция отправлена в Telegram." : "Инструкция создана, но бот не смог отправить сообщение.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Не удалось получить инструкцию.");
    } finally {
      setActionLoading(false);
    }
  }

  if (loading && !user) {
    return (
      <main className="app-shell center">
        <Loader2 className="spin" size={28} />
      </main>
    );
  }

  if (!user?.access_active) {
    return (
      <main className="app-shell">
        <Paywall telegramId={telegramUser.id} onBuy={startManualPurchase} onCopyId={copyTelegramId} loading={actionLoading} />
        {message && <div className="toast">{message}</div>}
      </main>
    );
  }

  if (selectedItem) {
    return (
      <main className="app-shell">
        <ItemDetails
          item={selectedItem}
          onBack={() => setSelectedItem(null)}
          onInstruction={sendInstruction}
          instructionLoading={actionLoading}
        />
        {message && <div className="toast">{message}</div>}
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Resale Radar</p>
          <h1>Каталог сделок</h1>
          {user.premium_until && (
            <p className="access-line">
              <CalendarDays size={15} />
              Доступ до {new Date(user.premium_until).toLocaleDateString("ru-RU")}
            </p>
          )}
        </div>
        <div className="premium-pill">
          <CheckCircle2 size={16} />
          Active
        </div>
      </header>

      <StepOptions title="1. Страна" options={COUNTRIES} value={filters.country} onChange={updateCountry} />
      {filters.country && <StepOptions title="2. Площадка" options={platforms} value={filters.platform} onChange={updatePlatform} />}
      {filters.platform && <StepOptions title="3. Категория" options={CATEGORIES} value={filters.category} onChange={updateCategory} />}

      <section className="items-section">
        <div className="section-head">
          <h2>4. Товары</h2>
          {filtersComplete && <span>{loading ? "Поиск" : `${items.length} вариантов`}</span>}
        </div>

        {!filtersComplete && (
          <div className="empty-state">
            <ShieldAlert size={22} />
            Выбери страну, площадку и категорию.
          </div>
        )}

        {filtersComplete && loading && (
          <div className="empty-state">
            <Loader2 className="spin" size={22} />
            Загружаем подборку.
          </div>
        )}

        {filtersComplete && !loading && items.length === 0 && <div className="empty-state">Под эти фильтры пока нет товаров.</div>}

        <div className="item-list">
          {items.map((item) => (
            <ItemCard key={item.id} item={item} onOpen={setSelectedItem} />
          ))}
        </div>
      </section>

      {message && <div className="toast">{message}</div>}
    </main>
  );
}
