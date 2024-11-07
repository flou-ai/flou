from fastapi import APIRouter


from flou.conf import settings
from flou.engine.router import router as engine_router
from flou.experiments.router import router as experiments_router

router = APIRouter()

router.include_router(engine_router)
router.include_router(experiments_router, prefix="/experiments")


@router.get("/example")
def read_example():
    return {
        "message": "Hello, World!",
        "engine": settings.old_database.engine,
    }
