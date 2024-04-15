from DataBase import Base
from sqlalchemy import Column, Integer, Boolean, Text, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import ChoiceType
import reprlib


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer,primary_key=True, autoincrement=True)
    username = Column(String(25), unique=True)
    email = Column(String(90), unique=True)
    password = Column(Text, nullable=True)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    orders = relationship('Order', back_populates='user') #this is for relationship between user-order
    
    
    def __repr__(self): #function to return representation of obj created from class "Data"
        return f"<user {self.username}"


class Order(Base):
    ORDER_STATUSES = (
        ('PENDING', 'pending'),
        ('IN-TRANSIT', 'in-transit'),
        ('DELIVERED', 'delivered')
    )
    
    PIZZA_SIZES = (
        ('SMALL', 'small'),
        ('MEDIUM', 'medium'),
        ('LARGE', 'large'),
        ('EXTRA-LARGE', 'extra-large')
    )
    
    
    __tablename__ = "orders"
    id = Column(Integer,primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False)
    order_status = Column(ChoiceType(choices=ORDER_STATUSES), default="PENDING")
    pizza_size = Column(ChoiceType(choices=PIZZA_SIZES), default="SMALL")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='orders') #this is for relationship between user-order
    
    # transfer representations of obj created from this class
    def __repr__(self):
        return f"<Order {self.id}"
    
    