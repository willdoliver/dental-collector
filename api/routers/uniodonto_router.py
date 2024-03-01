from fastapi import APIRouter, Depends
from ..dependencies import get_token_header
from api.controllers.uniodonto_controller import UniodontoController

uniodonto_controller = UniodontoController()

router = APIRouter(
    prefix="/uniodonto",
    tags=["uniodonto"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found my dear"}},
)

@router.get("/get_dentistas/")
async def get_dentistas():
    return uniodonto_controller.get_dentistas_uniodonto()

@router.get("/find_dentistas/")
async def find_dentistas():
    return uniodonto_controller.find_dentistas_from_uniodonto()