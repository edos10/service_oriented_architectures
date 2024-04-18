from src.repo.init_db import connection_start
from collections import defaultdict

class Repository:
    async def get_users(self) -> list:
        conn = await connection_start()
        values = await conn.fetch('''SELECT * FROM users''')
        await conn.close()
        return values

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

    async def add_user(self, data: defaultdict) -> None:
        conn = await connection_start()
        await conn.fetch(f"""INSERT INTO users (
                                      nickname, password, email, description) 
                                      VALUES ('{data['nickname']}', '{data['password']}', 
                                      '{data['email']}', '{data['description']}')""")
        await conn.close()

    async def update_user(self, user_id: int, data: dict) -> None:
        conn = await connection_start()
        await conn.fetch(f"""UPDATE INTO users (
                                      nickname, password, email, description) 
                                      VALUES ('{data['nickname']}', '{data['password']}', 
                                      '{data['email']}', '{data['description']}')""")
        await conn.close()

    async def new_token(self, token: str, user_id: int, end_time) -> None:
        conn = await connection_start()
        await conn.fetch(f"""INSERT INTO tokens (id, token, end_time) 
                         VALUES ({user_id}, '{token}', '{end_time}')
                         """)
        await conn.close()
