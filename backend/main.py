from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import LineString
from typing import List, Optional
import asyncio
import logging

import models
import database
import schemas
import risk_engine
import actuation
import auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Maple Backend", version="0.1.0")

# CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
async def get_db():
    async with database.async_session() as session:
        yield session

# Autonomous Grid Safety Agent - Periodic Loop
async def monitor_grid_loop():
    """
    Autonomous background agent loop.
    Reasons about live weather + Mireye land factors to calculate wildfire threat levels.
    Decides and automatically acts (dispatches SCADA line isolation orders) when risk threshold is crossed.
    """
    logger.info("Initializing Maple Autonomous Grid Safety Agent loop...")
    await asyncio.sleep(5) # Let database connections stabilize
    
    # Auto-seed on startup if needed
    try:
        async with database.async_session() as db:
            lines = await models.get_all_lines(db)
            if not lines:
                logger.info("Database empty on startup. Triggering auto-seeding...")
                await seed_database_helper(db)
    except Exception as e:
        logger.error(f"Startup auto-seeding failed: {e}")

    while True:
        try:
            async with database.async_session() as db:
                lines = await models.get_all_lines(db)
                for line in lines:
                    # 1. Check if line has already been de-energized
                    log_result = await db.execute(
                        select(models.ActuationLog)
                        .filter(models.ActuationLog.line_id == line.id, models.ActuationLog.action == "shutdown")
                        .order_by(models.ActuationLog.timestamp.desc())
                        .limit(1)
                    )
                    latest_log = log_result.scalar_one_or_none()
                    if latest_log and latest_log.status == "sent":
                        # Already secured by operator or agent, skip
                        continue
                    
                    # 2. Query and compute threat level
                    logger.info(f"Agent scanning Grid Node: {line.name}...")
                    risk_data = await risk_engine.compute_risk_for_line(db, line)
                    
                    # 3. Decision threshold: If risk score > 70% (high hazard)
                    if risk_data["score"] > 70.0:
                        logger.warning(f"AUTO-RELAY: Critical Wildfire Threat ({risk_data['score']}%) on {line.name}! Dispatched breaker trip.")
                        auto_user = {"id": "auto_safety_relay", "name": "Maple Protective Relay"}
                        await actuation.send_shutdown_command(db, line.id, auto_user)
        except Exception as e:
            logger.error(f"Error in autonomous monitoring agent iteration: {e}")
            
        await asyncio.sleep(45) # Run safety checks every 45 seconds

@app.on_event("startup")
async def startup_event():
    # A new Docker volume must be usable immediately, without manual migrations.
    async with database.engine.begin() as connection:
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await connection.run_sync(models.Base.metadata.create_all)
    # Spin up autonomous grid monitoring agent task in background.
    asyncio.create_task(monitor_grid_loop())

@app.get("/lines", response_model=List[schemas.TransmissionLineOut])
async def list_lines(db: AsyncSession = Depends(get_db)):
    return await models.get_all_lines(db)

@app.get("/lines/geojson")
async def get_lines_geojson(db: AsyncSession = Depends(get_db)):
    """
    Returns transmission lines formatted as a GeoJSON FeatureCollection.
    """
    lines = await models.get_all_lines(db)
    features = []
    for line in lines:
        shape = to_shape(line.geom)
        coords = list(shape.coords)
        features.append({
            "type": "Feature",
            "id": line.id,
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            },
            "properties": {
                "name": line.name,
                "voltage_kv": line.voltage_kv
            }
        })
    return {
        "type": "FeatureCollection",
        "features": features
    }

@app.get("/risk/{line_id}", response_model=schemas.RiskScoreOut)
async def risk_for_line(line_id: int, scenario: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    line = await models.get_line_by_id(db, line_id)
    if not line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line not found")
    if scenario not in (None, "severe"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown demo scenario")
    return await risk_engine.compute_risk_for_line(db, line, scenario=scenario)

@app.post("/actuate/{line_id}", response_model=schemas.ActuationResponse)
async def actuate_line(line_id: int, scenario: Optional[str] = None, db: AsyncSession = Depends(get_db), user: dict = Depends(auth.get_current_user)):
    # Verify line exists
    line = await models.get_line_by_id(db, line_id)
    if not line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line not found")
    
    if scenario not in (None, "severe"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown demo scenario")

    risk = await risk_engine.compute_risk_for_line(db, line, scenario=scenario, persist=False)
    if risk["score"] < 70:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Protective simulation requires risk of at least 70%; current risk is {risk['score']}%."
        )

    # Send a simulated breaker trip command and log it.
    result = await actuation.send_shutdown_command(db, line_id, user)
    return {"status": "sent", "detail": result}

async def seed_database_helper(db: AsyncSession):
    # Define seed data with coordinates (Lng, Lat for PostGIS/Shapely standard)
    seed_data = [
        {
            "id": 1,
            "name": "Big Sur Forest Span (Monterey County)",
            "voltage_kv": 500.0,
            "coords": [(-121.8081, 36.2704), (-121.7881, 36.2504)]
        },
        {
            "id": 2,
            "name": "Santa Rosa Foothills Span (Sonoma County)",
            "voltage_kv": 115.0,
            "coords": [(-122.6801, 38.4404), (-122.6601, 38.4204)]
        },
        {
            "id": 3,
            "name": "Calistoga Valley Span (Napa County)",
            "voltage_kv": 230.0,
            "coords": [(-122.5801, 38.5804), (-122.5601, 38.5604)]
        },
        {
            "id": 4,
            "name": "San Francisco Downtown Span (Urban/Non-Forest)",
            "voltage_kv": 12.0,
            "coords": [(-122.4194, 37.7749), (-122.3994, 37.7549)]
        }
    ]

    for data in seed_data:
        line_geom = from_shape(LineString(data["coords"]), srid=4326)
        line = models.TransmissionLine(
            id=data["id"],
            name=data["name"],
            voltage_kv=data["voltage_kv"],
            geom=line_geom
        )
        db.add(line)

    await db.commit()

@app.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_database(db: AsyncSession = Depends(get_db)):
    """
    Seeds the database with four key transmission line nodes in California if empty.
    """
    existing_lines = await models.get_all_lines(db)
    if existing_lines:
        return {"status": "already_seeded", "count": len(existing_lines)}

    await seed_database_helper(db)
    return {"status": "seeded", "count": 4}
