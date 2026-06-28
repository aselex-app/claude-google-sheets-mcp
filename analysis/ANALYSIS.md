# Аналіз Google Sheets MCP — порівняння репозиторіїв

> Дата: 2026-06-28. Мета: знайти розширені інструменти в трьох публічних
> Google Sheets MCP-серверах і перенести найкраще до нашого сервера.

## Наш поточний сервер (`google_sheets`)

- **Стек**: Python, власна архітектура `SheetsToolHandler` (ABC + реєстр класів),
  не FastMCP.
- **Автентифікація**: OAuth 2.0, **принцип найменших привілеїв**:
  - `spreadsheets` — повний R/W доступ до даних таблиць (вкл. усі `batchUpdate`).
  - `drive.metadata.readonly` — лише читання метаданих для пошуку/переліку.
- **Безпека (наша сильна сторона)**: екранування query-ін'єкцій у Drive `q`,
  санітизація помилок (деталі лише в лог), валідація дат, права `0600` на токени.
- **7 інструментів**: `read_range`, `write_range`, `append_data`, `clear_range`,
  `list_spreadsheets`, `search_spreadsheets`, `get_spreadsheet_info`.
- **Прогалини**: не вміємо створювати таблиці, керувати вкладками (створити/
  видалити/перейменувати/дублювати), робити batch-операції, шукати всередині
  таблиці, вставляти/видаляти рядки/стовпці, форматувати, будувати діаграми.

---

## Репозиторій 1 — `xing5/mcp-google-sheets` (Python, FastMCP, ~20 tools)

**Найбагатший за функціоналом.** Найкращий орієнтир.

| Категорія | Інструменти |
|---|---|
| Читання | `get_sheet_data`, `get_sheet_formulas`, `get_multiple_sheet_data`, `get_multiple_spreadsheet_summary` |
| Запис | `update_cells`, `batch_update_cells`, `add_rows`, `add_columns` |
| Вкладки | `list_sheets`, `create_sheet`, `rename_sheet`, `copy_sheet` |
| Таблиці | `create_spreadsheet`, `list_spreadsheets`, `search_spreadsheets` |
| Пошук | `find_in_spreadsheet` |
| Доступ | `share_spreadsheet` (Drive write) |
| Diagram | `add_chart` (8 типів: COLUMN/BAR/LINE/AREA/PIE/SCATTER/COMBO/HISTOGRAM) |
| Power | `batch_update` (довільний `spreadsheets.batchUpdate` passthrough) |

**Переваги**: batch-операції, читання формул, пошук значень всередині таблиці,
діаграми, гнучка автентифікація (Service Account / OAuth / ADC / base64),
`ENABLED_TOOLS` для економії контексту, Docker + SSE.
**Недоліки**: немає спеціалізованих інструментів форматування (тільки через
сирий `batch_update`), Service Account не створює файли в "My Drive".

**Що беремо**: `create_spreadsheet`, `list_sheets`, `create_sheet`, `rename_sheet`,
`copy_sheet`, `get_multiple_sheet_data` (batch read), `batch_update_cells`
(batch write), `find_in_spreadsheet`, `add_chart`. (`share_spreadsheet` — НІ,
ламає принцип найменших привілеїв.)

---

## Репозиторій 2 — `mkummer225/google-sheets-mcp` (TypeScript, ~15 tools)

**Легкий, зручний CRUD.** Цінність — у гранулярних "зручних" інструментах.

| Категорія | Інструменти |
|---|---|
| Auth | `refresh_auth` |
| Таблиці | `create_spreadsheet`, `rename_doc` |
| Вкладки | `list_sheets`, `create_sheet`, `rename_sheet` |
| Читання | `read_all_from_sheet`, `read_headings`, `read_rows`, `read_columns` |
| Запис | `edit_cell`, `edit_row`, `edit_column` |
| Структура | `insert_row`, `insert_column` |

**Переваги**: дуже прості "людські" операції (редагувати рядок, колонку,
заголовки), чистий OAuth.
**Недоліки**: немає форматування, формул-обчислень, batch read (читає колонки
по одній — неефективно), немає пагінації.

**Що беремо**: ідею `insert_row`/`insert_column` → узагальнюємо до
`insert_dimension`/`delete_dimension` (ROWS/COLUMNS). `read_headings` зручна, але
покривається нашим `read_range`.

---

## Репозиторій 3 — `henilcalagiya/google-sheets-mcp` (Python, FastMCP, 24 tools, Service Account)

**Спеціалізація на нативному Sheets Tables API** (типізовані таблиці з колонками,
типами, dropdown-ами, сортуванням). Унікальний підхід.

| Категорія | Інструменти |
|---|---|
| Spreadsheets | `discover_spreadsheets`, `update_spreadsheet_title` |
| Sheets | `create_sheets`, `delete_sheets`, `create_duplicate_sheet`, `update_sheet_titles`, `analyze_sheet_structure` |
| Tables (native) | `create_table`, `delete_table`, `add_table_records`, `get_table_data`, `update_table_*`, `delete_table_*`, `update_dropdown_options` та ін. (17 шт.) |

**Переваги**: типізовані колонки (TEXT/DOUBLE/CURRENCY/PERCENT/DATE/TIME/BOOLEAN/
DROPDOWN), data validation, `analyze_sheet_structure` (діаграми, slicers, drawings,
developer metadata, тип листа), валідація на боці клієнта, batch-операції з
кількома листами.
**Недоліки**: вузька спеціалізація на Tables API (складно, не всім потрібно),
дублювання коду, Drive лише readonly, немає формул/charts/named ranges.

**Що беремо**: `delete_sheet`, `duplicate_sheet` (із batch для кількох вкладок),
ідею `analyze_sheet_structure` (легша версія через наш `get_spreadsheet_info`).
Повний Tables API — поки НІ (надмірна складність для нашого профілю).

---

## Підсумкове порівняння можливостей

| Можливість | Наш | xing5 | mkummer | henil |
|---|:--:|:--:|:--:|:--:|
| read/write/append/clear range | ✅ | ✅ | ✅ | ✅ |
| list/search spreadsheets | ✅ | ✅ | ➖ | ✅ |
| **create_spreadsheet** | ❌ | ✅ | ✅ | ➖ |
| **list/create/rename/delete sheet (tab)** | ❌ | частк. | частк. | ✅ |
| **duplicate / copy sheet** | ❌ | ✅ | ❌ | ✅ |
| **batch read (кілька діапазонів)** | ❌ | ✅ | ❌ | частк. |
| **batch write (кілька діапазонів)** | ❌ | ✅ | ❌ | ✅ |
| **insert/delete rows/columns** | ❌ | ✅ | ✅ | ✅ |
| **find / find&replace** | ❌ | ✅ | ❌ | ❌ |
| **форматування комірок** | ❌ | сирий | ❌ | частк. |
| **add_chart** | ❌ | ✅ | ❌ | ❌ |
| share (Drive write) | ❌ | ✅ | ❌ | ❌ |
| typed tables / dropdowns | ❌ | ❌ | ❌ | ✅ |
| least-privilege scopes | ✅ | ❌ | ➖ | ➖ |
| санітизація помилок / anti-injection | ✅ | ❌ | ❌ | ❌ |

---

## План імплементації (усе в межах наших скоупів)

Ключове: усі ці операції працюють через **Sheets API** (`spreadsheets` scope),
тому **не вимагають розширення дозволів** і зберігають наш принцип найменших
привілеїв. `create_spreadsheet` робимо через `spreadsheets().create()` (а не
Drive), тож теж лишаємось у межах скоупу.

**Беремо (13 нових інструментів):**

1. `create_spreadsheet` — створення таблиці (+ опц. початкові вкладки).
2. `list_sheets` — перелік вкладок таблиці.
3. `create_sheet` — нова вкладка.
4. `delete_sheet` — видалити вкладку.
5. `rename_sheet` — перейменувати вкладку.
6. `duplicate_sheet` — дублювати вкладку (в межах таблиці).
7. `copy_sheet_to` — копіювати вкладку в іншу таблицю (`sheets.copyTo`).
8. `batch_get_values` — читання кількох діапазонів за один виклик.
9. `batch_update_values` — запис кількох діапазонів за один виклик.
10. `insert_dimension` — вставити рядки/стовпці.
11. `delete_dimension` — видалити рядки/стовпці.
12. `find_replace` — пошук/заміна значень у таблиці чи вкладці.
13. `format_cells` — базове форматування (жирний/курсив/кольори/числовий формат).

**Не беремо (свідомо):**
- `share_spreadsheet` — потребує Drive write scope (ламає least-privilege).
- Повний Tables API (henil) — надмірна складність.
- `batch_update` raw passthrough — обходить нашу валідацію/санітизацію.
- `add_chart` — потужно, але складний chart spec; залишаємо як майбутній крок.
</content>
