# TheSoul Test — Полное ревью

**Дата:** 2025-07-12  
**Ревьюер:** Claude (по запросу Димы)  
**Общая оценка: 7.5 / 10** — сильная аналитика, слабая упаковка. 3-5 фиксов за 1-2 часа поднимут до 9.

---

## 1. Ноутбук (thesoul_analysis.ipynb)

### Код: 8/10

**✅ Сильные стороны:**
- Чистый, читаемый код. Единый стиль визуализаций (PALETTE, whitegrid, consistent figsize)
- Корректная обработка данных: comma-as-decimal fix, dedup в df3, fillna(0) в cumulative revenue
- Хорошая EDA-структура: crosstab → distributions → revenue landscape → 3 инсайта
- Все 15 code cells executed, нет ошибок, sequential execution_count 1-15
- Грамотное использование scipy (Mann-Whitney U), не overfit'ит статистику

**⚠️ Проблемы:**

| # | Серьёзность | Проблема | Где |
|---|------------|---------|-----|
| 1 | 🔴 CRITICAL | **Числа в markdown не совпадают с кодом.** Cell 19 claims $48.59 evergreen / $3.69 normal. Actual calc gives **$42.15 / $3.26**. Числа 48.59 и 3.69 не генерируются ни одной ячейкой ноутбука. | Cell 19 |
| 2 | 🔴 CRITICAL | **"+$1,197 net revenue" — не воспроизводится.** Мой расчёт (10% shorts × 3:1 effort): gained=$1,681, lost=$660, **net=$1,021**, не $1,197. Число нигде не считается в коде. | Cell 12 |
| 3 | 🟡 MEDIUM | **Две разные дефиниции "evergreen".** Cell 15 uses m3/m0 > 10% → 8.5%. Cell 17 lifecycle uses m1/m0 > 50% → 10.6%. Оба называются "Evergreen" без пояснения. Ревьюер может запутаться. | Cells 15, 17 |
| 4 | 🟡 MEDIUM | **"+80M incremental views" — не рассчитан в коде.** Это ключевой claim Insight 3, но нигде не показано как получена цифра. | Cell 24 |
| 5 | 🟡 MEDIUM | **"+$4,500 lifetime value" (Summary)** — тоже взят из воздуха. | Cell 25 |
| 6 | 🟢 LOW | `warnings.filterwarnings('ignore')` — нормально для презентации, но лучше фильтровать конкретные warnings. | Cell 1 |
| 7 | 🟢 LOW | Нет `pd.set_option('display.float_format')` — числа в таблицах иногда показываются с разной точностью. | Cell 1 |

### Качество анализа: 8.5/10

**Инсайты реально неочевидные и полезные:**

1. **Short-Form Monetization Trap** — 9/10. Классика "vanity metrics". 35× CPM gap — конкретная, проверяемая цифра. Duration bucket chart с 8-min threshold — отлично. Для TheSoul (компании Shorts-heavy) это напрямую actionable.

2. **Evergreen Compound Returns** — 8/10. Сильный инсайт: 8.5% → 54.5% revenue. Retention curves визуально убедительны. Platform comparison (YouTube 2.7× vs Facebook) добавляет глубины. Минус: "Evergreen Score" KPI предложен, но не реализован.

3. **Cross-Platform Synergy** — 7.5/10. Статистически корректный (Mann-Whitney U, p < 0.01). Selection bias addressed через same-channel comparison. НО: correlation ≠ causation — и notebook это честно признаёт. YouTube neutral result усиливает credibility.

**Общая глубина:** Хорошо, что автор не остановился на описательной статистике. Revenue proxy, cohort analysis, lifecycle segmentation, selection bias control — это уровень data scientist, не аналитика.

### Воспроизводимость: 7/10

- ✅ requirements.txt с минимальными версиями
- ✅ Notebook executed end-to-end (timestamps visible)
- ✅ Данные в data/ рядом
- ⚠️ Нет `random_state` (не критично — нет random operations)
- ⚠️ Нет pinned versions — `>=1.5.0` может поломаться через год
- ❌ Нет `pyproject.toml` (minor, requirements.txt acceptable)

---

## 2. Презентация (presentation.md)

### Структура: 8/10

7 слайдов (Approach → 3 Insights → What's Next → Appendix → Limitations). Логичная последовательность. Каждый инсайт: заголовок-провокация + таблица + recommendation.

**✅ Сильные стороны:**
- "Your best-performing format is your worst-earning one" — отличный hook
- Limitations slide — показывает зрелость, не пытается oversell
- "What's Next" — демонстрирует мышление (causal inference, prediction, NLP)
- Appendix с revenue landscape и lifecycle distribution — добавляет credibility

**⚠️ Проблемы:**

| # | Серьёзность | Проблема |
|---|------------|---------|
| 1 | 🔴 CRITICAL | **$48.59 / $3.69 — неверные числа** (повтор из ноутбука). Должно быть $42.15 / $3.26. |
| 2 | 🔴 CRITICAL | **"+$1,197" — не воспроизводится.** Фактически ~$1,021. |
| 3 | 🟡 MEDIUM | **"+80M incremental views" — не обоснован расчётом.** |
| 4 | 🟡 MEDIUM | **Формат Markdown** — TheSoul скорее ожидает PDF/Google Slides. Markdown-таблицы плохо рендерятся вне GitHub. |
| 5 | 🟡 MEDIUM | **Нет графиков в презентации** — только таблицы. Для "7 slides" это критично, таблицы менее убедительны визуально. |
| 6 | 🟢 LOW | Lifecycle table в Appendix: "Flash burn 41.6%" vs notebook output "41.7%" — rounding inconsistency. |
| 7 | 🟢 LOW | "Conservative estimate" label используется и для $1,197 и для +80M — разные уровни строгости под одним словом. |

### Грамматика/стилистика: 9/10

Английский чистый, профессиональный. Нет грамматических ошибок. Стиль data-driven и лаконичный. Единственное: "Not selection bias" на слайде 3 — слишком категорично. Лучше "Selection bias controlled" или "Robust to selection bias check".

---

## 3. Общее

### README: 8.5/10

- Хороший: Quick Start, Key Insights с цифрами, Data dictionary, Methodology
- ✅ "Revenue proxy" methodology explained
- ✅ Data table с размерами
- Минус: нет License/Contact section (minor)

### Структура проекта

**Что в финальном ZIP (должно быть):**
```
thesoul_analysis.ipynb    # Main notebook
presentation.md           # Slides
README.md
requirements.txt
data/
  dataset_1_video_performance.csv
  dataset_2_cohort_analysis.csv
  dataset_3_cross_platform.csv
  datasets_description.md
```

**⚠️ PROBLEM: Лишние файлы в репо:**

| Файл | Проблема |
|------|---------|
| `thesoul_analysis_v2.ipynb` | Draft с 5 инсайтами. НЕ должен попасть в ZIP. |
| `build_final.py` | Scaffold-скрипт. НЕ должен попасть в ZIP. |
| `research.py`, `research_deep.py` | Рабочие скрипты. НЕ должны. |
| `PLAN.md`, `RESEARCH_RESULTS.md`, `review_deep_insights.md` | Рабочие заметки. НЕ должны. |
| `presentation_ru.md`, `presentation_ru.html` | Русские версии. НЕ должны. |
| `data/assignment.docx` | Оригинальное задание. Спорно — лучше не включать. |

**ZIP пока не создан** — нужно будет собрать чисто.

---

## 4. Итоговая таблица проблем

### 🔴 Critical (исправить обязательно)

| # | Проблема | Где | Как исправить |
|---|---------|-----|---------------|
| C1 | Evergreen revenue $48.59/$3.69 — не совпадает с кодом | Notebook Cell 19, Presentation Slide 2 | Заменить на $42.15 / $3.26. Или добавить code cell который считает эти числа. |
| C2 | "+$1,197 net revenue" — фактически ~$1,021 | Notebook Cell 12, Presentation Slide 1 | Пересчитать и исправить. Либо показать формулу в code cell. |
| C3 | Manually typed numbers without code backing | Cells 12, 19, 24, 25 | Каждое число в markdown → должно быть computed в code cell выше. "Show your work." |

### 🟡 Medium (желательно исправить)

| # | Проблема | Как исправить |
|---|---------|---------------|
| M1 | "+80M views" и "+$4,500" — не рассчитаны | Добавить code cell с расчётом или убрать конкретные цифры, заменить на "significant uplift" |
| M2 | Две дефиниции "evergreen" без пояснения | Добавить markdown: "Note: lifecycle table uses m1/m0 binning, evergreen classification uses m3/m0 > 10%." |
| M3 | Презентация без графиков | Либо конвертировать в PDF с embedded charts, либо экспортировать ключевые графики как PNG и ссылаться |
| M4 | Лишние файлы в репо | При сборке ZIP включить только финальные deliverables |
| M5 | Нет ZIP файла | Создать `protasov_thesoul_test.zip` с чистой структурой |

### 🟢 Low (nice-to-have)

| # | Проблема | Как исправить |
|---|---------|---------------|
| L1 | requirements.txt с `>=` вместо `==` | Pin versions: `pandas==2.2.0` etc. |
| L2 | Rounding inconsistency (41.6% vs 41.7%) | Использовать одну точку рассчёта |
| L3 | "Not selection bias" слишком категорично | → "Selection bias controlled" |
| L4 | `assignment.docx` в data/ | Убрать из ZIP |

---

## 5. Глазами ревьюера в TheSoul

### Что впечатлит:
1. **Revenue-first мышление** — не пытается показать "интересные паттерны", а сразу переводит в деньги
2. **Самокритичность** — Limitations slide, "correlation ≠ causation" честно
3. **Cross-platform insight** — для компании с 10+ каналами на разных платформах это напрямую actionable
4. **Статистическая грамотность** — Mann-Whitney, не t-test. Selection bias check. Cohort analysis вместо простых средних.

### Что вызовет вопросы:
1. **"Где числа?"** — ревьюер проверит $48.59 и не найдёт его в коде → red flag
2. **Snapchat elephant** — 91.7% revenue = Snapchat. Insights 1 и 2 про YouTube (8.3% revenue). Ревьюер спросит: "Why focus on the small part?"
3. **3 инсайта vs задание** — задание просит "3 неочевидных инсайта". Формально ОК, но v2 notebook с 5 инсайтами (engagement anti-predicts revenue, concentration risk) был бы сильнее.
4. **Отсутствие ML** — для позиции "Applied AI Engineer" ожидается хотя бы простая модель. Evergreen predictor (AUC 0.937 в v2) был бы сильным дополнением.

### Что бы я добавил:
1. **Один cell с early evergreen predictor** (logistic regression, 3 features, 7-day data) — уже есть в v2 с AUC 0.937
2. **Insight 4: Engagement Anti-Predicts Revenue** — из v2. r=-0.24 correlation — killer finding для TheSoul
3. **Snapchat deep dive** — хотя бы одно предложение объясняющее почему 91.7% revenue
4. **Code cell для каждого claim** — золотое правило: если число в markdown, оно должно быть в output выше

---

## 6. Конкретный план действий (1-2 часа)

### Must-do (30 мин):
1. Исправить $48.59→$42.15, $3.69→$3.26 в Cell 19 и presentation
2. Исправить $1,197→$1,021 (или пересчитать с правильными параметрами и показать формулу)
3. Добавить code cell перед каждым Summary markdown: пусть считает и print'ит числа
4. Собрать чистый ZIP без мусорных файлов

### Should-do (30 мин):
5. Добавить расчёт "+80M views" или заменить на "significant uplift potential"
6. Пояснить две дефиниции evergreen (одно предложение в markdown)
7. "Not selection bias" → "Robust to selection bias check"

### Nice-to-do (30-60 мин):
8. Добавить Insight 4 (Engagement anti-predicts revenue) из v2 — сделает работу значительно сильнее
9. Добавить evergreen predictor cell (AUC 0.937) — покажет ML skills
10. Конвертировать презентацию в PDF с embedded графиками

---

*Ревью завершено. Работа в целом сильная — аналитика глубокая, инсайты действительно неочевидные. Критические баги — это несовпадение чисел между кодом и текстом. Легко чинится за час.*
