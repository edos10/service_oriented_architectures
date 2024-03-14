from src.repo.repository import *
from src.usecase.password import check_password
from collections import defaultdict

import datetime


async def add_new_user(data: dict) -> int:
    unfill = []
    for i in ["nickname", "password", "email", "birth_date", "phone_number", "name", "surname"]:
        if i not in data:
            unfill.append(i)
    if unfill:
        raise ValueError(f"not enough fields in data for register, you need to fill: {', '.join(unfill)}") 
    exists = await check_user(data['nickname'])
    if exists:
        raise ValueError("this user already exists!")
    return await Repository().add_user(defaultdict(str, data))


async def check_auth_user(login: str, password: str) -> bool:
    if not await check_user(login):
        raise ValueError("this user doesn't exists")
    hash_p = await Repository().ret_auth_data(login)
    print(hash_p[0]['password'], password)
    bytes_hash = bytes(hash_p[0]['password'], encoding='utf-8')
    return hash_p[0]['password'] == password
     

async def check_user(nick: str):
    return await Repository().check_user(nick)


async def change_data_user(new_data: dict):
    pass


async def add_token(user_id: int, token: str):
    time_for_end = datetime.datetime.now() + datetime.timedelta(seconds=40)
    await Repository().new_token(token, user_id, time_for_end)


async def add_without_token(nickname: str, token: str):
    user_id = await Repository().get_user(nickname)
    time_for_end = datetime.datetime.now() + datetime.timedelta(seconds=40)
    await Repository().new_token(token, user_id, time_for_end)


async def update_user(data: defaultdict):
    if "token" not in data:
        raise ValueError("you haven't got access for editing data")

    fields_for_update = dict()
    for i, v in data.items():
        if i in ["email", "phone_number", "name", "surname", "birth_date", "name"]:
            fields_for_update[i] = v
        if i in ["nickname", "password"]:
            raise ValueError("such fields are unavailable for updating")

    id_user = await Repository().get_user_token(data["token"])
    if not await Repository().check_current_token(data["token"], id_user):
        raise ValueError("life-time of token ended, try auth again!")
    await Repository().update_user(id_user, data)