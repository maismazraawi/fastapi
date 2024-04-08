from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine('postgresql://postgres:mys0206887@localhost/pizzaDeliveryDB',
                      echo = True # allow seeing generated database transactions
                      )

Base = declarative_base() #help in CRUD of api/DB resources

Session = sessionmaker()  #create session instances 
