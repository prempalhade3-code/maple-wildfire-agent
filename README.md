# Maple

> An autonomous wildfire grid-safety prototype. Maple watches the conditions around a monitored transmission span, explains its decision, and records a **simulated** protective response when risk crosses a threshold.

**[Open the live console](https://maple-wildfire-agent.vercel.app)** · **[API](https://maple-backend-pf5l.onrender.com)**

## what is inside

- **A FastAPI safety agent** that evaluates seeded transmission spans on a 45-second loop.
- **A physical-world evidence layer** powered by Mireye: soil moisture, vegetation canopy, terrain slope, nearby structures, and cited sources.
- **Live weather ingestion** from Open-Meteo: wind speed, direction, humidity, and temperature.
- **A transparent risk engine** that returns score contributors, evidence, citations, confidence, and a recommendation.
- **A Next.js operations console** for inspecting spans, switching to a clearly labelled severe-weather demo, and viewing the decision trail.
- **PostGIS-backed audit data** for lines, calculated risks, and simulated actuation records.

## architecture

```text
                         +------------------+
                         |   Open-Meteo     |
                         | live conditions  |
                         +---------+--------+
                                   |
+------------------+               v                 +-------------------+
|      Mireye      | ------> FastAPI risk engine ----> | PostgreSQL/PostGIS |
| cited place data |          + agent loop             | risks + audit log  |
+------------------+               |                 +-------------------+
                                   v
                         +------------------+
                         |  Next.js console |
                         | evidence → action|
                         +------------------+
```

### request flow

1. The frontend requests a selected span from the API.
2. The risk engine fetches Open-Meteo conditions and a Mireye location scan concurrently.
3. The engine calculates ignition probability and consequence, then derives a 0–100 risk score.
4. The response contains evidence, data sources, timestamps, cited datasets, score contributors, confidence, and a recommendation.
5. Scores above `70` can produce a **simulated** isolation record. No real grid equipment is contacted.

The backend also evaluates seeded spans every 45 seconds. The browser does **not** poll continuously; it refreshes when a user selects a span or changes the scenario.

## stack

| Layer | Implementation |
| --- | --- |
| Console | Next.js 13, React 18, TypeScript, Tailwind CSS, Framer Motion |
| API | FastAPI, Uvicorn, Pydantic, HTTPX |
| Data | PostgreSQL 15 + PostGIS, SQLAlchemy async, GeoAlchemy2 |
| Intelligence | Mireye `/v1/ask` + Open-Meteo forecast API |
| Local runtime | Docker Compose |
| Deployment | Vercel (console) + Render (API/Postgres) |

## repository map

```text
frontend/                 Next.js operator console
  pages/                  Home, platform, and operations views
  components/             Shared navigation and presentation components
  styles/                 Global and page-level styles
backend/                  FastAPI service
  main.py                 API routes, startup, seed data, agent loop
  risk_engine.py          Evidence normalization and risk calculation
  mireye_client.py        Mireye client and clearly labelled fallback data
  weather_client.py       Open-Meteo client
  actuation.py            Simulated SCADA actuation + audit logging
  models.py               PostGIS/SQLAlchemy models
docker-compose.yml        Local API + PostGIS database
```

## run locally

### prerequisites

- Docker Desktop with Compose
- Node.js 18+ and npm
- A Mireye API token for live physical-world responses

### 1. configure the backend

```bash
cp .env.example .env
```

Set your token in `.env`:

```env
MIREYE_API_TOKEN=your_mireye_token
```

Start the API and PostGIS database:

```bash
docker compose up --build
```

On first boot, Maple creates the PostGIS extension/tables and seeds four demonstration transmission spans. The API is then available at `http://localhost:8000`.

### 2. configure the console

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

`frontend/.env.local` defaults to `http://localhost:8000`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Open [http://localhost:3000](http://localhost:3000).

### 3. verify it

From the repository root:

```bash
curl http://localhost:8000/lines
curl http://localhost:8000/lines/geojson
curl http://localhost:8000/risk/1
curl -X POST "http://localhost:8000/actuate/1?scenario=severe"
```

The last command creates a simulated protective-action audit record. It is deliberately gated behind a score of at least `70`.

## API surface

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/lines` | List monitored spans |
| `GET` | `/lines/geojson` | Return spans as a GeoJSON FeatureCollection |
| `GET` | `/risk/{line_id}` | Calculate and return current evidence + risk decision |
| `GET` | `/risk/{line_id}?scenario=severe` | Run the labelled severe-weather demo |
| `POST` | `/actuate/{line_id}?scenario=severe` | Record a simulated isolation action when risk is high enough |
| `POST` | `/seed` | Seed demo spans when the database is empty |

### a note on data modes

Normal mode uses live Open-Meteo weather and calls Mireye when `MIREYE_API_TOKEN` is set. If Mireye cannot be reached or no token is configured, the service returns clearly identified local demo fallback data so the product can still be explored. The operations console exposes the current data mode and retains source/timestamp information with each response.

The severe-weather control is a labelled demonstration scenario. It uses deterministic severe conditions to make the protective-decision path reviewable regardless of the weather on demo day.

## build and test

```bash
# console production build
cd frontend
npm run build

# backend unit tests (with the Compose stack running)
cd ..
docker compose exec api pytest
```

## deploy

### console · Vercel

The Vercel project uses `frontend` as its root directory. Set this variable for both Preview and Production:

```env
NEXT_PUBLIC_API_URL=https://maple-backend-pf5l.onrender.com
```

Pushes to `main` trigger the connected Vercel deployment.

### API · Render

Deploy the `backend/` Docker service and configure:

```env
DATABASE_URL=postgresql+asyncpg://...
MIREYE_API_TOKEN=...
PORT=10000
```

The backend image honors Render's `PORT` variable and falls back to port `8000` for local Docker usage.

## safety boundary

Maple is a prototype and training/demo environment. Its SCADA workflow is simulated: it writes an audit record and never reaches real utility infrastructure. Do not use this application to control a live grid or as the sole basis for an operational safety decision.

## small disclaimer

The live answer can change with weather, source availability, and upstream API response time. That is why Maple displays evidence, timestamps, citations, and an explicit demo/fallback state instead of pretending every number is permanent.
