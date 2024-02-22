from fastapi import APIRouter, Depends
from api.controllers.metlife_controller import MetLifeController
from ..dependencies import get_token_header

metlife_controller = MetLifeController()

router = APIRouter(
    prefix="/metlife",
    tags=["metlife"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found my dear"}},
)

@router.get("/get_dentistas/")
async def get_dentistas():
    return metlife_controller.get_dentistas_metlife()

@router.get("/find_dentistas/")
async def find_dentistas():
    return metlife_controller.find_dentistas_from_metlife()