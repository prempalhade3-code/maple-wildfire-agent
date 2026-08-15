# Maple: Autonomous Wildfire Grid-Safety Agent

Maple is an agentic wildfire grid-safety platform designed to prevent power line-ignited forest fires. By integrating real-time weather analytics from Open-Meteo with physical-world intelligence from Mireye, it identifies wildfire risks at a granular, span-level prototype, enabling targeted protective recommendations instead of county-wide power shutoffs.

---

## 📋 The One-Pager Pitch

### 1. What problem are we solving?
High-voltage transmission lines clashing with tree branches during wind storms are the leading cause of catastrophic wildfires (e.g., California's Camp Fire). Today, utility operators execute massive "Public Safety Power Shutoffs" (PSPS) across entire counties, leaving thousands of customers, businesses, and hospitals in the dark.

**Maple solves this by tracking wildfire ignition risk at a granular, span-level prototype, allowing utilities to identify the line context that needs attention while keeping the rest of the grid powered.**

### 2. What "weird" combination of datasets are we using?
We combine **Mireye's physical-world intelligence** (soil conditions, vegetation canopy, terrain slope, and nearby structures) with **live weather telemetry** from Open-Meteo. Maple aligns the changing atmosphere with the physical context around an electric line, then produces an explainable protective recommendation.

### 3. Who is the buyer?
The buyers are **electric utilities** and their wildfire-mitigation, grid-operations, and risk-management teams. They need a better basis for targeted protective decisions than broad Public Safety Power Shutoffs.

---

## 🛠️ System Architecture

Maple is built as a modular, containerized web application with a true **Autonomous Agent Loop**:

1. **Autonomous Safety Agent**: A background worker process inside the FastAPI app that scans monitored line locations every 45 seconds, analyzes physical and weather metrics, reasons about wildfire threat levels, and makes a simulated protective recommendation if the risk score crosses 70%.
2. **Frontend**: Next.js (React + TypeScript) + Tailwind CSS dashboard with an animated field map, an evidence briefing, risk drivers, recommendation, and audit timeline.
3. **Backend API**: FastAPI (Python) web server providing REST endpoints for checking risks and running a simulated protective action.
4. **Database**: PostgreSQL with PostGIS extension (`postgis/postgis:15-3.4-alpine`) storing demonstration line paths, risk logs, and simulated actuation records.

---

## 🚀 Setup & Execution

### Prerequisite: Ensure Docker Desktop is Running
Make sure Docker Desktop is launched and the docker socket is responsive.

### 1. Configure live Mireye access
Copy the example environment file and add your Mireye API token. Do not commit `.env`.
```bash
cp .env.example .env
```

Set `MIREYE_API_TOKEN` in `.env`, then start the Docker Compose stack from the project root:
```bash
docker compose up -d --build
```
The backend now creates its own PostGIS tables and seeds its four demo spans at startup.

### 2. Launch the Frontend Dev Server
Navigate to the frontend folder, install packages, and start Next.js:
```bash
cd frontend
npm install
npm run dev
```
The client dashboard will start up at **http://localhost:3000**.

For a deployed or remote API, copy `frontend/.env.local.example` to
`frontend/.env.local` and set `NEXT_PUBLIC_API_URL` to that API's URL.

### 3. Verify the services
```bash
curl http://localhost:8000/lines
curl http://localhost:8000/risk/1
```

The Meet Maple page also has a clearly labelled **Run severe-weather demo** control. It uses simulated extreme conditions so the protective-action path can be demonstrated reliably; normal mode continues to use live weather.

---

## ⚡ Interactive Dashboard & SCADA Simulation

1. **Dashboard Overview**: Open **http://localhost:3000** in your browser.
2. **Geospatial Scans**: Click on the **Big Sur Forest Span** node on the interactive SVG map. Notice the live Open-Meteo wind forecasts and Mireye soil moisture metrics loading. The warning badge flashes crimson to indicate a critical risk.
3. **Emergency Isolation**: Click the **TRIGGER EMERGENCY SHUTDOWN** button:
   - A modal progress window will initiate to display real-time SCADA breaker trip handshakes.
   - HTML5 web audio alerts will emit warning sound tones directly in the browser.
   - Once the handshake is complete, the map active node and transmission lines turn green (safe/de-energized), the threat dials drop to 0%, and de-energization confirmation logs are appended to the scrolling safety ticker.
