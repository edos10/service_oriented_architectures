from fastapi import FastAPI
import uvicorn

from src.routing.routes import *
from src.config.config import *


app = FastAPI()
load_env()

app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000)
