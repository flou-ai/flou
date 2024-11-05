from fastapi import APIRouter


from flou.conf import settings

router = APIRouter()


@router.get("/example")
def read_example():
    return {
        "message": "Hello, World!",
        "engine": settings.old_database.engine,
    }
