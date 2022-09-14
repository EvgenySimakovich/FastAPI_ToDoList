from fastapi import APIRouter

from .tasks import router as tasks_router
from .auth import router as auth_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(tasks_router)

