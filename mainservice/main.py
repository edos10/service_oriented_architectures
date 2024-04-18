from fastapi import FastAPI
from src.routing.main_routes import main_router
from src.routing.posts_route import post_router
from src.config.config import *

app = FastAPI()
load_env()

app.include_router(main_router)
app.include_router(post_router)
