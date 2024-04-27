import bcrypt
import random
import string


symbols_for_pwd = string.ascii_letters + string.digits


def gen_token() -> str:
    return ''.join([random.choice(symbols_for_pwd) for _ in range(30)])


def hash_password(pwd: str) -> bytes:
    hash_and_salt = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())
    return hash_and_salt


def check_password(hash_str: bytes, password: str) -> bool:
    return bcrypt.checkpw(password.encode(), bytes(hash_str))
