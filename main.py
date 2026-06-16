from fastapi import FastAPI
from app.routes import api
from app.config import get_settings
from app.middleware.rate_limit import setup_rate_limiting

settings = get_settings()
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

setup_rate_limiting(app)

app.include_router(api.router, prefix='/api/v1')
