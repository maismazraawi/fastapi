from database import engine, Base
from models import User, Order


#to access metadata and connect it to sql engine
Base.metadata.create_all(bind=engine)
