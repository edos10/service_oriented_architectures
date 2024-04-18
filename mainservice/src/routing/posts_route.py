from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from src.usecase.usecase import *
from src.repo.repository import Repository
from src.usecase.password import gen_token
from src.models.models import *
from google.protobuf.json_format import MessageToJson
import grpc
from src.proto.posts_service_pb2_grpc import PostServiceStub
from src.proto import posts_service_pb2
from src.usecase.grpc import grpc_connect


import json

post_router = APIRouter()


@post_router.post('/create_post', status_code=201)
async def create_post(request: Request):
    input_data = await request.body()
    input_data = json.loads(input_data.decode("utf-8").replace("'",'"'))

    if 'title' not in input_data or 'text_description' not in input_data:
        return JSONResponse(content={"message": "invalid input data"}, status_code=400)
    

    # вынести в usecase
    get_id = await Repository.get_user_token(input_data['token'])

    if get_id <= 0:
        return JSONResponse(content={"message": "invalid token, try again"}, status_code=400)
    
    check_token = await Repository.check_current_token(input_data['token'], get_id)

    if not check_token:
        return JSONResponse(content={"message": "your authorization was expired, try again"}, status_code=400)
    
    try:
        client = await grpc_connect()
        response = client.CreatePost(
            posts_service_pb2.CreatePostRequest(Title=input_data['title'], 
                                               Text_description=input_data['text_description'],
                                               Post_time=str(datetime.now()),
                                               User_id=get_id))
        return JSONResponse({
            'message': "created post successfully",
            'id': response.Id,
            'title': response.Title,
            'text_description': response.Text_description,
            'post_time': response.Post_time
        }, status_code=201)
    except grpc.RpcError as e:
        msg = e.details()
        if e.code() == grpc.StatusCode.PERMISSION_DENIED:
            msg = "access to thid post denied!"
        elif e.code() == grpc.StatusCode.INTERNAL:
            msg = "error in grpc service"
        return JSONResponse({"message": e.details()}, status_code=400)


@post_router.post("/delete_post/{post_id}", status_code=204)
async def delete_post(request: Request, post_id: int):
    input_data = await request.body()
    input_data = json.loads(input_data.decode("utf-8").replace("'",'"'))
    
    get_id = await Repository.get_user_token(input_data['token'])

    if get_id <= 0:
        return JSONResponse(content={"message": "invalid token, try again"}, status_code=401)
    
    check_token = await Repository.check_current_token(input_data['token'], get_id)

    if not check_token:
        return JSONResponse(content={"message": "your authorization was expired, try again"}, 
                            status_code=401)
    
    try:
        client = await grpc_connect()
        client.DeletePost(
            posts_service_pb2.DeletePostRequest(Post_id=post_id))
        return JSONResponse({
            "message": f"post with id = {post_id} was deleted successfully"
        }, status_code=204)
    except grpc.RpcError as e:
        return JSONResponse({"message": e.details()}, status_code=400)



@post_router.put("/update_post/{post_id}", status_code=200)
async def update_post_user(request: Request, post_id: int):
    input_data = await request.body()
    input_data = json.loads(input_data.decode("utf-8").replace("'",'"'))
    input_data = defaultdict(str, input_data)

    get_id = await Repository.get_user_token(input_data['token'])

    if get_id <= 0:
        return JSONResponse(content={"message": "invalid token, try again"}, status_code=400)
    
    check_token = await Repository.check_current_token(input_data['token'], get_id)
    if not check_token:
        return JSONResponse(content={"message": "your authorization was expired, try again"}, status_code=400)
    
    try:
        client = await grpc_connect()
        response = client.UpdatePost(
            posts_service_pb2.UpdatePostRequest(Post_id=post_id,
                                                Title=input_data['title'],
                                                Text_description=input_data['text_description'],
                                                User_id=get_id))
        
        nickname = await Repository.get_nick_on_id(response.User_id)

        return JSONResponse({
            "post_body": {
            "title": response.Title,
            "text_description": response.Text_description,
            "post_time": response.Post_time,
            "nickname": nickname
            },
            "message": "update successfully"
        }, status_code=200)
    
    except grpc.RpcError as e:
        status_code = e.code()
        print(status_code)
        return JSONResponse({"message": e.details()}, status_code=400)

@post_router.get("/get_post/{post_id}", status_code=200)
async def get_post_on_id(request: Request, post_id: int):
    input_data = await request.body()
    input_data = json.loads(input_data.decode("utf-8").replace("'",'"'))

    get_id = await Repository.get_user_token(input_data['token'])

    if get_id <= 0:
        return JSONResponse(content={"message": "invalid token, try again"}, status_code=400)
    
    check_token = await Repository.check_current_token(input_data['token'], get_id)
    if not check_token:
        return JSONResponse(content={"message": "your authorization was expired, try again"}, status_code=400)
    

    try:
        client = await grpc_connect()
        response = client.GetPostOnId(
            posts_service_pb2.GetPostOnIdRequest(Post_id=post_id,))
        
        nickname = await Repository.get_nick_on_id(response.User_id)

        return JSONResponse({
            "title": response.Title,
            "text_description": response.Text_description,
            "post_time": response.Post_time,
            "nickname": nickname
        })
    except grpc.RpcError as e:
        status_code = e.code()
        print(status_code)
        return JSONResponse({"message": e.details()}, status_code=400)


@post_router.get("/get_post", status_code=200)
async def get_all_posts_with_pagination(request: Request):
    input_data = await request.body()
    input_data = json.loads(input_data.decode("utf-8").replace("'",'"'))

    get_id = await Repository.get_user_token(input_data['token'])

    if get_id <= 0:
        return JSONResponse(content={"message": "invalid token, try again"}, status_code=400)
    
    check_token = await Repository.check_current_token(input_data['token'], get_id)
    if not check_token:
        return JSONResponse(content={"message": "your authorization was expired, try again"}, status_code=400)
    


    if 'page_number' not in input_data or 'count_on_page' not in input_data:
        return JSONResponse(content={"message": "invalid input data"}, status_code=400)

    try:
        client = await grpc_connect()
        response = client.GetPostsOnPagination(
            posts_service_pb2.GetPostPageRequest(Num_page=input_data['page_number'], 
                                               Count_on_page=input_data['count_on_page'],))
        arr_posts = []
        for post in response.posts:
            arr_posts.append({"id": post.Id, 
                              "title": post.Title, 
                              "user_id": post.User_id, 
                              "text_description": post.Text_description, 
                              "post_time": post.Post_time})
        return JSONResponse(content=arr_posts, status_code=200)
    except grpc.RpcError as e:
        return JSONResponse(content={"message": f"{e.details()}"}, status_code=400)
