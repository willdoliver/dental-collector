from fastapi import APIRouter, Depends
from ..dependencies import get_token_header
from api.controllers.etl_controller import ETLController

etl_controller = ETLController()

router = APIRouter(
    prefix="/migration",
    tags=["migration"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found my dear"}},
)

@router.get("/create_tables/")
async def create_tables():
    return etl_controller.create_tables()

@router.get("/sync_data/")
async def sync_data():
    return etl_controller.sync_data()

@router.get("/clone_database/")
async def clone_database():
    return etl_controller.clone_database()