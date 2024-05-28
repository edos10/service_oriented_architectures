from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from src.usecase.usecase import *
from src.repo.repository import Repository
from src.usecase.password import gen_token
from src.models.models import *
import json, os
from src.usecase.kafka import *
import grpc
from src.proto import stat_service_pb2
from src.usecase.grpc import grpc_connect


stat_router = APIRouter()


@stat_router.post('/view_post/{post_id}', status_code=200)
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


@stat_router.post('/like_post/{post_id}', status_code=200)
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


@stat_router.get('/stats_post/{post_id}', status_code=200)
async def get_stats_post(request: Request, post_id: int):
    try:
        client = await grpc_connect()
        response = client.GetStatPost(
            stat_service_pb2.GetStatPostRequest(Post_id=post_id))
        return JSONResponse(content={
            "likes": response.Likes,
            "views": response.Views,
        }, status_code=200)
    except grpc.RpcError as e:
        msg = e.details()
        if e.code() == grpc.StatusCode.PERMISSION_DENIED:
            msg = "access to this post denied!"
        elif e.code() == grpc.StatusCode.INTERNAL:
            msg = "error in grpc service"
        return JSONResponse({"message": msg}, status_code=400)


@stat_router.get('/top3_users_like', status_code=200)
async def get_stats_post(request: Request):
    pass


@stat_router.get('/top5_posts_on_stat', status_code=200)
async def get_stats_post(request: Request, post_id: int):
    pass