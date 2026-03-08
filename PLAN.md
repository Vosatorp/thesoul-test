# TheSoul Test — План работ

## Часть 1: Рефакторинг и оформление

### 1.1 Структура решения
- [ ] Разбить монолитный notebook на логические секции с чистыми markdown-заголовками
- [ ] Убрать debug/exploration cells, оставить только финальный анализ
- [ ] Добавить executive summary в начало (3 bullet points, 30 секунд на чтение)
- [ ] Каждый инсайт: проблема → данные → вывод → рекомендация (единый шаблон)

### 1.2 Визуализации
- [ ] Унифицировать стиль графиков (единая palette, font size, figure size)
- [ ] Добавить аннотации на ключевые точки (35× gap, 8-min threshold)
- [ ] Revenue waterfall chart — общая картина "откуда деньги"
- [ ] Heatmap: channel × metric для Snapchat concentration (новый инсайт)

### 1.3 Добавить 4-й инсайт
- [ ] **Snapchat Revenue Concentration** — channel_621 story (из deep_insights #1)
- [ ] Визуализация: Lorenz curve / Pareto chart концентрации revenue по каналам
- [ ] Рекомендация: risk diversification + best practice extraction из top-5 каналов

### 1.4 Русская презентация
- [ ] Перевести presentation.md на русский
- [ ] Адаптировать под формат слайдов (Marp/reveal.js → PDF)
- [ ] 8-10 слайдов: титул, подход, 4 инсайта (по 1-2 слайда), next steps, appendix
- [ ] Каждый слайд: один график + 2-3 bullet points, минимум текста

### 1.5 Code quality
- [ ] requirements.txt → pyproject.toml с pinned versions
- [ ] Type hints в utility functions
- [ ] Reproducibility: random seeds, explicit data paths

---

## Часть 2: Ресёрч — куда ещё копать

### 🔴 Высокий приоритет (высокая вероятность сильного инсайта)

#### 2.1 Channel-Level Efficiency Analysis
**Гипотеза:** Разные каналы имеют радикально разную "эффективность" (revenue per video, evergreen rate). Паттерны top-каналов можно масштабировать.
- Revenue per video по каналам → найти outliers
- Что отличает top-10 каналов от bottom-50%? (формат, длительность, частота публикации)
- Channel-level recommendation: оптимальный mix форматов для каждого канала
- **Данные:** dataset_1 (channel_id, video_type, revenue_proxy, duration)

#### 2.2 Engagement → Revenue Disconnect
**Гипотеза:** Engagement rate (likes/comments/shares) — плохой предиктор revenue. Команды оптимизируют не тот KPI.
- Корреляция engagement_rate vs revenue_proxy по форматам
- Какой metric лучше предсказывает revenue? (watch_time, avg_view_duration, ad_impressions)
- Построить "правильный" KPI-прокси
- **Данные:** dataset_1 (engagement_rate, likes, comments, shares, revenue_proxy, watch_time)

#### 2.3 Content Velocity vs Quality Tradeoff
**Гипотеза:** Каналы с высокой частотой публикации имеют ниже revenue/video. "Меньше, но лучше" выигрывает.
- Частота публикации по каналам (publish_date группировка)
- Корреляция: publish frequency vs avg revenue/video vs evergreen rate
- Оптимальная каденция публикации по форматам
- **Данные:** dataset_1 (channel_id, publish_date, revenue_proxy)

### 🟡 Средний приоритет (интересно, но может не дать wow-результат)

#### 2.4 Watch Time Efficiency
**Гипотеза:** Не все минуты watch time равны. Revenue/minute сильно варьируется по форматам и платформам.
- Revenue per watch_time_minute по сегментам
- "Эффективность внимания": сколько стоит 1 минута зрителя на каждой платформе
- **Данные:** dataset_1 (watch_time_minutes, revenue_proxy, platform, video_type)

#### 2.5 First 7 Days as Predictor
**Гипотеза:** Поведение видео в первые 7 дней предсказывает lifetime performance. Можно рано выявлять winners.
- first_7d_views / total_views ratio по сегментам
- Какие видео "разгоняются" после 7 дней? Характеристики?
- Early warning model: classification по 7-day metrics → evergreen/not
- **Данные:** dataset_1 (first_7d_views, first_30d_views, total_views) + dataset_2 (cohort)

#### 2.6 Seasonal/Temporal Patterns
**Гипотеза:** Есть сезонные паттерны в performance (месяц публикации, день недели).
- Revenue proxy по месяцу/дню недели публикации
- Взаимодействие с форматом: Shorts лучше в будни, Production в выходные?
- ⚠️ Осторожно с publish_hour (малые выборки, confounders) — только крупные бакеты
- **Данные:** dataset_1 (publish_date → extract month/dow)

### 🟢 Низкий приоритет (nice to have)

#### 2.7 Dislike Ratio Analysis
**Гипотеза:** Высокий dislike ratio → controversy → больше views но меньше revenue (алгоритм пессимизирует).
- dislike/(like+dislike) ratio vs revenue, views, evergreen rate
- **Данные:** dataset_1 (likes, dislikes, revenue_proxy)

#### 2.8 Ad Impression Density
**Гипотеза:** ad_impressions/views сильно варьируется — не все views монетизируются одинаково.
- Ad fill rate по форматам/платформам/каналам
- Что влияет на ad density кроме длительности?
- **Данные:** dataset_1 (ad_impressions, total_views)

---

## Порядок работы

### Фаза 1: Ресёрч (сначала, пока свежий взгляд)
1. **2.1** Channel Efficiency — скорее всего даст самый сильный новый инсайт
2. **2.2** Engagement disconnect — если подтвердится, это killer insight для TheSoul
3. **2.3** Content velocity — практическая рекомендация

### Фаза 2: Интеграция
4. Лучшие находки из ресёрча → добавить в notebook как инсайты 4-5
5. Snapchat concentration → инсайт (из review)

### Фаза 3: Оформление
6. Рефакторинг notebook (1.1-1.2)
7. Русская презентация (1.4)
8. Code quality (1.5)

---

*Создано: 2026-03-07*
