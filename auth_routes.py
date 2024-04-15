from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from DataBase import Session, engine
from sqlalchemy.orm import Session
from schemas import SignUpModel, LoginModel
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder 


auth_router = APIRouter(  # prefix to create seperate routes -> acsess from http
    prefix= ("/auth"),
    tags= ['auth'] 
    )


session = Session(bind=engine) #map session to database


@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user:SignUpModel):
    """
        ## Creat a User
        requires -> 
        ```
                username: int
                email: str
                password: str
                is_staff: Bool,
                is_active: Bool
        ```
    """
    
    db_email = session.query(User).filter(User.email==user.email).first()
    
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail= "User with the email already exists"
                             )

    db_username = session.query(User).filter(User.username==user.username).first()
    
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail= "User with the username already exists"
                             )

    new_user = User(
        #id = user.id,
        username = user.username,
        email = user.email,
        password = generate_password_hash(user.password),
        is_active = user.is_active,
        is_staff = user.is_staff
    )
    
    session.add(new_user)
    
    session.commit()
    
    response = {
        #"id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "is_active": new_user.is_active,
        "is_staff": new_user.is_staff
    }
    
    return jsonable_encoder(response)

# Login Route
@auth_router.post('/login', status_code=status.HTTP_202_ACCEPTED)
#query -> check user exists or not
async def login(user:LoginModel, Authorize:AuthJWT=Depends()):
    """
        ## LogIn a User
        require ->
        ```
                username: str
                password: str
        ```
        and returns a token pair 'access' and 'refresh'
    """
    
    db_user = session.query(User).filter(User.username==user.username).first()

    if db_user and check_password_hash(db_user.password, user.password):
        access_token = Authorize.create_access_token(subject=db_user.username)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username)

        response = {
            "access": access_token,
            "refresh": refresh_token
        }
        
        return jsonable_encoder(response)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Username or Password"
                        )
    
