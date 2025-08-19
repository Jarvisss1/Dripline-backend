# backend/app/auth.py

from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
import jwt # <-- Use the PyJWT library consistently
from jwt import PyJWKClient, InvalidTokenError
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user_id(token: str = Security(oauth2_scheme)) -> str:
    """Validates Clerk JWT and returns the user ID."""
    if not settings.CLERK_ISSUER_URL:
        raise HTTPException(status_code=500, detail="Clerk issuer URL not configured")
    try:
        jwks_url = f"{settings.CLERK_ISSUER_URL}/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)
        
        # Get the signing key from the token's header
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Decode the token using the PyJWT library
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.CLERK_ISSUER_URL,
            options={"verify_signature": True, "verify_aud": False} # aud claim is not standard
        )
        return payload["sub"]  # "sub" claim is the user ID
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {e}")
