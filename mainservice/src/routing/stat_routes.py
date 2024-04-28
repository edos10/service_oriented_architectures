from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from src.usecase.usecase import *
from src.repo.repository import Repository
from src.usecase.password import gen_token
from src.models.models import *
import json, os
from src.usecase.kafka import *


stat_router = APIRouter()


@stat_router.post('/view/{post_id}', status_code=200)
async def new_view(request: Request, post_id: int):
    input_data = await request.body()
    input_data = json.loads(input_data.decode("utf-8").replace("'",'"'))

    if "token" not in input_data:
        return JSONResponse(content={"message": "you didn't authorized!"}, status_code=400)
    
    get_id = await Repository.get_user_token(input_data['token'])

    if get_id <= 0:
        return JSONResponse(content={"message": "invalid token, try again"}, status_code=400)
    
    check_token = await Repository.check_current_token(input_data['token'], get_id)

    if not check_token:
        return JSONResponse(content={"message": "your authorization was expired, try again"}, status_code=400)
    
    producer = await get_producer(os.getenv("KAFKA_INSTANCE"))

    await send_producer_kafka(producer, {"time": datetime.now().isoformat(), "user_id": get_id, "post_id": post_id}, "views")


@stat_router.post('/like/{post_id}', status_code=200)
async def new_like(request: Request, post_id: int):
    input_data = await request.body()
    input_data = json.loads(input_data.decode("utf-8").replace("'",'"'))

    if "token" not in input_data:
        return JSONResponse(content={"message": "you didn't authorized!"}, status_code=400)
    
    get_id = await Repository.get_user_token(input_data['token'])

    if get_id <= 0:
        return JSONResponse(content={"message": "invalid token, try again"}, status_code=400)
    
    check_token = await Repository.check_current_token(input_data['token'], get_id)

    if not check_token:
        return JSONResponse(content={"message": "your authorization was expired, try again"}, status_code=400)
    
    producer = await get_producer(os.getenv("KAFKA_INSTANCE"))

    await send_producer_kafka(producer, {"time": datetime.now().isoformat(), "user_id": get_id, "post_id": post_id}, "likes")