import grpc
from src.proto.posts_service_pb2_grpc import PostServiceStub

async def grpc_connect():
    channel = grpc.insecure_channel("post_service:80")
    return PostServiceStub(channel)
