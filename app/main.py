"""Module to invoke api"""
from fastapi import FastAPI
#from app.api.api_v1.api import router as api_router

# add openapi_prefix="/dev" to fix docs in api getway
app = FastAPI()


@app.get("/")
async def root():
    """root endpoint"""
    return {"mesage": "Welcome to Cats API"}


#app.include_router(api_router, prefix="/api/v1")
