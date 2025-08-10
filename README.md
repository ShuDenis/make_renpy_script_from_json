
# make_renpy_script_from_json

A small utility to convert JSON-described dialogues into a Ren'Py script.

## Project structure

```
README.md
LICENSE
pyproject.toml
scripts/
    run.py
src/
    make_renpy_script/
        __init__.py
        converter.py
tests/
    test_converter.py
```

## Usage

Install the package in editable mode and run the converter:

```bash
pip install -e .
python scripts/run.py path/to/dialogue.json -o output.rpy
```

Run the test suite with:

```bash
pytest
```

# SceneGen (JSON → Ren'Py scenes)

Утилита без внешних зависимостей:
- Валидирует JSON сцен (фоновые слои + хотспоты).
- Генерирует `.rpy` экраны/лейблы для Ren'Py.

## Установка/запуск

### Через виртуальное окружение

```bash
./setup.sh                       # создаёт .venv и ставит зависимости
./run.sh --in examples/scenes.json --out-dir /path/to/your/renpy/game
```

Способ 1 (одним файлом):
```bash
python -m scenegen.cli --in examples/scenes.json --out-dir /path/to/your/renpy/game
```

Способ 2 (как пакет локально):
```bash
    pip install -e .  # (опционально, если добавите setup.py)
    scenegen --in examples/scenes.json --out-dir /path/to/your/renpy/game
```

## Пакетная генерация

В репозитории есть скрипты `generate.sh` (Linux/macOS) и `generate.bat`
(Windows), которые обрабатывают все `.json` из директории `input` и кладут
результат в `output`:

```bash
cp examples/scenes.json input/
./generate.sh       # или generate.bat на Windows
```

## Что генерируется
- `_gen/scene_helpers.rpy` — тултипы и внутренний редирект для `go_scene`.
- `_gen/scene_<id>.rpy` — экран `scene_<id>()` + `label show_<id>`.

## Ограничения и заметки
- Многоугольники и круги кликаются по ограничивающему прямоугольнику (упрощение UX).
- Пунктирная рамка заменена тонкой сплошной линией (в Ren'Py нет нативного "dash" для границы).
- `enter_transition`/`action.transition` поддерживаются частично (fade/dissolve/slide*).

## Пример JSON
Смотрите `examples/scenes.json`.

