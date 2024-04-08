from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from DataBase import Session, engine
from schemas import SignUpModel, LoginModel
from models import User
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder 


auth_router = APIRouter(  # prefix to create seperate routes -> acsess from http
    prefix= ("/auth"),
    tags= ['auth'] 
    )


session = Session(bind=engine) #map session to database


@auth_router.get('/')  # create instances similar to main api instance -> routers create diff routes to diff func
async def hello(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token"
                            )
    
    return {"message": "Hiii"}


@auth_router.post('/signup',
                  status_code=status.HTTP_201_CREATED
                  )
async def signup(user:SignUpModel):
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
        username = user.username,
        email = user.email,
        password = generate_password_hash(user.password),
        is_active = user.is_active,
        is_staff = user.is_staff
    )
    
    Session.add(new_user)
    
    Session.commit
    
    return new_user 


# Login Route
@auth_router.post('/login', status_code=200)
#query -> check user exists or not
async def login(user:LoginModel, Authorize:AuthJWT=Depends()):
    db_user = Session.query(User).filter(User.username==user.username).first()

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
    
    
#Refreshing Tokens
@auth_router.get('/refresh')
async def refresh_token(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_refresh_token_required()
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Please Provide a Refreshed Token"
                            )
    
    current_user = Authorize._get_jwt_identifier()
    
    access_token = Authorize.create_access_token(subject=current_user)
    
    return jsonable_encoder({"access":access_token})        
