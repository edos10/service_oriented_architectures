from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from src.usecase.usecase import *
from src.repo.repository import Repository
from src.usecase.password import gen_token
from src.models.models import *

import json

main_router = APIRouter()


@main_router.post('/register', response_model=ResponseRegister, status_code=201)
async def register_new_user(request: Request, _: NewUser):
    input_data = await request.body()
    if not input_data:
        return JSONResponse(content={"message": "invalid input data"}, status_code=400)
    data_input = defaultdict(str, json.loads(input_data))
    
    try:
        new_id = await add_new_user(data_input)
    except ValueError as e:
        raise HTTPException(400, {"message": str(e)})

    if new_id <= 0:
        raise HTTPException(500, {"message": "error in create user"})

    token = gen_token()
    await add_token(new_id, token)

    return JSONResponse(content={"token": token}, status_code=200)


@main_router.post("/auth", response_model=ResponseAuth, status_code=201)
async def auth_user(request: Request, _: AuthUser):
    input_data = await request.body()
    if not input_data:
        return JSONResponse(content={"message": "invalid input data"}, status_code=400)
    data_input = defaultdict(str, json.loads(input_data))
    if "nickname" not in data_input or "password" not in data_input:
        raise HTTPException(400, {"message": "not enough data for check user"})
    try:
        res = await check_auth_user(data_input['nickname'], data_input['password'])
    except ValueError as e:
        raise HTTPException(400, {"message": str(e)})

    if not res:
        raise HTTPException(400, {"message": "wrong password, try again!"})

    token = gen_token()

    get_id = await Repository().get_user_nick(data_input['nickname'])

    await add_token(get_id, token)

    return JSONResponse(content={"token": token}, status_code=200)


# данный метод создан для тестирования правильности работы системы
@main_router.get('/get', response_model=list[NewUser], status_code=200)
async def get_users():
    values = await Repository().get_users()
    return values


@main_router.put("/update", response_model=ResponseUpdate, status_code=200)
async def update_data_user(request: Request, _: UpdateUser):
    input_data = await request.body()
    if not input_data:
        return JSONResponse(content={"message": "no data for update"}, status_code=400)
    data_input = defaultdict(str, json.loads(input_data))
    try:
        await update_user(data_input)
    except ValueError as e:
        raise HTTPException(401, {"message": str(e)})

    return JSONResponse(content={"message": "data succesfully updated"}, status_code=200)
