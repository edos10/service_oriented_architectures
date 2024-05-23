import asyncpg
from src.config.config import *
import os


async def connection_start():
    print(os.getenv("DB_HOST"),os.getenv("DB_NAME"),os.getenv("DB_USER"),os.getenv("DB_PASS"))
    connection = await asyncpg.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
    
    return connection
