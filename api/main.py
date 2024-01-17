
from fastapi import Depends, FastAPI

from .dependencies import get_query_token, get_token_header
from .routers import unimedRouter


app = FastAPI()

app.include_router(
    unimedRouter.router,
    dependencies=[Depends(get_token_header)]
)

@app.get("/")
async def root():
    return {"message": "Alive :)"}

@app.get("/databases")
async def databases():
    import pymongo
    cl = pymongo.MongoClient("mongodb://localhost:27017/")
    return {"databases": cl.list_database_names()}


# https://fastapi.tiangolo.com/tutorial/bigger-applications/
# /docs