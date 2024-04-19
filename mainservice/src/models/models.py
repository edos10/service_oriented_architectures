from pydantic import BaseModel
from datetime import datetime

class NewUser(BaseModel):

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

class ResponseNewPost(BaseModel):
     model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Foo",
                    "text_description": "43g4rg4v",
                    "post_time": "2024-12-05T15:36:20Z",
                    "id": 12,
                    "message": "created post successfully",
                },
            ]
        }
    }

class UpdatePost(BaseModel):
     model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Foo",
                    "text_description": "43g4rg4v",
                    "token": "CNRUdemikc44mc3ocmr"
                },
                {
                    "text_description": "43g4rg4v",
                    "token": "CNRUdemikc44mc3ocmr"
                },
            ]
        }
    }

class UpdatePostResponse(BaseModel):
     model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "post_body": {
                    "title": "test",
                    "text_description": "test text",
                    "post_time": "2024-12-05T15:36:20Z",
                    "nickname": "user100",
                    },
                    "message": "update successfully"
                },
            ]
        }
    }

class UpdatePostResponseError(BaseModel):
     model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "access to this post denied",
                },
            ]
        }
    }