import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from flou.conf import settings
from flou.api.router import router

# import the app folder
sys.path.append(os.getcwd())

import app

app = FastAPI(
    title=settings.APP_NAME,
)
app.include_router(router, prefix="/api/v0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)