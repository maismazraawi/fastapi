from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from models import User, Order
from schemas import OrderModel, OrderStatusModel
from DataBase import Session, engine
from fastapi.encoders import jsonable_encoder


order_router = APIRouter(  # prefix to create seperate routes -> acsess from http
    prefix= "/orders",
    tags = ['orders']
    )

session = Session(bind=engine)


# create instances similar to main api instance -> routers create diff routes to diff func
@order_router.post('/order', status_code=status.HTTP_201_CREATED)
async def place_order(order:OrderModel, Authorize:AuthJWT=Depends()):
    """
        ## Placing an Order
        requires :
        quantity:int , 
        pizza_size:str,
        pizza_status
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
        quantity = order.quantity,
        order_status = order.order_status
    )
    
    new_order.user = user
    session.add(new_order) 
    session.commit()
    
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
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token"
                            )
    
    orders = session.query(Order).all()
    return jsonable_encoder(orders)


#get one order by id 
@order_router.get('/orders/{id}')
async def get_order_by_id(id:int, Authorize:AuthJWT=Depends()):
    """
        ## Getting an Order by providing it's ID
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
        
    order = session.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return jsonable_encoder(order)
 

#Update an Order
@order_router.put('/order/update/{id}/')
async def Update_Order(id:int,
                       order:OrderModel, 
                       status_update: OrderStatusModel, 
                       Authorize:AuthJWT=Depends()):
    """
        ## Updating an Order
        requires :
        quantity:int , 
        pizza_size:str,
        pizza_status
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
        
    order_to_update = session.query(Order).filter(Order.id==id).first()
    if not order_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    order_to_update.quantity = order.quantity
    order_to_update.pizza_size = order.pizza_size
    order_to_update.order_status = order.order_status
    
    session.commit()

    response={
                "id":order_to_update.id,
                "quantity":order_to_update.quantity,
                "pizza_size":order_to_update.pizza_size,
                "order_status":order_to_update.order_status,
            }
    
    return jsonable_encoder(response)


# Delete an Order Route
@order_router.delete('/order/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
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
