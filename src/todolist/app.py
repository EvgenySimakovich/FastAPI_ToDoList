from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .settings import settings
from .api import router

app = FastAPI()
app.include_router(router)

app.mount('/static', StaticFiles(directory=settings.static_dir), name='static')
