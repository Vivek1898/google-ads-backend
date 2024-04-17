# app/routes/campaign_routes.py
from fastapi import APIRouter, HTTPException, Depends , Header
from middlewares.middlewares import auth_middleware

from controllers.ad_group_controllers import create_ad_group ,list_ad_groups
router = APIRouter()

@router.post("/adGroup/create")
async def create_ad_group_route(
        authorization: str = Header(None),
        ad_group_data: dict = None
):
    print(authorization)
    ad_group =  create_ad_group(authorization , ad_group_data)
    return ad_group


@router.post("/adGroup/list")
async def list_ad_groups_route(
        authorization: str = Header(None),
        ad_group_data: dict = None
):
    ad_groups = list_ad_groups(authorization , ad_group_data)
    return ad_groups