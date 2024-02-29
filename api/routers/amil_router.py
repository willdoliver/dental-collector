from fastapi import APIRouter, Depends
from ..dependencies import get_token_header
from api.controllers.amil_controller import AmilController

amil_controller = AmilController()

router = APIRouter(
    prefix="/amil",
    tags=["amil"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found my dear"}},
)

@router.get("/get_dentistas/")
async def get_dentistas():
    return amil_controller.get_dentistas_amil()

@router.get("/find_dentistas/")
async def find_dentistas():
    return amil_controller.find_dentistas_from_amil()