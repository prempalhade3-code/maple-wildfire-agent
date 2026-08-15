from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class TransmissionLine(Base):
    __tablename__ = "transmission_lines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    # GeoJSON LineString stored as PostGIS geometry
    geom = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)
    voltage_kv = Column(Float, nullable=True)
    # Additional static attributes can be added later

class RiskScore(Base):
    __tablename__ = "risk_scores"
    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(Integer, nullable=False, index=True)
    score = Column(Float, nullable=False)
    probability = Column(Float, nullable=False)
    consequence = Column(Float, nullable=False)
    timestamp = Column(String, nullable=False)  # ISO timestamp

class ActuationLog(Base):
    __tablename__ = "actuation_logs"
    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(Integer, nullable=False)
    user_id = Column(String, nullable=True)  # from auth provider
    action = Column(String, nullable=False)  # e.g., "shutdown"
    status = Column(String, nullable=False)  # e.g., "sent", "failed"
    timestamp = Column(String, nullable=False)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def get_all_lines(db: AsyncSession):
    result = await db.execute(select(TransmissionLine))
    return result.scalars().all()

async def get_line_by_id(db: AsyncSession, line_id: int):
    result = await db.execute(select(TransmissionLine).filter(TransmissionLine.id == line_id))
    return result.scalar_one_or_none()
