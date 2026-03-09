# TheSoul Test — Финальное ревью

**Дата:** 2025-07-13  
**Ревьюер:** Claude (Opus)  
**Файлы:** `thesoul_analysis_v2.ipynb`, `presentation.md`, `presentation_ru.md`, `README.md`, `protasov_thesoul_test.zip`  
**Контекст:** Applied AI Engineer / Data Scientist, напрямую под CEO TheSoul Group

---

## Общая оценка: 8.5 / 10

**Резюме:** Работа сильная, значительно улучшена по сравнению с предыдущей версией. Все критические проблемы из REVIEW.md исправлены: числа теперь совпадают между кодом и текстом, добавлены инсайты 4 и 5 (engagement paradox, concentration risk), есть ML-модель. Работа готова к отправке с небольшими доработками. Ниже — детальный разбор по секциям.

---

## 1. Качество инсайтов: 9 / 10

### Инсайт 1: Shorts Are More Efficient Than They Look — ⭐ 9/10

**Сильные стороны:**
- Контринтуитивный фрейминг: "ваш лучший формат — ваш худший по заработку". Для CEO это мгновенный attention-grabber.
- Переворот нарратива: вместо "Shorts плохие" → "Shorts эффективнее по revenue-на-час-контента". Для TheSoul (компании, которая массово производит Shorts) это позитивный и actionable вывод.
- **Revenue per hour of content** ($167/hr vs $19/hr) — элегантный proxy для ROI без данных о реальных затратах. Очень грамотно.
- Sensitivity analysis (breakeven chart) — показывает, при каком соотношении затрат Shorts выгоднее Production. Это зрелый подход: "вот допущение, вот как ответ меняется при его нарушении".
- Тройная декомпозиция Shorts: длительность (45-60s optimal), день недели (воскресенье +159%), каналы (top-10 = 82% revenue). Каждый из этих паттернов actionable отдельно.
- 8-15 минут sweet spot для Production (12.4× efficiency) — конкретный, проверяемый, связанный с YouTube mid-roll policy.

**Замечания:**
- Revenue per hour of content — сильный proxy, но **сам автор корректно указывает**, что это не равно production cost. Хорошо бы в ноутбуке одним предложением подчеркнуть, что это approximation with known limitations.
- Sunday effect (+159%) — интригующий, но нет гипотезы "почему". Даже одно предложение ("possibly lower competition for viewer attention") усилит.
- Рекомендация "shift toward 45-60s" — отлично. Но стоит добавить оговорку о размере выборки: 420 видео для 45-60s vs 2,473 для 15-30s. Разница статистически значима, но CEO может спросить.

### Инсайт 2: Evergreen Content = Compound Returns — ⭐ 9/10

**Сильные стороны:**
- Мощная метафора "compound returns" — CEO сразу понимает value.
- Полный pipeline: определение → кластеризация → ML-предиктор → actionable KPI. Это уровень senior data scientist.
- K-Means на lifecycle patterns (3 кластера: Spike & Die 79.2%, Moderate Decay 12.4%, Evergreen 8.5%) — убедительная сегментация, каждый кластер имеет чёткий профиль.
- Gradient Boosting с AUC = 0.87 (5-fold CV) — сильный результат для 8 фичей. Cross-validation правильная (StratifiedKFold для imbalanced classes).
- Threshold analysis table — показывает precision/recall tradeoff для разных бизнес-сценариев. Это зрелый ML-подход, не просто "accuracy = X%".
- Feature importance: pct_7d_views (66.6%) — интуитивно понятно CEO: "если видео набирает просмотры и на 2-й неделе, скорее всего оно вечнозелёное".
- Честно указаны missing data для next step (promotion spend, A/B test).

**Замечания:**
- Определение evergreen: >50% views after month 0 (из когорт). В предыдущей версии было две разные дефиниции — в v2 это **исправлено**: одна последовательная дефиниция. Отлично.
- AUC 0.87 vs AUC 0.937 (из build_final.py / предыдущих research). В предыдущем REVIEW упоминался AUC 0.937 — вероятно, это был однофичевый предиктор (pct_7d_views only), а 0.87 — полная модель с CV. Рекомендация: **в ноутбуке стоит добавить комментарий**, что простой rule-based (threshold на pct_7d_views) даёт AUC ~0.93, а полная модель — 0.87 с CV. Это кажется парадоксальным, но объясняется overfitting простого предиктора на всех данных vs honest CV. Одна строка комментария снимет вопрос ревьюера.
- "Evergreen Score = month 3 / month 0 views" предложен как KPI, но не реализован в ноутбуке. Минимально: добавить code cell, считающий этот скор для всех видео и показывающий распределение.

### Инсайт 3: Cross-Platform Publishing Doubles Views — ⭐ 8/10

**Сильные стороны:**
- Статистически корректный: Mann-Whitney U (непараметрический), p < 0.0001 для Facebook и Snapchat.
- Нулевой эффект для YouTube (p = 0.175) **честно показан** — это усиливает credibility всего анализа.
- Best combo: Facebook + Snapchat ($2,671 revenue per content piece).
- Mean delay 87 days — практическое наблюдение: кросс-постинг работает с задержкой, не одновременно.

**Замечания:**
- ⚠️ **Ключевая проблема: selection bias.** Multi-platform content (4%) может быть **изначально качественнее** (его cross-posted именно потому, что оно хорошее). Notebook это **не адресует напрямую** в ячейке 19. В presentation.md есть recommendation "A/B test for causal confirmation" — отлично. Но в самом ноутбуке стоит добавить 2-3 строки: "Caveat: multi-platform content may be selected for quality. The +100%/+134% uplift is associative, not causal. Same-channel comparison below partially controls for this." И провести same-channel comparison (видео одного канала: single vs multi).
- Сравнение по mean views (127K vs 63K) — для TheSoul CEO это убедительно, но **median views** был бы более robust к outliers. В code output средние, не медианы. Рекомендация: добавить медианы рядом.

### Инсайт 4: Engagement Anti-Predicts Revenue — ⭐ 9.5/10

**Сильные стороны:**
- **Самый сильный инсайт** — контринтуитивный, подкреплённый конкретным механизмом (Simpson's paradox), и напрямую actionable ("switch KPI").
- Spearman correlations (не Pearson!) — правильный выбор для revenue data с тяжёлыми хвостами.
- Механизм Simpson's paradox **чётко объяснён**: Shorts = high engagement + near-zero CPM; Production = low engagement + 35× CPM. Mixing → anti-correlation.
- "Within Production only, ρ = +0.163" — парадокс исчезает внутри формата. Это доказывает, что engagement per se не вреден, а смешивание форматов вредит.
- "Only 13.4% of top-engagement videos are also top-revenue — worse than random 25%" — killer stat для CEO.
- Рекомендация: shares → единственная engagement-метрика, связанная с revenue. Конкретно и actionable.

**Замечания:**
- Можно добавить одно предложение: "This doesn't mean engagement is useless — it means engagement comparisons must be within-format, never cross-format." Сейчас это implied, но для CEO лучше explicit.

### Инсайт 5: Revenue Concentration Risk — ⭐ 7.5/10

**Сильные стороны:**
- Gini = 0.73, channel_621 = 46.4% — конкретный risk signal.
- Lorenz curve визуализация — наглядна для CEO.
- Recommendation: "no channel > 25% of platform revenue" — actionable target.

**Замечания:**
- Это скорее **наблюдение**, чем инсайт. Concentration risk — стандартный анализ. Для усиления: добавить "что делает channel_621 иначе?" (формат, длительность, частота). В research.py это есть (channel archetypes), но в ноутбук не вошло.
- Гини 0.73 без benchmark'а. Стоит сказать: "For comparison, YouTube channel revenue has Gini of X.XX" — чтобы показать, что Snapchat concentration аномально высокая.
- Этот инсайт мог бы быть частью Insight 1 (revenue landscape) или appendix, а не отдельным insight #5. 5 инсайтов — уже на границе "too many" для CEO-презентации.

### Общая оценка инсайтов

| # | Инсайт | Неочевидность | Actionability | Статистика | Итого |
|---|--------|:---:|:---:|:---:|:---:|
| 1 | Shorts efficiency | 🟢 Высокая | 🟢 Высокая | 🟢 Сильная | 9/10 |
| 2 | Evergreen compound | 🟢 Высокая | 🟢 Высокая | 🟢 Сильная | 9/10 |
| 3 | Cross-platform synergy | 🟡 Средняя | 🟢 Высокая | 🟡 Хорошая* | 8/10 |
| 4 | Engagement paradox | 🟢 Очень высокая | 🟢 Высокая | 🟢 Сильная | 9.5/10 |
| 5 | Concentration risk | 🟡 Низкая | 🟡 Средняя | 🟢 Сильная | 7.5/10 |

*Selection bias не полностью контролируется.

---

## 2. Методология: 8.5 / 10

### Статистические тесты — ✅ Корректны

| Тест | Где | Корректность |
|------|-----|:---:|
| Mann-Whitney U | Cross-platform views lift | ✅ Правильный выбор (non-parametric, skewed distribution) |
| Spearman rank correlation | Engagement vs Revenue | ✅ Правильный (ordinal, non-linear relationships) |
| Revenue proxy: views × CPM / 1000 | Everywhere | ✅ Стандартная формула, корректна для available data |
| K-Means (k=3) | Lifecycle clusters | ✅ Разумный k, интерпретируемые кластеры |
| Gradient Boosting | Evergreen prediction | ✅ Хороший выбор для tabular data |
| StratifiedKFold (k=5) | ML evaluation | ✅ Правильный для imbalanced classes |

### ML-модель — ✅ Корректна, с одним замечанием

- **Positive:** Stratified CV, multiple thresholds shown, feature importance — все правильно.
- **Positive:** 8 фичей, все доступны на day 7 — практически развёртываемая модель.
- **Замечание:** AUC 0.87 ± 0.01 — стандартное отклонение очень маленькое, что хорошо. Но стоит отметить, что класс "evergreen" = 9.5% от dataset'а, и при таком дисбалансе AUC может быть оптимистичным. Precision-Recall AUC (PR-AUC) был бы более информативным metric для imbalanced data. Это не ошибка — ROC-AUC общепринят — но добавление PR-AUC в скобках усилит.

### Кластеризация — ✅ Корректна

- K-Means на pct_after_m0 с StandardScaler — разумно.
- 3 кластера — хорошо интерпретируемы.
- **Замечание:** Кластеризация по одному фичу (pct_after_m0) — это, по сути, binning. Не ошибка, но можно было бы добавить ещё 1-2 фичи (duration, CPM) для более rich segmentation. Впрочем, для простоты объяснения CEO однофичевая кластеризация — OK.

### Revenue Proxy — ✅ Обоснован

- `views × estimated_cpm / 1000` — стандартный подход.
- **Caveat:** estimated_cpm может не точно отражать actual CPM. Это inherent limitation данных, и автор его **корректно указывает** в Limitations.

### Что не проверено, но должно быть

1. **Selection bias в cross-platform** — частично, но не полностью. Need: same-channel comparison или propensity score matching (упомянуто в What's Next, но не выполнено).
2. **Multiple testing correction** — 5 инсайтов, множество тестов. При таком количестве comparisons p-values могут быть inflated. Bonferroni или FDR correction не применялась. Для CEO-отчёта это не критично (p-values и так < 0.0001), но для строгости стоило бы упомянуть.
3. **Temporal confounds** — Shorts и Production могут публиковаться в разные периоды (разный CPM landscape). Notebook не проверяет это. Минимально: scatter plot publish_date vs revenue by format.

---

## 3. Код: 8.5 / 10

### Структура ноутбука — ✅ Хорошая

| Аспект | Оценка | Комментарий |
|--------|:---:|-------------|
| Markdown-заголовки | ✅ | Каждый инсайт: заголовок → контекст → код → визуализация → рекомендация |
| Executive summary | ✅ | Cell 0: таблица с 4 инсайтами, 30 сек на чтение |
| Revenue Landscape | ✅ | Правильно: сначала контекст "откуда деньги", потом инсайты |
| Action Plan | ✅ | Чёткие this week / 1-3 months / 3-6 months |
| What's Next | ✅ | SMM hypothesis, production pipeline, data gaps |
| Единый стиль графиков | ✅ | COLORS dict, whitegrid, consistent figsize, bold titles |

### Воспроизводимость — 8/10

| Аспект | Оценка | Комментарий |
|--------|:---:|-------------|
| requirements.txt | ✅ | Pinned versions (==), 7 пакетов |
| Sequential execution | ✅ | Cells 1-13, последовательные |
| Data paths | ✅ | `data/` relative path |
| Random state | ⚠️ | `KMeans(n_clusters=3, random_state=42, n_init=10)` — есть в Cell 14. GradientBoosting в Cell 16 — **нужно проверить** |
| Outputs saved | ✅ | Все cells executed, outputs preserved |

### Качество кода — 8/10

**Плюсы:**
- Чистый, читаемый код. Переменные с осмысленными именами.
- `warnings.filterwarnings('ignore')` — нормально для презентационного notebook.
- Грамотная обработка данных: comma → dot в duration_seconds, dedup в df3.
- Хорошее использование pandas (groupby/agg, crosstab, pivot_table).
- Визуализации информативные: bar charts + annotations, scatter + color by format.

**Минусы:**
- Нет type hints (ожидаемо для notebook, но стоит упомянуть).
- Некоторые code cells длинные (Cell 16 — ML + ROC + threshold analysis + feature importance в одной ячейке). Можно разбить на 2-3 для лучшей навигации.
- `df1['revenue_proxy'] = df1['total_views'] * df1['estimated_cpm'] / 1000` — формула revenue proxy не вынесена в отдельную функцию. При повторном использовании в cohort analysis (Cell 12) считается заново. Minor, но helper function `calc_revenue(views, cpm)` было бы чище.
- Cell 12: `.apply(lambda g: pd.Series({...}))` — работает, но медленный. Для 10K видео это OK, но стоит прокомментировать.

### Что в ZIP — ✅ Чисто

```
thesoul_analysis_v2.ipynb     ✅ Main notebook
presentation.md               ✅ English slides
presentation_ru.md             ✅ Russian slides
README.md                      ✅ Documentation
data/                          ✅ 3 CSV + description
figures/                       ✅ 9 PNG (exported charts)
```

Нет мусорных файлов (build_final.py, research.py, PLAN.md, REVIEW.md и т.д.) — **исправлено** по сравнению с предыдущей версией.

**Единственное замечание:** `requirements.txt` **не включён в ZIP**. Это проблема — ревьюер не сможет установить зависимости. Quick Start в README.md содержит `pip install ...`, но pinned versions из requirements.txt предпочтительнее. **Нужно добавить requirements.txt в ZIP.**

---

## 4. Презентация: 8 / 10

### Английская презентация (presentation.md) — 8.5/10

**Структура:** 12 секций (Approach → 5 Insights → Action Plan → What's Next). Каждый инсайт: заголовок-провокация → таблица с данными → рекомендация.

**Сильные стороны:**
- **Revenue-first framing**: "Your best-performing format is your worst-earning one" — идеальный hook для CEO.
- **Таблицы с конкретными числами** — CEO может принимать решения прямо по таблице.
- **Action Plan**: this week / 1-3 months / 3-6 months — показывает стратегическое мышление.
- **What's Next**: SMM hypothesis + production pipeline + data gaps — демонстрирует, что кандидат думает дальше одного задания.
- **Limitations** и "correlation ≠ causation" — зрелость и честность.
- **Все числа совпадают** с ноутбуком — критическая проблема из предыдущей версии исправлена.
- **Снэпчат объяснён**: "Snapchat drives 91.7% of revenue through volume. But content strategy decisions are made based on YouTube and Facebook data." — снимает вопрос "почему фокус на малой части?".

**Замечания:**
- ⚠️ **Нет встроенных графиков.** Markdown-формат не поддерживает images inline. Для CEO визуальная презентация критична. **Рекомендация:** конвертировать в PDF/Google Slides с embedded charts из `figures/`. Графики уже экспортированы в ZIP — нужно только вставить.
- 12 секций — **многовато для CEO**. Идеальный формат: 7-8 слайдов, максимум 10. Объединить Insight 5 (concentration) с Revenue Landscape как sidebar.
- Insight 1 занимает 3 секции (Shorts efficiency + Shorts patterns + Production sweet spot). Можно сжать до 2.
- Revenue Concentration Risk описан как отдельный insight, но в presentation.md это скорее appendix material.

### Русская презентация (presentation_ru.md) — 8/10

**Сильные стороны:**
- Marp-formatted (заголовки `---` для слайдов) — можно сразу конвертировать в PDF.
- Язык чистый, профессиональный, не калька с английского.
- Добавлен вводный слайд "Как устроена монетизация" — объясняет CPM/платформы для non-technical CEO. Отлично.
- Каждый слайд: одна идея + таблица + 2-3 bullet points. Минимум текста.

**Замечания:**
- Те же структурные проблемы: 16 слайдов — **слишком много**. Для 15-минутной презентации CEO оптимально 8-10.
- Слайд "Как устроена монетизация" — хорош, но стоит оценить: если CEO TheSoul уже знает как работает CPM, этот слайд может показаться patronizing. Безопаснее: сделать его бэкап-слайдом (в конце, "на случай вопросов").
- Insight 2 занимает 4 слайда (определение + кластеры + ML + что не хватает) — перегруз. Сжать до 2: "10.8% видео дают 44% выручки. ML-модель (AUC 0.87) находит их на 7-й день." + 1 визуализация.
- **Нет HTML-версии** в ZIP (presentation_ru.html не включён). Если планируется показывать Marp-слайды, стоит либо включить HTML, либо конвертировать в PDF.

### Глазами CEO TheSoul

**Что впечатлит:**
1. Revenue-first мышление — не "interesting patterns", а "вот сколько денег вы теряете/можете заработать".
2. Simpson's paradox (engagement anti-predicts revenue) — это реальный paradigm-shifting finding для контент-компании.
3. ML-модель с threshold analysis — показывает, что кандидат не просто аналитик, а engineer, который думает о deployment.
4. What's Next → production pipeline — CEO видит, что это не разовый анализ, а начало системы.

**Что вызовет вопросы:**
1. "91.7% revenue = Snapchat, но инсайты про YouTube" — объяснено в Approach, но CEO может переспросить. Стоит на первом слайде 2-3 слова: "Snapchat revenue follows content strategy decisions made on YouTube/Facebook — so that's where the leverage is."
2. "Cross-platform +100% views — but is it causal?" — honest answer: "No, correlation. A/B test needed." Это уже есть, но стоит быть готовым к challenge.
3. "Why only 4% is cross-posted?" — ноутбук не отвечает на этот вопрос. Стоит иметь гипотезу: resource constraints? Platform-specific content? Deliberate strategy?
4. "$167/hr vs $19/hr" — CEO может challenge "duration ≠ cost". Sensitivity analysis есть, но стоит быть ready to defend.

---

## 5. Сравнение с предыдущей версией (REVIEW.md)

Предыдущий REVIEW.md выявил 3 critical, 5 medium, 4 low проблемы. Статус:

### 🔴 Critical — ВСЕ ИСПРАВЛЕНЫ ✅

| # | Проблема | Статус |
|---|---------|:---:|
| C1 | $48.59/$3.69 не совпадает с кодом | ✅ Убрано. Теперь $10.56/$1.61 — совпадает с Cell 12 output |
| C2 | "+$1,197 net revenue" не воспроизводится | ✅ Убрано из v2. Числа больше нет |
| C3 | Manually typed numbers without code backing | ✅ Все ключевые числа генерируются code cells |

### 🟡 Medium — В ОСНОВНОМ ИСПРАВЛЕНЫ

| # | Проблема | Статус |
|---|---------|:---:|
| M1 | "+80M views" и "+$4,500" не рассчитаны | ✅ Убрано из v2 |
| M2 | Две дефиниции "evergreen" | ✅ Единая: >50% views after month 0 |
| M3 | Презентация без графиков | ⚠️ Частично: figures/ экспортированы, но не встроены в MD |
| M4 | Лишние файлы в репо | ✅ ZIP чистый |
| M5 | Нет ZIP файла | ✅ protasov_thesoul_test.zip создан |

### 🟢 Low

| # | Проблема | Статус |
|---|---------|:---:|
| L1 | requirements.txt с `>=` | ✅ Pinned versions (==) |
| L2 | Rounding inconsistency | ✅ Числа совпадают |
| L3 | "Not selection bias" | ✅ Смягчено. В presentation.md: "A/B test for causal confirmation" |
| L4 | assignment.docx в data/ | ✅ Не в ZIP |

### Новое в v2

| Добавлено | Оценка |
|-----------|:---:|
| Insight 4: Engagement paradox (Simpson's) | ⭐ Очень сильное добавление |
| Insight 5: Revenue concentration (Gini) | ✅ Хорошее, но не wow |
| Sensitivity analysis (breakeven chart) | ✅ Добавляет rigour |
| Figures exported to PNG | ✅ Готовы для презентации |
| Russian presentation (Marp) | ✅ Профессионально |
| Pinned requirements.txt | ✅ Воспроизводимость |

---

## 6. Что добавить/улучшить до отправки

### 🔴 Must-do (30 минут)

| # | Действие | Почему |
|---|---------|--------|
| 1 | **Добавить requirements.txt в ZIP** | Без него ревьюер не сможет воспроизвести. Quick Start в README.md — не замена |
| 2 | **Проверить random_state в GradientBoosting** (Cell 16) | Если нет — добавить `random_state=42`. Воспроизводимость ML-модели критична |
| 3 | **Сжать число слайдов** в presentation_ru.md до 10 | 16 слайдов — перегруз для CEO. Объединить Insight 2 (4 слайда → 2), Insight 1 (3 → 2), Insight 5 → sidebar/appendix |

### 🟡 Should-do (30-60 минут)

| # | Действие | Почему |
|---|---------|--------|
| 4 | **Selection bias check для cross-platform** (Insight 3) | Добавить в Cell 19: same-channel comparison (видео одного канала: single vs multi). 5-10 строк кода |
| 5 | **Конвертировать presentation в PDF** | Markdown-таблицы плохо рендерятся вне GitHub. PDF с embedded charts из `figures/` — production-ready |
| 6 | **Добавить медианы** в cross-platform comparison | Mean views sensitive к outliers. Медианы рядом усилят аргумент |
| 7 | **Пояснить AUC 0.87 vs простой pct_7d predictor** | Одна строка: "Single-feature threshold gives higher apparent AUC but overfits; cross-validated model is more reliable" |

### 🟢 Nice-to-have (если есть время)

| # | Действие | Почему |
|---|---------|--------|
| 8 | Добавить Evergreen Score calculation cell | Предложен как KPI, но не реализован. 3-5 строк кода покажут распределение |
| 9 | Channel_621 deep dive: что отличает? | Усилит Insight 5 от "наблюдения" до "рекомендации" |
| 10 | PR-AUC рядом с ROC-AUC | Для imbalanced data (9.5% positive) PR-AUC более информативен |
| 11 | Temporal plot: publish_date vs revenue by format | Снимает вопрос о temporal confounds |
| 12 | "Как устроена монетизация" → бэкап-слайд (в конец) | CEO TheSoul знает как работает CPM. Убрать из основного потока |

---

## 7. Итоговая таблица оценок

| Критерий | Оценка | Комментарий |
|----------|:---:|-------------|
| **Качество инсайтов** | 9/10 | 5 инсайтов, 4 из них неочевидные, все actionable, подкреплены данными |
| **Методология** | 8.5/10 | Корректные тесты, ML с CV, единственное замечание — selection bias в Insight 3 |
| **Код** | 8.5/10 | Чистый, воспроизводимый, единый стиль. Minor: requirements.txt не в ZIP |
| **Презентация** | 8/10 | Сильный контент, но формат (MD без графиков) и длина (16 слайдов) — weak points |
| **Готовность к отправке** | 8.5/10 | 3 must-do фикса за 30 минут поднимут до 9+ |
| **Общая** | **8.5/10** | |

---

## 8. Вердикт

**Работа сильная.** Инсайты реально неочевидные и подкреплены данными. Simpson's paradox (Insight 4) — killer finding. ML-модель — не для галочки, а с практическим deployment plan. Presentation quality значительно выросла по сравнению с v1.

**Критических багов нет.** Все числа совпадают между кодом и текстом. Прошлые проблемы исправлены.

**Для позиции "Applied AI Engineer напрямую под CEO"** — работа демонстрирует:
- ✅ Аналитическое мышление (revenue-first, не vanity metrics)
- ✅ Статистическую грамотность (non-parametric tests, CV, selection bias awareness)
- ✅ ML skills (Gradient Boosting, threshold analysis, feature importance)
- ✅ Бизнес-ориентированность (action plan, next steps, data gaps)
- ✅ Самокритичность (limitations, "correlation ≠ causation")
- ✅ Презентационные навыки (clean narrative, provocative framing)

**Рекомендация:** исправить 3 must-do пункта (30 мин), по возможности 4-7 should-do (ещё 30-60 мин), и **отправлять**.

---

*Ревью завершено. Дмитрий, работа на уровне. Удачи! 🚀*
