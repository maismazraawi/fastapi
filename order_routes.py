from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from models import User, Order
from schemas import OrderModel, OrderStatusModel
from DataBase import Session, engine
from fastapi.encoders import jsonable_encoder


order_router = APIRouter(  # prefix to create seperate routes -> acsess from http
    prefix= ("/orders"),
    tags = ['orders']
    )

session = Session(bind=engine)


@order_router.get('/')  # create instances similar to main api instance -> routers create diff routes to diff func
async def hello(Authorize:AuthJWT=Depends()):
    """
        ## Sample Route
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
            )
    return {"message": "Hi"}


@order_router.post('/order', status_code=status.HTTP_201_CREATED)
async def place_order(order:OrderModel, Authorize:AuthJWT=Depends()):
    """
        ## Placing an Order
        requires -> quantity:int , pizza_size:str
    """
    try:
        Authorize.jwt_required()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
            )
        
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username==current_user).first()
    
    new_order = Order(
        pizza_size = order.pizza_size,
        quantity = order.quantity
    )
    
    new_order.user = user
    session.add(new_order) 
    session.Commit()
    
    response = {
        "pizza_size": new_order.pizza_size,
        "quantity": new_order.quantity,
        "id": new_order.id,
        "order_status": new_order.order_status
    }
    
    return jsonable_encoder(response)


#list all the orders
@order_router.get('/orders')
async def list_all_orders(Authorize:AuthJWT=Depends()):
    """
        ## lists all the Orders 
        can be accessed by SuperUsers
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token"
                            )
    
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username==current_user).first()
    
    if user.is_staff:
        orders = session.query(Order).all()
        return jsonable_encoder(orders)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="You are not a SuperUser"
                        )


#get one order by id -> only accessed by a superuser
@order_router.get('/orders/{id}')
async def get_order_by_id(id:int, Authorize:AuthJWT=Depends()):
    """
        ## Getting an Order by it's ID
        -- only accessed by SuperUser
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    user = Authorize.get_jwt_subject()    
    current_user = session.query(User).filter(User.username==user).first()
    
    if current_user.is_staff:
        order = session.query(Order).filter(order.id==id).first()
        return jsonable_encoder(order)
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User NOt Allowed To Carry Out Request"
        )
 
    
#Get Current User Orders
@order_router.get('/user/orders')
async def get_user_orders(Authorize:AuthJWT=Depends()):
    """
        ## Getting The Current User Orders
        lists orders made by currently logged users
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    user = Authorize.get_jwt_subject()    
    current_user = session.query(User).filter(User.username==user).first()
    
    return jsonable_encoder(current_user.orders)


# Get Current User's Specific Order
@order_router.get('/user/order/{id}/')
async def get_specific_order(id:int, Authorize:AuthJWT=Depends()):
    """
        ## Getting specific Order by Current User
        lists order by ID made by currently logged users
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    subject = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username==subject).first()
    orders = current_user.orders
    for o in orders:
        if o.id == id:
            return jsonable_encoder(o)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No Order With Such ID"
                        )
    
#Update an Order
@order_router.put('/orders/order/update/{id}/')
async def Update_Order(id:int,order:OrderModel, Authorize:AuthJWT=Depends()):
    """
        ## Updating an Order
        requires -> quantity:int , pizza_size:str
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
        
    order_to_update = session.query(Order).filter(Order.id==id).first()
    order_to_update.quantity = order.quantity
    order_to_update.pizza_size = order.pizza_size
    
    session.commit()

    response={
                "id":order_to_update.id,
                "quantity":order_to_update.quantity,
                "pizza_size":order_to_update.pizza_size,
                "order_status":order_to_update.order_status,
            }
    
    return jsonable_encoder(order_to_update)


# implement order status in route
@order_router.patch('/order/update/{id}/')
async def update_order_statuse(id:int,
                               order:OrderStatusModel, 
                               Authorize:AuthJWT=Depends()
                               ):
    """
        ## Updating an Order's Status
        requires -> order_status:str
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username==username).first()
    if current_user.is_staff:
        order_to_update = session.query(Order).filter(Order.id==id).first()
        order_to_update.order_status = order.order_status
        
        session.commit()
        
        respose ={
                "id": order_to_update.id,
                "quantity": order_to_update.quantity,
                "pizza_size": order_to_update.pizza_size,
                "order_statuse": order_to_update.order_status,
            }
        
        return jsonable_encoder(respose)


# Delete an Order Route
@order_router.delete('/order/delet/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_an_order(id:int, Authorize:AuthJWT=Depends()):
    """
        ## Deleting Order
        for deleting an specific Order by it's ID
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    order_to_delete = session.query(Order).filter(Order.id==id).first()
    session.delete(order_to_delete)
    session.commit()
    
    return order_to_delete

