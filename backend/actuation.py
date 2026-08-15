from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from models import ActuationLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_shutdown_command(db: AsyncSession, line_id: int, user: dict) -> str:
    """
    Simulates sending a SCADA breaker trip command to de-energize a transmission line segment.
    Logs the actuation action in the database.
    """
    user_id = user.get("id") if user else "anonymous"
    timestamp = datetime.utcnow().isoformat()

    logger.info(f"SCADA Command: Initiating breaker trip for line_id={line_id} triggered by user={user_id}")

    # Create actuation log
    log_entry = ActuationLog(
        line_id=line_id,
        user_id=user_id,
        action="shutdown",
        status="sent",
        timestamp=timestamp
    )
    
    db.add(log_entry)
    await db.commit()

    detail_message = (
        f"De-energize command dispatched to line ID {line_id}. "
        "SCADA breakers opened successfully. Busbar potential verified at 0.0kV."
    )
    return detail_message
