import os
from dotenv import load_dotenv


def load_env():
    path = "/".join([os.getcwd(), "src", "config", ".env"])
    load_dotenv(path)
    print(os.getenv("DB_PASS"))
