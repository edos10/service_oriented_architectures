import datetime

from src.repo.init_db import connection_start
from collections import defaultdict


class Repository:
    async def get_users(self) -> list:
        conn = await connection_start()
        values = await conn.fetch('''SELECT * FROM users''')
        await conn.close()
        return values

    async def get_user_nick(nick: str) -> int:
        conn = await connection_start()
        value = await conn.fetch(f"SELECT id FROM users WHERE nickname='{nick}'")
        await conn.close()
        if len(value) == 0:
            return -1
        return value[0]['id']
    
    async def get_nick_on_id(user_id: int) -> str:
        conn = await connection_start()
        value = await conn.fetch(f"SELECT nickname FROM users WHERE id={user_id}")
        await conn.close()
        if len(value) == 0:
            return ""
        return value[0]['nickname']

    async def get_user_token(token: str) -> int:
        conn = await connection_start()
        value = await conn.fetch(f"SELECT id FROM tokens WHERE token='{token}'")
        await conn.close()
        if len(value) == 0:
            return -1
        return value[0]['id']

    async def check_user(self, nick: str) -> bool:
        conn = await connection_start()
        values = await conn.fetch(f"SELECT * FROM users WHERE nickname='{nick}'")
        await conn.close()
        return bool(values)
    
    async def ret_auth_data(self, login: str) -> str:
        conn = await connection_start()
        hash = await conn.fetch(f"SELECT password FROM users WHERE nickname='{login}'")
        await conn.close()
        return hash

    async def add_user(self, data: defaultdict) -> int:
        conn = await connection_start()
        new_id = await conn.fetch(f"""INSERT INTO users (
                                      nickname, "password", email, phone_number, "name", surname, birth_date) 
                                      VALUES (
                                      '{data['nickname']}', 
                                      '{data['password']}', 
                                      '{data['email']}', 
                                      '{data['phone_number']}', 
                                      '{data['name']}',
                                      '{data['surname']}', 
                                      CASE WHEN ('{data['birth_date']}' <> '') IS FALSE THEN CAST(NULL as DATE)
										  ELSE '{data['birth_date'] or '2002-10-05'}'
									  END
                                      ) RETURNING id""")
        await conn.close()
        return new_id[0]['id']

    async def update_user(user_id: int, data: dict) -> dict:
        conn = await connection_start()
        data.pop("token")
        for i, v in data.items():
            await conn.fetch(f"""UPDATE users SET {i}='{v}' WHERE id = $1""", user_id)
        value = await conn.fetch(f"SELECT * from users WHERE id = $1", user_id)
        if not value:
            raise ValueError("error in database in selecting this user!")
        await conn.close()
        user = value[0]
        return {
            "email": user['email'],
            "name": user['name'],
            "surname": user['surname'],
            "nickname": user['nickname'],
            "phone_number": user['phone_number'],
            "birth_date": datetime.datetime.strftime(user['birth_date'], '%Y-%m-%d')
        }

    async def new_token(self, token: str, user_id: int, end_time) -> None:
        conn = await connection_start()
        await conn.fetch(f"""INSERT INTO tokens (id, token, end_time) 
                         VALUES ({user_id}, '{token}', '{end_time}')
                         """)
        await conn.close()

    async def check_current_token(token: str, user_id: int) -> bool:
        conn = await connection_start()
        tokens = await conn.fetch(f"SELECT * FROM tokens WHERE id={user_id} AND token='{token}'")
        await conn.close()
        if tokens[0]['end_time'] >= datetime.datetime.now():
            return True
        return False


class RepositoryPost:
    async def get_posts():
        pass

    async def get_post_on_id(id: int):
        conn = await connection_start()
        tokens = await conn.fetch(f"SELECT * FROM posts WHERE id={id}")
        await conn.close()
        if len(tokens):
            return True
        return False
        
