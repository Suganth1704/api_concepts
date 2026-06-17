from fastapi import FastAPI
from app.routes import api
from app.config import get_settings
from app.middleware.rate_limit import setup_rate_limiting
from app.db.client import connect_to_mongo, close_mongo

settings = get_settings()
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

@app.on_event("startup")
def startup():
    setup_rate_limiting(app)
    connect_to_mongo(app)

@app.on_event("shutdown")
def shutdown():
    close_mongo()

app.include_router(api.router, prefix='/api/v1')
