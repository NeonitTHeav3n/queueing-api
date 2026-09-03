# Queueing Theory API

REST API для расчёта характеристик систем массового обслуживания: вычисляет стационарные метрики очередей **M/M/1** и **M/D/1** (аналитически и методом Монте-Карло) и хранит историю расчётов в базе данных. Продолжает тему репозитория `queueing-theory-simulation` — та же предметная область, но уже как серверное приложение.

> **Abstract (EN):** A FastAPI-based REST service that computes steady-state metrics (E[N], E[T], E[W], E[Q]) of M/M/1 and M/D/1 queues — both in closed form and via Monte-Carlo simulation — and persists calculation history in a database. Includes Pydantic validation, SQLAlchemy models, unit tests, Docker and CI.

## Возможности

- **Закрытые формулы** для M/M/1 и M/D/1 (Бочаров, Печинкин, «Теория массового обслуживания», стр. 110–114).
- **Монте-Карло симуляция** (векторизованная, детерминированная по seed) с оценкой E[N], E[T], E[W], E[Q].
- **Валидация входных данных** через Pydantic (0 < ρ < 1, μ > 0).
- **История расчётов**: CRUD-эндпоинты поверх SQLite (SQLAlchemy 2.0).
- **Автодокументация**: интерактивный Swagger UI на `/docs` и ReDoc на `/redoc`.
- **Тесты** (pytest + httpx), **Docker** и **CI** (GitHub Actions, Python 3.10–3.12).

## Endpoints

| Метод | Путь | Описание |
|---|---|---|
| GET | `/health` | Проверка живости |
| GET | `/` | Инфо об API |
| GET | `/queues/mm1?rho=0.7&mu=1` | Аналитические метрики M/M/1 |
| GET | `/queues/md1?rho=0.7&mu=1` | Аналитические метрики M/D/1 |
| POST | `/queues/simulate` | Аналитика + опционально Монте-Карло |
| POST | `/calculations` | Сохранить расчёт в историю |
| GET | `/calculations` | Список расчётов |
| GET | `/calculations/{id}` | Один расчёт |
| DELETE | `/calculations/{id}` | Удалить расчёт |

Пример запроса и ответа:

```bash
curl "http://127.0.0.1:8000/queues/mm1?rho=0.7&mu=1.0"
```

```json
{
  "queue_type": "mm1",
  "rho": 0.7,
  "mu": 1.0,
  "E_N": 2.3333333333333335,
  "E_T": 3.3333333333333335,
  "E_W": 2.3333333333333335,
  "E_Q": 1.6333333333333335
}
```

Симуляция:

```bash
curl -X POST "http://127.0.0.1:8000/queues/simulate" \
     -H "Content-Type: application/json" \
     -d '{"queue_type": "md1", "rho": 0.7, "method": "simulation", "seed": 42}'
```

Сохранение в историю:

```bash
curl -X POST "http://127.0.0.1:8000/calculations" \
     -H "Content-Type: application/json" \
     -d '{"queue_type": "md1", "rho": 0.7}'
```

## Формулы

Обозначения: ρ = λ/μ — загрузка, μ — интенсивность обслуживания, E[N] — среднее число заявок, E[T] — время пребывания, E[W] — время ожидания, E[Q] — длина очереди.

| Величина | M/M/1 | M/D/1 |
|---|---|---|
| E[N] | ρ / (1 − ρ) | ρ + ρ² / (2(1 − ρ)) |
| E[T] | 1 / (μ(1 − ρ)) | (2 − ρ) / (2μ(1 − ρ)) |
| E[W] | ρ / (μ(1 − ρ)) | ρ / (2μ(1 − ρ)) |
| E[Q] | ρ² / (1 − ρ) | ρ² / (2(1 − ρ)) |

## Структура репозитория

```
queueing-api/
├── app/
│   ├── main.py                 # FastAPI-приложение
│   ├── db.py                   # SQLAlchemy engine/session + dependency
│   ├── models.py               # ORM-модель Calculation
│   ├── schemas.py              # Pydantic-схемы с валидацией
│   ├── calculator.py           # формулы + симуляция
│   └── routers/
│       ├── queues.py           # /queues/...
│       └── history.py          # /calculations/...
├── tests/                      # pytest-тесты (httpx TestClient)
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml              # настройки pytest
├── Dockerfile
├── .github/workflows/ci.yml    # CI на Python 3.10–3.12
├── LICENSE
└── README.md
```

## Установка и запуск

### Локально

```bash
git clone <url-репозитория>
cd queueing-api
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Откройте в браузере:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Через Docker

```bash
docker build -t queueing-api .
docker run -p 8000:8000 queueing-api
```

### Тесты

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Конфигурация

- `DATABASE_URL` — строка подключения к БД (по умолчанию `sqlite:///./queueing.db`). Можно указать PostgreSQL и другие СУБД, поддерживаемые SQLAlchemy.

## Технологии

- [FastAPI](https://fastapi.tiangolo.com/) + [Pydantic v2](https://docs.pydantic.dev/)
- [SQLAlchemy 2.0](https://www.sqlalchemy.org/) + SQLite
- [numpy](https://numpy.org/) — симуляция
- [pytest](https://docs.pytest.org/) + [httpx](https://www.python-httpx.org/)
- [Docker](https://www.docker.com/)

## Литература

- Бочаров П. П., Печинкин А. В. *Теория массового обслуживания*. — М.: Изд-во РУДН, 1995. — С. 110–114.

## Лицензия

[MIT](LICENSE)
