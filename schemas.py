from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class SignUpModel(BaseModel):
    username : str
    email : EmailStr
    password : str
    is_staff : Optional[bool]
    is_active : Optional[bool]
    
    class config: # attach user table to validition schema
        from_orm = True
        json_schema_extra = {
            'example': {
                "username": "maismazraawi",
                "email": "maismazraawi@gmail.com",
                "password": "password",
                "is_staff": False,
                "is_active": True
            }
        }
        
        
#juw auth -> route to log in users
#tokens: stored on client + enable users to access routes
class Settings(BaseModel): 
    authjwt_secret_key: str='e345cb067a8c96c11a7feca28334c6abf5f3e936502cdc46af496c0d17f7c058'
    

class LoginModel(BaseModel): #schema to validate logging in data
    username : str
    password : str
    
    
class OrderModel(BaseModel):
    quantity : Optional[int]
    order_status: Optional[str] = "PENDING"
    pizza_size : Optional[str] = "SMALL"
    user_id : Optional[int]

    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example":{
                "quantity": 2,
                "pizza_size": "LARGE"
            }
        }
        
        
class OrderStatusModel(OrderModel):
    order_status : Optional[str] = "PENDING"
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example":{
                "order_status" : "PENDING"
            }
        }