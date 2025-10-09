# Bidder Backend

This FastAPI service powers the Bidder estimating platform. It exposes a public API that
accepts job parameters, enriches them with data from free APIs, and persists normalized bid
records using SQLModel.

## Getting Started

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

Configuration lives in `.env`. The following environment variables are supported:

- `GEOAPIFY_KEY`
- `OPENWEATHER_API_KEY`
- `BLS_API_KEY`

The API is served under `/api/v1`. Use the interactive docs at `/docs` for exploration.
