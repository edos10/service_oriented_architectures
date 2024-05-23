from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from src.usecase.usecase import *
from src.repo.repository import Repository
from src.usecase.password import gen_token

import json

main_router = APIRouter()


@main_router.post('/register')
async def register_new_user(request: Request):
    input = await request.body()
    if not input:
        return JSONResponse(content={"message": "invalid input data"}, status_code=400)
    data_input = defaultdict(str, json.loads(input))
    
    try:
        await add_new_user(data_input)
    except ValueError as e:
        raise HTTPException(400, {"message": str(e)})
    
    token = gen_token()
    await add_token(token)

    return JSONResponse(content={"token": token}, status_code=200)


@main_router.patch("/update")
async def update_data_user(request: Request):
    pass


@main_router.post("/auth")
async def auth_user(request: Request):
    input = await request.body()
    if not input:
        return JSONResponse(content={"message": "invalid input data"}, status_code=400)
    data_input = defaultdict(str, json.loads(input))



@main_router.get('/get')
async def get_users():
    print("AAAAAA")
    values = await Repository().get_users()
    print(values)
    return values