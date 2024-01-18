from fastapi import APIRouter
from api.controllers.unimed_controller import UnimedController
from api.controllers.search_points import *
from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_token_header

unimed_controller = UnimedController()

router = APIRouter(
    prefix="/unimed",
    tags=["unimed"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found my dear"}},
)

@router.get("/get_dentistas/")
async def get_dentistas():
    return unimed_controller.get_dentistas_unimed()

@router.get("/get_dentista/{cro_num}/{cro_uf}")
async def get_dentista(cro_num, cro_uf):
    return unimed_controller.get_dentista_unimed(cro_num, cro_uf)

@router.get("/find_dentistas")
async def find_dentistas():
    return unimed_controller.get_dentistas_from_unimed_odonto()

@router.get("/get_search_ponts")
def get_search_ponts():
    get_brazil_search_points()