from src.repo.repository import *
from src.usecase.usecase import *
from src.usecase.password import check_password

import datetime


async def add_new_user(data: dict):
    unfill = []
    for i in ["nickname", "password", "email", "birth_date", "phone_number", "name", "surname"]:
        if i not in data:
            unfill.append(i)
    if unfill:
        raise ValueError(f"not enough fields in data for register, you need to fill: {', '.join(unfill)}") 
    exists = await check_user(data['nickname'])
    if exists:
        raise ValueError("this user already exists!")
    await Repository().add_user(data)


async def check_auth_user(login: str, password: str) -> bool:
    if not check_user(login):
        raise ValueError("this user doesn't exists")
    hash = await Repository().ret_auth_data(login)
    bytes_hash = bytes(hash)
    return check_password(bytes_hash, password)
     

async def check_user(nick: str):
    v = await Repository().check_user(nick)
    return v


async def change_data_user(new_data: dict):
    pass


async def add_token(user_id: int, token: str):
    time_for_end = datetime.datetime.now() + datetime.timedelta(hours=3)
    await Repository().new_token(token, user_id, time_for_end)
