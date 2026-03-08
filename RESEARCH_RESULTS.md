# TheSoul Research Results — 2026-03-07

## 🔴 R1: Channel Efficiency — СИЛЬНЫЙ ИНСАЙТ ✅

**Находка:** 36× разрыв в revenue/video между top-10 и bottom-50% каналов YouTube.

Ключевые паттерны top-каналов:
- **Production share** сильно коррелирует с revenue/video (Spearman r=0.43, p=0.002)
- **Evergreen rate** тоже коррелирует (r=0.34, p=0.018)
- Top-каналы: ниже retention (37% vs 71%) — парадокс! Длинные видео = ниже % viewed, но выше CPM
- Top-каналы: 4× длиннее контент (1863s vs 465s)
- Engagement rate у top-каналов НИЖЕ (1.27 vs 1.46) — подтверждает R2

**channel_10846** — звезда: 100% Production, 65.9% evergreen rate, $9.37/video. Модель для копирования.

**Snapchat:** Gini=0.73, extreme concentration. channel_621 = 46.4% всей выручки Snapchat ($131K из $283K). Top-5 = 72.5%. Это и risk, и opportunity.

**Годится как инсайт:** ✅ Да. "Your best channels share 3 traits: high production share, long-form, low engagement rate. Engagement is a misleading KPI."

---

## 🔴 R2: Engagement ≠ Revenue — KILLER INSIGHT ✅✅✅

**Находка:** Engagement rate ОТРИЦАТЕЛЬНО коррелирует с revenue (r = -0.24). Это не noise — это сигнал.

Ключевые цифры:
| Metric | Корреляция с revenue | Полезность |
|---|---|---|
| **Engagement rate** | **r = -0.24** ⚠️ | ANTI-predictor |
| **Avg % viewed** | **r = -0.42** ⚠️ | ANTI-predictor |
| **Watch time (min)** | **r = +0.72** ✅ | ЛУЧШИЙ предиктор |
| **Ad impressions** | **r = +0.93** ✅ | Тривиальный (=revenue proxy) |
| **Likes** | r = +0.45 | Средний |
| **Total views** | r = +0.55 | Средний |

**Confusion matrix (YouTube):** из видео в top-25% по engagement, только 13.4% попадают в top-25% по revenue. Хуже рандома (25%)! Engagement не просто бесполезен — он вредит.

**Почему:** Shorts имеют 105% retention и высокий engagement — но CPM $0.06. Production: 20% retention, низкий engagement — но CPM $1.94. Команды, оптимизирующие engagement, невольно сдвигаются к Shorts.

**Рекомендация:** Заменить engagement rate на **watch_time_minutes** как primary KPI. Watch time r=+0.72 — лучший одиночный предиктор revenue на YouTube.

**Годится как инсайт:** ✅✅ Однозначно. Это самый "неочевидный" и actionable из всех. "Your engagement KPI is actively hurting your revenue."

---

## 🔴 R3: Content Velocity — ХОРОШИЙ ИНСАЙТ ✅

**Находка:** Негативная корреляция между частотой публикации и revenue/video (r = -0.46, p < 0.0001).

| Частота | Channels | Avg $/video | Format Mix |
|---|---|---|---|
| 1-3/wk | 8 | $4.82 | 71% Production |
| **3-7/wk** | **48** | **$101.56** | **65% Story, 25% Prod** |
| 1-2/day | 11 | $3.56 | 54% Shorts |
| >2/day | 17 | $0.87 | 74% Shorts |

**Нюанс:** Пик $101.56 у "3-7/wk" — но это Snapchat Stories (65% mix). Stories = high CPM на Snap. Для чистого YouTube: каналы 1-3/wk (Production-heavy) vs >2/day (Shorts-heavy) → 5.5× gap.

**Реальный инсайт:** Каналы, публикующие >2 видео в день, почти исключительно Shorts. Гонка за volume = гонка за Shorts = убивает revenue/video. Модель "меньше, но длиннее" работает лучше.

**Годится как инсайт:** ✅ Да, но пересекается с R1 и Insight 1. Лучше как supporting evidence к "Production > Shorts" нарративу.

---

## 🟡 Бонусные находки

### 2.4 Watch Time Efficiency
Snapchat: $0.0032/min — в **32× дороже** чем YouTube ($0.0001/min). Каждая минута внимания на Snapchat в 32 раза ценнее. Интересно, но скорее следствие CPM structure.

### 2.5 First 7 Days — СЮРПРИЗ ⭐
**ROC AUC = 0.937** для предсказания evergreen по доле views в первые 7 дней. Evergreen видео набирают 33% views за 7 дней, обычные — 97%.

**Рекомендация:** Можно строить early-warning систему: если через 7 дней видео набрало <50% от пиковых daily views → вероятный evergreen → активнее промоутить. Отличный add-on к Insight 2.

### 2.6 Day of Week
Незначимый разброс ($20-34/video по дням). Среда и суббота чуть выше, четверг/пятница ниже. Нет actionable инсайта.

### 2.7 Dislike Ratio
r = -0.05 с revenue — никакого эффекта. Controversy не помогает и не мешает.

### 2.8 Ad Fill Rate
Production: 1.17 ads/view (больше 1 рекламы на просмотр!). Shorts: 0.0 (почти без рекламы). Это объясняет 35× CPM gap — mid-roll ads.

---

## Итого: что добавить к решению

### Новые инсайты для notebook (ранг полезности):

1. **⭐⭐⭐ "Engagement Anti-Predicts Revenue"** (R2) — killer insight, самый неочевидный
   - Engagement r = -0.24, avg_viewed r = -0.42
   - Watch time r = +0.72 — правильный KPI
   - Confusion matrix: 13.4% overlap vs 25% random
   
2. **⭐⭐ "Snapchat Revenue Concentration"** (R1 + review) — risk management
   - channel_621 = 46.4%, Gini = 0.73
   - Top-5 = 72.5%, остальные 27 каналов делят 27.5%
   
3. **⭐⭐ "7-Day Early Evergreen Detection"** (R2.5) — actionable add-on
   - AUC 0.937, порог 50% views за 7 дней
   - Добавить к Insight 2 как practical tool

4. **⭐ "Velocity Kills Revenue"** (R3) — supporting evidence
   - >2/day = $0.87/video vs 1-3/wk = $4.82
   - Но пересекается с Insight 1, лучше интегрировать

### Phase 2 — Дополнительные находки

**Duration Sweet Spot (granular):**
- 8-10 min: efficiency 11.7× (0.7% supply → 8.2% revenue, $38.28/video)
- 10-15 min: efficiency 10.3× (2% supply → 20.5% revenue, $32.38/video)
- 15-30 min: резко падает до 1.7× ($5.29-$11.11/video)
- Snapchat 10m+: $1,270/video (n=46), в 8× больше 2-5m stories
- **Action:** Целить в 8-15 min (не просто ">8 min" — 15-30 уже теряет)

**Shares > Likes (YouTube):**
- like_rate: r=-0.23 с revenue (анти-предиктор!)
- share_rate: r=+0.24 (положительный!)
- comment_rate: r=+0.24
- Даже внутри Shorts: share_rate r=+0.29 vs like_rate r=-0.17
- **Action:** Shares = лучший engagement proxy после watch time

**Cross-platform delayed posting:**
- Facebook↔Snapchat delay median: 73 дня
- YouTube↔Snapchat: 52 дня
- Facebook↔YouTube: 22 дня
- Best combo: Facebook+Snapchat ($183/video avg)

**Watch Time → Universal Best KPI:**
- YouTube: watch_time r=+0.72 vs views r=+0.54
- Facebook: watch_time r=+0.55 vs views r=+0.49
- Snapchat: watch_time r=+0.86 vs views r=+0.83
- На ВСЕХ платформах watch time лучше предсказывает revenue

**Channel Archetypes:**
- Snapchat Native: $149/video (top)
- Mixed format: $5.21/video
- Production Studio: $4.18/video
- Shorts Machine: $1.92/video (bottom)

**7-day Evergreen Predictor (подтверждено):**
- AUC 0.937
- Evergreen: 33% views за 7 дней, Normal: 97%
- Видео с >30% views после 30 дней: $28.68/video vs $2.68 overall (10.7×)

### Структура обновлённого решения:
1. **Insight 1:** Short-Form Monetization Trap (существующий) + duration sweet spot 8-15 min
2. **Insight 2:** Evergreen Compound Returns (существующий) + 7-day predictor (AUC 0.937)
3. **Insight 3:** Cross-Platform Synergy (существующий) + delayed posting + best combos
4. **Insight 4: NEW — "Engagement is Anti-Revenue"** ← killer insight (engagement r=-0.24, watch time r=+0.72, shares>likes)
5. **Insight 5: NEW — "Revenue Concentration Risk"** ← Snapchat channel_621 story + channel archetypes
