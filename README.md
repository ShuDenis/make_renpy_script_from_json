# SceneGen (JSON → Ren'Py scenes)

Утилита без внешних зависимостей:
- Валидирует JSON сцен (фоновые слои + хотспоты).
- Генерирует `.rpy` экраны/лейблы для Ren'Py.

## Установка/запуск

Способ 1 (одним файлом):
```bash
python -m scenegen.cli --in examples/scenes.json --out-dir /path/to/your/renpy/game
```

Способ 2 (как пакет локально):
```bash
pip install -e .  # (опционально, если добавите setup.py)
scenegen --in examples/scenes.json --out-dir /path/to/your/renpy/game
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
