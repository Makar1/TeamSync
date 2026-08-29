# TeamSync

Backend для управления командой внутри компании: пользователи, команды, задачи с комментариями и статусами, встречи с проверкой пересечений по времени, оценки работы, календарь.

## Стек

- **FastAPI** + **Pydantic** — API
- **SQLAlchemy 2.0** + **Alembic** — ORM и миграции
- **PostgreSQL** (в Docker) — БД
- **JWT** (`python-jose`) — авторизация
- **pytest** + `TestClient` — тесты, с изоляцией БД через SAVEPOINT-транзакции

## Установка и запуск

```bash
git clone <repo_url>
cd TeamSync

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
```

Скопируй `.env.example` в `.env` и при необходимости поправь значения:

```bash
cp .env.example .env        # Git Bash / Linux / macOS
# copy .env.example .env    # Windows PowerShell / cmd
```

Подними PostgreSQL:

```bash
docker-compose up -d
```

Примени миграции:

```bash
alembic upgrade head
```

Запусти сервер:

```bash
uvicorn app.main:app --port 8000
```

API доступен на `http://localhost:8000`, интерактивная документация — на `http://localhost:8000/docs`.

## Тестирование

```bash
pytest --cov=app --cov-report=term-missing
```

Каждый тест выполняется в собственной транзакции (SAVEPOINT), которая откатывается после теста — реальная БД не затрагивается, даже несмотря на то что код эндпоинтов сам вызывает `db.commit()`.

## Роли

- **`is_admin`** — глобальный флаг на пользователе (сейчас не используется в бизнес-логике, задел на будущее).
- **`member` / `manager`** — роль внутри конкретной команды (в `TeamMember`), не глобальная: один и тот же пользователь может быть менеджером в одной команде и рядовым участником в другой.

## API

Полный список параметров и тел запросов — в Swagger (`/docs`). Здесь — обзор по ресурсам.

### Auth
| Метод | Путь | Доступ |
|---|---|---|
| POST | `/auth/register` | любой |
| POST | `/auth/login` | любой |

### Users
| Метод | Путь | Доступ |
|---|---|---|
| GET | `/users/me` | залогинен |
| PATCH | `/users/me/password` | залогинен |
| GET | `/users/me/evaluations` | залогинен — свои оценки + средний балл |

### Teams
| Метод | Путь | Доступ |
|---|---|---|
| POST | `/teams/` | залогинен — создатель становится `manager` |
| POST | `/teams/{team_id}/join` | залогинен, по `invite_code` |
| GET | `/teams/{team_id}/members/` | участник команды |
| PATCH | `/teams/{team_id}/members/{user_id}/role` | `manager` |
| DELETE | `/teams/{team_id}/members/{user_id}` | `manager` |

### Tasks
| Метод | Путь | Доступ |
|---|---|---|
| POST | `/teams/{team_id}/tasks` | `manager` |
| GET | `/teams/{team_id}/tasks` | участник команды |
| GET | `/teams/{team_id}/tasks/{task_id}` | участник команды |
| PATCH | `/teams/{team_id}/tasks/{task_id}` | `manager` |
| DELETE | `/teams/{team_id}/tasks/{task_id}` | `manager` |
| PATCH | `/teams/{team_id}/tasks/{task_id}/status` | `manager` или исполнитель задачи |
| POST | `/tasks/{task_id}/comments` | участник команды, к которой относится задача |
| POST | `/tasks/{task_id}/evaluation` | `manager`, только для задач в статусе `done` с назначенным исполнителем, одна оценка на задачу |

### Meetings
| Метод | Путь | Доступ |
|---|---|---|
| POST | `/teams/{team_id}/meetings/` | участник команды — создатель автоматически становится организатором и участником |
| GET | `/teams/{team_id}/meetings` | участник команды |
| PATCH | `/teams/{team_id}/meetings/{meeting_id}` | `manager` или организатор встречи |
| DELETE | `/teams/{team_id}/meetings/{meeting_id}` | `manager` или организатор встречи |

Создание и изменение встречи проверяют пересечение по времени для **каждого** участника (включая организатора), по всем его встречам во всех командах — не только внутри текущей. При конфликте — `409`.

### Calendar
| Метод | Путь | Доступ |
|---|---|---|
| GET | `/calendar?from=...&to=...` | залогинен — свои задачи (по `due_date`) и встречи (по участию) за период |

## Архитектура

- `app/models/` — SQLAlchemy-модели (по файлу на сущность)
- `app/schemas/` — Pydantic-схемы запросов/ответов
- `app/api/` — роутеры FastAPI
- `app/services/` — вынесенная бизнес-логика: проверка пересечений встреч, вычисление среднего балла, создание/изменение встречи, создание оценки
- `app/dependencies.py` — переиспользуемые проверки (`get_current_user`, `get_team_membership`)
- `alembic/` — миграции

Простые CRUD-операции (создание/изменение команд, задач, комментариев) выполняют запросы к БД прямо в route-handler'ах, без отдельного сервис-слоя — это осознанный выбор: для операций из одного `db.query`/`db.add` дополнительная прослойка не даёт ощутимой пользы. В `services/` вынесено то, что содержит настоящую логику с ветвлением (проверка пересечений времени, агрегирующие запросы, многошаговая валидация).

## Известные ограничения (out of scope)

- **Logout** не реализован. JWT — stateless токен; полноценный logout потребовал бы отдельной инфраструктуры (blacklist токенов в БД или Redis), что выходит за рамки MVP.
