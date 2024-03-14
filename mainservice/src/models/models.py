from pydantic import BaseModel
from datetime import datetime

class NewUser(BaseModel):
     nickname: str
     password: str
     name: str | None
     surname: str | None
     email: str | None
     birth_date: str | None
     phone_number: str | None

     model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nickname": "Foo",
                    "password": "309230",
                    "name": "Ivan",
                    "surname": "Ivanov",
                    "email": "ivan@mail.ru",
                    "birth_date": "2005-12-31",
                    "phone_number": "79998887766"
                },
                {
                    "nickname": "Foo",
                    "password": "309230",
                }
            ]
        }
    }


class AuthUser(BaseModel):
     nickname: str
     password: str
     
     model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nickname": "Foo",
                    "password": "309230",
                }
            ]
        }
    }
    
class UpdateUser(BaseModel):
     token: str
     name: str | None
     surname: str | None
     email: str | None
     birth_date: str | None
     phone_number: str | None
     
     model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "token": "f34rgFN4J40okplLP0",
                    "name": "Ivan",
                    "surname": "Ivanov",
                    "email": "ivan@mail.ru",
                    "birth_date": "2005-12-31",
                    "phone_number": "79998887766"
                },
                {
                    "token": "f34rgFN4J40okplLP0",
                    "email": "ivan@mail.ru",
                }
            ]
        }
    }
     

class ResponseRegister(BaseModel):
     token: str
     
     model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "token": "f34rgFN4J40okplLP0",
                }
            ]
        }
    }

class ResponseRegister(BaseModel):
     token: str
     
     model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "token": "f34rgFN4J40okplLP0",
                }
            ]
        }
    }

class ResponseRegister(BaseModel):
     token: str | None
     message: str | None

     model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "token": "f34rgFN4J40okplLP0",
                },
                {
                    "message": "not enough data for register",
                }
            ]
        }
    }

class ResponseAuth(BaseModel):
     token: str | None
     message: str | None
     
     model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "token": "f34rgFN4J40okplLP0",
                },
                {
                    "message": "wrong password, try again!",
                },
                {
                    "message": "this user doesn't exists!",
                }
            ]
        }
    }

class ResponseUpdate(BaseModel):
     token: str
     
     model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "data succesfully updated",
                },
                {
                    "message": "data didn't update",
                },
                {
                    "message": "this user doesn't exists!",
                },
                {
                    "message": "life-time of token ended, try auth again!",
                }

            ]
        }
    }