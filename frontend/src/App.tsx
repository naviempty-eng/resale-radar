import { ArrowLeft, CheckCircle2, ExternalLink, Loader2, MessageCircle, ShieldAlert, Star } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { enableDemoPremium, getItems, getMe, requestInstruction } from "./api/client";
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

function Paywall({ onActivate, loading }: { onActivate: () => void; loading: boolean }) {
  return (
    <section className="paywall">
      <div>
        <p className="eyebrow">Доступ закрыт</p>
        <h1>Подборки доступны после покупки</h1>
        <p>
          На этом этапе оплата не подключена. Для проверки MVP можно активировать демо-доступ, который ставит
          пользователю флаг <span className="code">is_premium</span>.
        </p>
      </div>
      <button className="primary-button" onClick={onActivate} disabled={loading}>
        {loading ? <Loader2 className="spin" size={18} /> : <CheckCircle2 size={18} />}
        Активировать демо-доступ
      </button>
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
          <Star size={17} />
          Открыть карточку
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
    if (!user?.is_premium || !filtersComplete) {
      setItems([]);
      return;
    }

    setLoading(true);
    getItems(telegramUser, filters)
      .then(setItems)
      .catch((error) => setMessage(error.message))
      .finally(() => setLoading(false));
  }, [filters, filtersComplete, telegramUser, user?.is_premium]);

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

  async function activateDemoPremium() {
    setActionLoading(true);
    try {
      const updated = await enableDemoPremium(telegramUser);
      setUser(updated);
      setMessage("Демо-доступ активирован.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Не удалось активировать доступ.");
    } finally {
      setActionLoading(false);
    }
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

  if (!user?.is_premium) {
    return (
      <main className="app-shell">
        <Paywall onActivate={activateDemoPremium} loading={actionLoading} />
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
          <h1>Выгодные товары</h1>
        </div>
        <div className="premium-pill">
          <CheckCircle2 size={16} />
          Premium
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
