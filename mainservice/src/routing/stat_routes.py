from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from src.usecase.usecase import *
from src.repo.repository import Repository, RepositoryPost
from src.usecase.password import gen_token
from src.models.models import *
from src.routing.posts_route import get_post_on_id
import json, os
from src.usecase.kafka import *
import grpc
from src.proto import stat_service_pb2
from src.usecase.grpc import grpc_connect


stat_router = APIRouter()


@stat_router.post('/view_post/{post_id}', status_code=200)
async def new_view(request: Request, post_id: int):
    input_data = request.headers
    if 'token' not in input_data:
        return JSONResponse(content={"message": "not autorized, required token, try authorize"}, status_code=401)
    
    get_id = await Repository.get_user_token(input_data['token'])

    if get_id <= 0:
        return JSONResponse(content={"message": "invalid token, try again"}, status_code=400)
    
    check_token = await Repository.check_current_token(input_data['token'], get_id)

    if not check_token:
        return JSONResponse(content={"message": "your authorization was expired, try again"}, status_code=400)

    check_post = await get_post_on_id(request, post_id)
    if check_post.status_code != 200:
        return JSONResponse(content={"message": "such post doesnt exists"}, status_code=404) 
    
    ans_json = check_post.body
    ans_json = json.loads(ans_json.decode("utf-8").replace("'",'"'))
    id_user = await Repository.get_user_nick(ans_json["nickname"])
    if id_user <= 0:
        return JSONResponse(content={"message": "error in like post, try again"}, status_code=400)
    
    producer = await get_producer(os.getenv("KAFKA_INSTANCE"))

    await send_producer_kafka(producer, {"time": datetime.now().isoformat(), "user_id": get_id, "post_id": post_id, "author": id_user}, "views")


@stat_router.post('/like_post/{post_id}', status_code=200)
async def new_like(request: Request, post_id: int):
    input_data = request.headers
    if 'token' not in input_data:
        return JSONResponse(content={"message": "not autorized, required token, try authorize"}, status_code=401)
    
    get_id = await Repository.get_user_token(input_data['token'])

    if get_id <= 0:
        return JSONResponse(content={"message": "invalid token, try again"}, status_code=400)
    
    check_token = await Repository.check_current_token(input_data['token'], get_id)

    if not check_token:
        return JSONResponse(content={"message": "your authorization was expired, try again"}, status_code=400)

    check_post = await get_post_on_id(request, post_id)
    if check_post.status_code != 200:
        return JSONResponse(content={"message": "such post doesnt exists"}, status_code=404)
    
    ans_json = check_post.body
    ans_json = json.loads(ans_json.decode("utf-8").replace("'",'"'))
    id_user = await Repository.get_user_nick(ans_json["nickname"])
    if id_user <= 0:
        return JSONResponse(content={"message": "error in like post, try again"}, status_code=400)

    producer = await get_producer(os.getenv("KAFKA_INSTANCE"))

    await send_producer_kafka(producer, {"time": datetime.now().isoformat(), "user_id": get_id, "post_id": post_id, "author": id_user}, "likes")


@stat_router.get('/stats_post/{post_id}', status_code=200)
async def get_stats_post(request: Request, post_id: int):
    if not RepositoryPost.get_post_on_id(post_id):
        raise HTTPException(status_code=404, content={"message": "such post doesnt exists"})
    input_data = request.headers
    if 'token' not in input_data:
        return JSONResponse(content={"message": "not autorized, required token, try authorize"}, status_code=401)
    try:
        client = await grpc_connect("stat")
        response = client.GetStatPost(
            stat_service_pb2.GetStatPostRequest(Post_id=post_id))
        return JSONResponse(content={
            "likes": response.Likes,
            "views": response.Views,
            "id": response.Post_id
        }, status_code=200)
    except grpc.RpcError as e:
        msg = e.details()
        if e.code() == grpc.StatusCode.PERMISSION_DENIED:
            msg = "access to this post denied!"
        elif e.code() == grpc.StatusCode.INTERNAL:
            msg = "error in grpc service"
        return JSONResponse({"message": msg}, status_code=400)


@stat_router.get('/top3like', status_code=200)
async def get_top3_users(request: Request):
    input_data = request.headers
    if 'token' not in input_data:
        return JSONResponse(content={"message": "not autorized, required token, try authorize"}, status_code=401)
    try:
        client = await grpc_connect("stat")
        response = client.GetTopNUsers(
            stat_service_pb2.GetTopNUsersRequest(Top_N=3))
        lst = []
        for user in response.Users:
            user_login = await Repository.get_nick_on_id(user.User_id)
            print(user.User_id, user_login, user.Total_likes)
            if user_login == "":
                raise HTTPException(status_code=404, detail={"message": "error in returning id author..."})
            lst.append(
                {
                    "id": user.User_id,
                    "login": user_login,
                    "total_likes": user.Total_likes,
                }
            )
        return JSONResponse(content=lst, status_code=200)
    except grpc.RpcError as e:
        msg = e.details()
        if e.code() == grpc.StatusCode.PERMISSION_DENIED:
            msg = "access to this post denied!"
        elif e.code() == grpc.StatusCode.INTERNAL:
            msg = "error in grpc service"
        return JSONResponse({"message": msg}, status_code=400)


@stat_router.get('/top5_post_stat/', status_code=200)
async def get_top5_posts(request: Request, is_views: bool = False):
    if "is_views" in request.query_params:
        try:
            is_views = int(request.query_params["is_views"])
        except Exception:
            return JSONResponse(content={"message": "wrong query parameter"}, status_code=400)
    input_data = request.headers
    if 'token' not in input_data:
        return JSONResponse(content={"message": "not autorized, required token, try authorize"}, status_code=401)

    field_for_ans = "views" if is_views else "likes"

    try:
        client = await grpc_connect("stat")
        response = client.GetTopPosts(
            stat_service_pb2.GetTopPostsRequest(Views=is_views))
        lst = []
        for post in response.Posts:
            user_login = await Repository.get_nick_on_id(post.Author)
            print(user_login, post.Author)
            if user_login == "":
                raise HTTPException(status_code=404)
            lst.append(
                {
                    "post_id": post.Id,
                    "nickname": user_login,
                    field_for_ans: post.Amount,
                    "user_id": post.Author,
                }
            )
        return JSONResponse(content=lst, status_code=200)
    except grpc.RpcError as e:
        msg = e.details()
        if e.code() == grpc.StatusCode.INTERNAL:
            msg = "error in grpc service"
        return JSONResponse({"message": msg}, status_code=400)