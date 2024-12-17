from fastapi import APIRouter, Depends, HTTPException

from app.api import deps
from app.core.logging import get_logger
from app.models.user import User
from app.services.ghibli import GhibliService

router = APIRouter()
logger = get_logger(__name__)


@router.get("/")
async def get_ghibli_data(current_user: User = Depends(deps.get_current_active_user)):
    """
    Obtiene datos de Studio Ghibli API según el rol del usuario
    """
    logger.info(
        f"Fetching Ghibli data for user: {current_user.username} with role: {current_user.role}"
    )

    try:
        data = GhibliService.get_data_by_role(current_user.role)
        return data
    except Exception as e:
        logger.error(f"Error fetching Ghibli data: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error fetching Ghibli data"
        )