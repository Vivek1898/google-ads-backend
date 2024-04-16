# app/routes/campaign_routes.py
from fastapi import APIRouter, HTTPException, Depends , Header
from middlewares.middlewares import auth_middleware

from controllers.campaign_controller import get_campaigns, create_campaigns

router = APIRouter()

@router.post("/campaigns/list" )
async def get_campaigns_route(
        authorization: str = Header(None),
        camp_data: dict = None
):
    print(authorization)
    campaigns = await get_campaigns(authorization , camp_data)
    return campaigns

#add middleware to the route
@router.post("/campaigns")
async def create_campaign_route(
        authorization: str = Header(None),
        camp_data: dict = None ):
    try:
        created_campaign = create_campaigns(
            authorization, camp_data
        )
        return created_campaign
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
