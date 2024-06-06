from fastapi import Depends, HTTPException, APIRouter

router = APIRouter()


@router.get("/")
async def get_company_name():
    return {"company_name": "company_name 1"}


@router.get("/employees/")
async def get_number_of_employees():
    return {"number_of_employees": 100}
