import grpc
from src.proto.posts_service_pb2_grpc import PostServiceStub
from src.proto.stat_service_pb2_grpc import StatServiceStub

async def grpc_connect(name_service: str):
    assert name_service == "stat" or name_service == "post"
    port_service = "80"
    if name_service == "stat":
        port_service = "81"
    channel = grpc.insecure_channel(f"{name_service}_service:{port_service}")
    if name_service == "post":
        return PostServiceStub(channel)
    return StatServiceStub(channel)
