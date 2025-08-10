# Tech Spec: Система редактирования и генерации диалогов Ren’Py

## 1) Назначение

Система покрывает полный цикл работы с диалогами для Ren’Py:

* **Редактор диалогов** (отдельное приложение) — авторинг контента (реплики, выборы, условия, переходы, метаданные).
* **Генератор** (`DialogGen`) — валидация и трансляция JSON → `.rpy` (лейблы, меню, метки голоса, теги форматирования, переходы).
* **Совместимость** с нод-системой ветвления и другими подсистемами (сцены, предметы, UI).

Проект **не** затрагивает рендеринг сцен/спрайтов — это отдельный модуль. Здесь — только текстовые диалоги, ветвления и переходы потока.

---

## 2) Архитектура и пайплайн

```
[Редактор диалогов] → dialogs.json → (валидация) → DialogGen → /game/_gen/dialogs_*.rpy → Ren’Py build
```

* Редактор хранит и экспортирует **детерминированный JSON** (стабильные ID узлов/переходов).
* `DialogGen` — отдельная CLI-утилита без внешних зависимостей; выдаёт `.rpy` по шаблонам.
* Генерируемые файлы **не редактируются вручную**, регенерируются целиком.

---

## 3) JSON-формат диалогов (v1)

### 3.1 Заголовок

```json
{
  "version": "1.0",
  "project": {
    "language": "ru",
    "default_character": "narrator",
    "naming": { "label_prefix": "dlg_", "menu_prefix": "m_" }
  },
  "dialog_trees": [ /* см. ниже */ ]
}
```

### 3.2 Структура дерева диалога

```json
{
  "id": "day1_intro",                // стабильный ID дерева
  "title": "День 1 — вступление",    // подпись для редактора
  "entry_node": "n_start",           // первый узел
  "locals": [                          // локальные переменные дерева (инициализируются при входе)
    { "name": "mood", "type": "str", "default": "neutral" }
  ],
  "using_characters": [ "narrator", "e", "m" ],
  "nodes": [ /* см. типы узлов */ ]
}
```

### 3.3 Типы узлов

Все узлы имеют общие поля: `id`, `type`, `comment?`, `tags?`.

#### 3.3.1 Узел-реплика (`say`)

```json
{
  "id": "n_start",
  "type": "say",
  "character": "e",               // alias из Ren’Py define e = Character("...")
  "text": "Привет! Сегодня начнём.",
  "text_tags": ["b"],              // optional: теги форматирования (b, i, color=#hex, size=...)
  "voice": "voice/day1_001.ogg",  // optional: voice
  "auto_advance": false,            // optional: авто-переход без клика
  "next": "n_choice_1"            // следующий узел
}
```

#### 3.3.2 Узел-выбор (`choice`)

```json
{
  "id": "n_choice_1",
  "type": "choice",
  "prompt": "Как ответить?",
  "choices": [
    {
      "id": "c_ask",
      "text": "Спросить про курс",
      "conditions": ["points >= 0"],     // список выражений
      "effects": ["interest = 'course'"],// side-effects перед переходом
      "next": "n_course"
    },
    {
      "id": "c_silent",
      "text": "Промолчать",
      "next": "n_silent"
    }
  ]
}
```

#### 3.3.3 Узел-условие (`if`)

```json
{
  "id": "n_gate",
  "type": "if",
  "branches": [
    { "condition": "mood == 'happy'", "next": "n_happy" },
    { "condition": "mood == 'sad'",   "next": "n_sad" },
    { "condition": "True",            "next": "n_neutral" }
  ]
}
```

#### 3.3.4 Узел-скрипт (`script`)

Исполняет простой Python-код/присваивания внутри безопасного подмножества.

```json
{
  "id": "n_calc",
  "type": "script",
  "code": [
    "points += 1",
    "mood = 'happy' if points > 3 else mood"
  ],
  "next": "n_choice_2"
}
```

#### 3.3.5 Узлы-переходы (`jump`, `call`, `return`)

```json
{ "id": "n_to_label", "type": "jump",   "label": "some_label" }
{ "id": "n_call",     "type": "call",   "label": "mini_game" }
{ "id": "n_ret",      "type": "return" }
```

#### 3.3.6 Узел-показ экрана (`screen`)

```json
{
  "id": "n_screen",
  "type": "screen",
  "screen": "inventory",
  "params": { "filter": "quest" },
  "next": "n_after_screen"
}
```

#### 3.3.7 Узел-комментарий (`note`)

Не попадает в `.rpy`, используется редактором.

```json
{ "id": "n_note1", "type": "note", "text": "Вставить сцену знакомства" }
```

### 3.4 Макросы и инлайны

* `text_tags`: в генерации разворачиваются в Ren’Py-теги `{b}`, `{i}`, `{color=#}` и т.п.
* Интерполяция "Очки: [points]" — поддерживается напрямую.
* Локализация: все `text` и `prompt` оборачиваются в `_()` при генерации.

### 3.5 Правила идентификаторов

* Все `id` (деревьев, узлов, выборов) — **стабильные** (UUID/slug), не меняются после создания в редакторе.
* Генератор формирует уникальные `label` из `dialog_tree.id` и `node.id`:

  * `label dlg_<tree>__<node>` (напр. `dlg_day1_intro__n_start`).

---

## 4) Правила валидации (Validator)

* Топ-уровень: `version`, `project`, `dialog_trees[]` — обязательны.
* Для каждого дерева: `id`, `entry_node`, `nodes[]` — обязательны.
* Уникальность `id` у деревьев/узлов/choices.
* Графовые проверки: все `next`/`branches[].next`/переходы указывают на существующие узлы или разрешённые цели (`label`).
* Запрет висячих узлов (опционально — как предупреждение).
* Типовая проверка выражений в условиях/эффектах (лексический беллист).

---

## 5) Генерация `.rpy` (DialogGen)

### 5.1 Файловая структура вывода

```
_gen/
  dialogs_helpers.rpy      # общие утилиты/функции
  dialogs_<tree>.rpy       # сгенерированный код дерева
```

### 5.2 Общие правила эмиссии кода

* Для каждого дерева создаётся `label dlg_<tree>__start` (вход) → `jump` на `dlg_<tree>__<entry_node>`.
* Для каждого узла создаётся одноимённый `label dlg_<tree>__<node>`.
* Все тексты заворачиваются в `_()`.
* `voice` → `voice "..."` перед `say`, опционально `stop voice`.
* `auto_advance: true` → `extend` или `with Pause` (в зависимости от UX-политики проекта).

### 5.3 Маппинг узлов

**say →**

```renpy
label dlg_day1_intro__n_start:
    voice "voice/day1_001.ogg"
    e _("{b}Привет! Сегодня начнём.{/b}")
    jump dlg_day1_intro__n_choice_1
```

**choice →**

```renpy
label dlg_day1_intro__n_choice_1:
    menu:
        _("Как ответить?"):
            "Спросить про курс" if points >= 0:
                $ interest = 'course'
                jump dlg_day1_intro__n_course
            "Промолчать":
                jump dlg_day1_intro__n_silent
```

**if →**

```renpy
label dlg_day1_intro__n_gate:
    if mood == 'happy':
        jump dlg_day1_intro__n_happy
    elif mood == 'sad':
        jump dlg_day1_intro__n_sad
    else:
        jump dlg_day1_intro__n_neutral
```

**script →**

```renpy
label dlg_day1_intro__n_calc:
    $ points += 1
    $ mood = 'happy' if points > 3 else mood
    jump dlg_day1_intro__n_choice_2
```

**jump/call/return →**

```renpy
label dlg_day1_intro__n_to_label:
    jump some_label

label dlg_day1_intro__n_call:
    call mini_game
    return

label dlg_day1_intro__n_ret:
    return
```

**screen →**

```renpy
label dlg_day1_intro__n_screen:
    call screen inventory(filter="quest")
    jump dlg_day1_intro__n_after_screen
```

---

## 6) Локализация, озвучка, форматирование

* `_(...)` применяется к `text` и `prompt`.
* Поддержка тэгов: `{b}`, `{i}`, `{color=#hex}`, `{size=}`, `{u}`, `{s}`.
* Поддержка `voice`/`stop voice` в узлах `say`.
* Позже — автогенерация `tl/<lang>` через Ren’Py tools.

---

## 7) Совместимость с нод-редактором ветвлений

* Редактор хранит граф (`nodes[]` + ориентированные рёбра `next/branches`).
* Идентификаторы `node.id` стабильны; перетаскивание, группировка и рефакторинг не меняют `id`.
* Есть служебные узлы (`note`) для документации внутри графа.

---

## 8) Версионирование и миграции

* Поле `version` у корня и у каждого дерева (опционально) для будущих миграций.
* Мигратор в `DialogGen` повышает минорные версии (например, добавление `auto_advance`).
* Лог изменений/депрекейты в README.

---

## 9) Валидация выражений (sandbox)

* Беллист допустимых конструкций: сравнения, логические операции, простые арифметические выражения, индексация запрещена.
* Список доступных имён:

  * локальные `locals[]`, глобальные дефолты (`default` в проекте), `persistent.*`.
* Генератор не исполняет выражения, только синтаксически проверяет и транслирует в Ren’Py.

---

## 10) Производительность и сейвы

* Сгенерированный `.rpy` компилируется в `.rpyc`, выполняется нативно.
* Состояние переменных сохраняется Ren’Py автоматически (при использовании `default`/store).
* Структура лейблов стабильна → сейвы совместимы между билдами при неизменных `id` и порядке переходов.

---

## 11) CLI `DialogGen`

```
python -m dialoggen.cli --in dialogs.json --out-dir /path/to/game
```

* Шаги: загрузка → валидация → генерация файлов.
* Коды выхода: 0 — успех; 2 — нет входного файла; 3 — ошибки валидации.
* Выход: `_gen/dialogs_helpers.rpy` и `_gen/dialogs_<tree>.rpy`.

---

## 12) Пример JSON целого дерева

```json
{
  "id": "day1_intro",
  "title": "День 1 — вступление",
  "entry_node": "n_start",
  "locals": [{ "name": "mood", "type": "str", "default": "neutral" }],
  "using_characters": ["narrator", "e"],
  "nodes": [
    { "id": "n_start", "type": "say", "character": "e", "text": "Привет! Сегодня начнём.", "next": "n_choice_1" },
    { "id": "n_choice_1", "type": "choice", "prompt": "Как ответить?", "choices": [
      { "id": "c_ask", "text": "Спросить про курс", "effects": ["interest='course'"], "next": "n_gate" },
      { "id": "c_silent", "text": "Промолчать", "next": "n_ret" }
    ]},
    { "id": "n_gate", "type": "if", "branches": [
      { "condition": "mood=='happy'", "next": "n_happy" },
      { "condition": "True", "next": "n_neutral" }
    ]},
    { "id": "n_happy", "type": "say", "character": "e", "text": "Классное настроение!", "next": "n_ret" },
    { "id": "n_neutral", "type": "say", "character": "e", "text": "Окей, продолжим.", "next": "n_ret" },
    { "id": "n_ret", "type": "return" }
  ]
}
```

---

## 13) Риски и ограничения

* Сложные выражения и побочные эффекты следует ограничивать (валидация/беллист).
* Перестройка графа с изменением `id` может ломать сейвы — правила миграции обязательны.
* Озвучка и тайминг автопрокрутки требуют чёткой политики UX.

---

## 14) План расширений

* Маркеры **текстовых событий** (паузы `{w=}`, эффекты `{nw}`, шейк/типпинг) через `text_tags`.
* Поддержка **временных веток** (ограничения по времени выбора).
* Интеграция с **редактором сцен** (связь узлов `say` с контекстом сцены и позиций спрайтов).
* Связка с **редактором предметов** (условия/эффекты по инвентарю).
* Экспорт **комментариев/описаний** в `.rpy` как `#` для удобства ревью.
