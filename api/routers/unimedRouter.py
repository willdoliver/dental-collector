from fastapi import APIRouter
from api.unimed import *
from api.search_points import *
from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_token_header

router = APIRouter(
    prefix="/unimed",
    tags=["unimed"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found my dear"}},
)

@router.get("/get_dentistas/")
async def get_dentistas():
    return [{"username": "Rick"}, {"username": "Morty"}]

@router.get("/get_dentista/")
async def get_dentista():
    return [{"username": "Rick"}]

@router.get("/find_dentistas")
async def find_dentistas():
    get_dentistas_from_unimed_odonto()
    return {"search": "done"}


@router.get("/get_search_ponts")
def get_search_ponts():
    get_brazil_search_points()