from fastapi import APIRouter, HTTPException
from controllers.auth_controller import generate_token_and_jwt , access_token_login , get_linked_accounts

router = APIRouter()


@router.post("/auth")
async def genrate_auth_token(auth_data: dict):
    try:
        auth_response =  generate_token_and_jwt(auth_data)
        return auth_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/accessTokenLogin")
async def token_login(auth_data: dict):
    try:
        auth_response = access_token_login(auth_data)
        return auth_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/linkedAccounts")
async def link_accounts(auth_data: dict):
    try:
        auth_response = get_linked_accounts(auth_data)
        return auth_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))