import os
from dotenv import load_dotenv


def load_env():
    path = "/".join([os.getcwd(), "src", "config", ".env"])
    print(path)
    load_dotenv(path)
    print("initialized")
    print(os.getenv("DB_PASS"))
