from fastapi import FastAPI
from src.routing.routes import *
from src.config.config import *


app = FastAPI()
load_env()

app.include_router(main_router)
