from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from src.usecase.usecase import *
from src.repo.repository import Repository
from src.usecase.password import gen_token
from src.models.models import *

import json

main_router = APIRouter()


@main_router.post('/register', status_code=201)
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


@main_router.post("/auth", status_code=201)
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
@main_router.get('/get', status_code=200)
async def get_users():
    values = await Repository().get_users()
    return values


@main_router.put("/update", status_code=200)
async def update_data_user(request: Request, _: UpdateUser):
    input_data = await request.body()
    input_data = json.loads(input_data.decode("utf-8").replace("'",'"'))
    
    get_id = await Repository.get_user_token(input_data['token'])

    if get_id <= 0:
        return JSONResponse(content={"message": "invalid token, try again"}, status_code=401)
    
    check_token = await Repository.check_current_token(input_data['token'], get_id)

    if not check_token:
        return JSONResponse(content={"message": "your authorization was expired, try again"}, 
                            status_code=401)
    
    if not input_data:
        return JSONResponse(content={"message": "no data for update"}, status_code=401)
    
    try:
        value = await update_user(input_data)
    except ValueError as e:
        raise HTTPException(400, {"message": str(e)})

    return JSONResponse(content={"message": "data succesfully updated", "user_data": value}, status_code=200)
