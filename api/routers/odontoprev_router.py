from fastapi import APIRouter, Depends
from ..dependencies import get_token_header
from api.controllers.odontoprev_controller import OdontoprevController

odontoprev_controller = OdontoprevController()

router = APIRouter(
    prefix="/odontoprev",
    tags=["odontoprev"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found my dear"}},
)

@router.get("/get_dentistas/")
async def get_dentistas():
    return odontoprev_controller.get_dentistas_odontoprev()

@router.get("/find_dentistas/")
async def find_dentistas():
    return odontoprev_controller.find_dentistas_from_odontoprev()

