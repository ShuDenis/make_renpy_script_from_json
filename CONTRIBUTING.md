# Contributing

## Branching scheme

- `main` – stable release branch.
- `develop` – integration branch for upcoming releases.
- `release/X.Y` – preparation branches for version X.Y. Merged into `main` and `develop` at release.
- `feature/<name>` – feature development off `develop`.
- `fix/<name>` – bug fixes targeting `develop`.
- `core/<name>` – changes to core functionality.
- `hotfix/<name>` – urgent fixes off `main`, merged back into `main` and `develop`.

## Versioning

This project follows [Semantic Versioning](https://semver.org/) (SemVer).
Releases are tagged as `vX.Y.Z`. Pre-releases use suffixes like:

- `-alpha.N`
- `-beta.N`
- `-rc.N`

## Changelog

- Add changelog fragments under `changelog/unreleased/*.md` as part of each change.
- During a release, fragments are combined into `changelog/vX.Y.Z.md`.
- Update `CHANGELOG.md` to reference the new release file.
## Core workflow и релизы

Зачем: крупные пласты работы (core) живут отдельно и не обязаны попадать в ближайший релиз. Мы интегрируем только выбранные из них.

Долгоживущая ветка core: `core/<codename>`

Интеграционная «песочница» на цикл релиза: `int/core/<codename>` (одноразовая)

Зависимые фичи базируем на соответствующей `int/core/<codename>`

### Как готовить core к включению в релиз

Создать интеграционную ветку от актуального `develop`:

```bash
git checkout -B int/core/<codename> origin/develop
git merge --no-ff origin/core/<codename> -m "Integrate core/<codename>"
```

Разрулить конфликты и добавить необходимые фиксы только в `int/core/<codename>`.

Открыть PR: `int/core/<codename>` → `develop` (см. чек-лист PR ниже).

Если core не выбран в релиз — PR не мержим; ветку `int/core/...` закрываем и при необходимости пересоздаём в следующем цикле.

### Фичи, зависящие от core

Создавать от `int/core/<codename>`:

```bash
git checkout -b feature/<slug> origin/int/core/<codename>
# по завершении — PR feature → int/core/<codename>
```

### После релиза

Синхронизация потока разработки:

```bash
# после merge release → main
git checkout develop
git merge --no-ff origin/main -m "Sync from main after release"
git push
```

Обновить активные core на новую базу `develop`:

Вариант A — rebase (линейная история, если мало соавторов):

```bash
git checkout core/<codename>
git pull --ff-only
git rebase origin/develop
git push --force-with-lease
```

Вариант B — merge (если много соавторов, без переписывания истории):

```bash
git checkout core/<codename>
git pull --ff-only
git merge --no-ff origin/develop -m "Sync core/<codename> with develop"
git push
```

Далее на новый цикл снова создаём `int/core/<codename>` от свежего `develop` и открываем PR в `develop`.

## Release flow (alpha/beta/rc)

Релизная ветка: `release/X.Y` (создаётся от `develop`, когда выбран набор изменений).

В `release/X.Y` принимаются только багфиксы.

Пре-релизы — теги на ветке `release/X.Y`:

- `vX.Y.0-alpha.N` — ранние сборки;
- `vX.Y.0-beta.N` — фичи заморожены, шлифуем баги;
- `vX.Y.0-rc.N` — release candidate ("почти релиз"): если критичных багов нет, превращается в финальный релиз без суффикса.

Финал: PR `release/X.Y` → `main` (squash), затем тег `vX.Y.0` на `main` и обратная синхронизация `main` → `develop`.

Примеры:

```bash
# срез релиза
git checkout -b release/1.6 develop

# пререлизы
git tag -a v1.6.0-alpha.1 -m "1.6 alpha 1" && git push --tags
git tag -a v1.6.0-beta.1  -m "1.6 beta 1"  && git push --tags
git tag -a v1.6.0-rc.1    -m "1.6 RC1"     && git push --tags

# финальный релиз (после merge PR release/1.6 → main)
git tag -a v1.6.0 -m "1.6.0" && git push --tags
```

## Hotfix flow

Срочный фикс: `hotfix/<slug>` от `main` → PR в `main` → тег `vX.Y.Z+1`.

Обязательно вернуть изменения в `develop` (и в актуальную `release/*`, если она ещё открыта):

```bash
git checkout develop
git merge --no-ff origin/main -m "Back-merge hotfix"
git push
```

## Branch naming

Разрешённые паттерны:

- `core/<codename>`
- `int/core/<codename>`
- `feature/<slug>`
- `fix/<slug>`
- `release/X.Y`
- `hotfix/<slug>`

Правила:

- только `a-z0-9-_.`, без пробелов; длина ≤ 40 символов;
- коротко и по делу: `core/scene-gen`, `feature/textwrap-import`, `fix/windows-bash`.

## Commit messages

Используем Conventional Commits (или эквивалент внутренних правил):

```
feat: краткое описание новой возможности
fix: исправление …
docs: обновить документацию …
refactor: …
chore: …
```

В PR сливаем через squash, чтобы история `develop/main` оставалась чистой.

## Pull Requests — чек-лист

В каждом PR указываем:

- цель и контекст (что включаем/исключаем);
- список изменений по пунктам;
- как проверить (шаги/команды);
- ссылки на задачи/issue;
- метки: тип (feature/fix/docs/…), область (area/*), breaking changes.

База PR:

- `feature/*` → `develop` (или → `int/core/<codename>`, если зависит от core);
- `int/core/*` → `develop`;
- `release/X.Y` → `main`;
- `hotfix/*` → `main`.

Все PR проходят CI.

## Репозиторные настройки (для мейнтейнеров)

Автоудаление веток после merge:

Settings → General → Pull Requests → включить *Automatically delete head branches*.

Удаляется только ветка-источник PR на GitHub; PR и история остаются. Кнопка *Restore branch* доступна.

### Защита веток (Branch protection rules)

**main**

- Require pull request before merging (1–2 approvals)
- Require status checks to pass (CI)
- (опц.) Require branches to be up to date
- Disallow force pushes & deletions
- В Merge options оставить только Squash merge

**develop**

- Прямые пуши разрешены (для бота/интеграции), но удаление запрещено
- (опц.) Restrict who can push — добавить Codex/бота/команду
- (опц.) Включить базовые статус-чеки

**release/***

- Require PR, Require status checks
- Удаление запрещено (ветки релизов сохраняем)

Автоудаление не затронет `main`, `develop` и `release/*` благодаря защите; временные `feature/*` и `fix/*` будут очищаться автоматически.
