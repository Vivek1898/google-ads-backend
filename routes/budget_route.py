from fastapi import APIRouter, HTTPException, Depends , Header
from controllers.budget_controller import create_budget ,list_budgets

router = APIRouter()

@router.post("/budget/create")
async def create_budget_route(
        authorization: str = Header(None),
        budget_data: dict = None ):
    try:
        created_budget = create_budget(
            authorization, budget_data
        )
        return created_budget
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/budget/list")
async def list_budgets_route(
        authorization: str = Header(None),
        budget_data: dict = None
):
    budgets = list_budgets(authorization , budget_data)
    return budgets