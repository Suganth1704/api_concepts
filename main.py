from fastapi import FastAPI
from app.routes import api
from app.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.include_router(api.router, prefix='/api/v1')
