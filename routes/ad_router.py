# Ad Router
from fastapi import APIRouter, HTTPException, Depends , Header
from middlewares.middlewares import auth_middleware

from controllers.ad_controller import create_ad , list_ads

router = APIRouter()

@router.post("/ad/create")
async def create_ad_route(
        authorization: str = Header(None),
        ad_data: dict = None
):
    ad =  create_ad(authorization , ad_data)
    return ad

@router.post("/ad/list")
async def list_ads_route(
        authorization: str = Header(None),
        ad_data: dict = None
):
    ads = list_ads(authorization , ad_data)
    return ads

