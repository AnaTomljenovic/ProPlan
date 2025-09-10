from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from proplan.custom_models import Token
from proplan.database import get_session
from proplan.managers.auth_manager import AuthManager


router = APIRouter(prefix="/auth", tags=["auth"])
auth_manager = AuthManager()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    token = await auth_manager.authenticate(session, form_data.username, form_data.password)
    return {"access_token": token, "token_type": "bearer"}
