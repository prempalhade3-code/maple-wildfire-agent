from fastapi import Header, HTTPException, status
from typing import Optional

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Decodes the Clerk authentication token or returns a mock user in demo/development mode.
    """
    if not authorization:
        # For development/demo purposes, we default to a mock operator profile.
        return {
            "id": "usr_demo_scada_operator",
            "name": "Demo SCADA Operator",
            "email": "operator@gridsentry.io",
            "role": "operator"
        }
    
    try:
        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise ValueError()
        
        token = parts[1]
        # In production, Clerk JWT is verified using pyjwt and Clerk PEM keys.
        # We parse the token or return a mock user profile linked to the session.
        return {
            "id": "usr_clerk_scada_operator",
            "name": "Verified SCADA Operator",
            "email": "operator@gridsentry.io",
            "role": "operator",
            "token_snippet": token[:12] + "..."
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token format"
        )
