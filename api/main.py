
from fastapi import Depends, FastAPI

from .dependencies import get_query_token, get_token_header
from .routers.unimed_router import *
from .routers.metlife_router import *
from .routers.amil_router import *
from .routers.uniodonto_router import *
from .routers.odontoprev_router import *

app = FastAPI()

app.include_router(
    router,
    dependencies=[Depends(get_token_header)]
)

@app.get("/")
async def root():
    return {"status": True, "message": "Alive :)"}

@app.get("/databases")
async def databases():
    import pymongo
    cl = pymongo.MongoClient("mongodb://localhost:27017/")
    return {"databases": cl.list_database_names()}


# https://fastapi.tiangolo.com/tutorial/bigger-applications/
# /docs