from fastapi import APIRouter


from flou.conf import settings
from flou.engine.router import router as engine_router
from flou.experiments.router import router as experiments_router
from flou.datasets.router import router as datasets_router

router = APIRouter()

router.include_router(engine_router)
router.include_router(experiments_router, prefix="/experiments")
router.include_router(datasets_router, prefix="/datasets")


@router.get("/example")
def read_example():
    return {
        "message": "Hello, World!",
        "engine": settings.old_database.engine,
    }
