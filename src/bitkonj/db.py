import datetime
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Tick(Base):
    __tablename__ = 'tick'
    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)

class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
    op_type = Column(String, nullable=False)
    tick_id = Column(Integer,
                     ForeignKey('tick.id'),
                     nullable=False)
    tick = relationship('Tick')

engine = create_engine('sqlite:///bitkonj.db')
Base.metadata.bind = engine
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

def save_tick(price):
    try:
        new_tick = Tick(price=price)
        session.add(new_tick)
        session.commit()

        return new_tick.id
    except Exception as e:
        raise(f"{e}")

def save_order(price, op_type, tick_id):
    try:
        new_order = Order(price=price, op_type=op_type, tick_id=tick_id)
        session.add(new_order)
        session.commit()
    except Exception as e:
        raise(f"{e}")

def get_last_op_id():
    try:
        return session.query(Order).all()[-1].id
    except Exception:
        return None

def get_last_op_tick_id():
    try:
        return session.query(Order).all()[-1].tick_id
    except Exception:
        return None

def get_last_op_type():
    try:
        return session.query(Order).all()[-1].op_type
    except Exception:
        return None

def get_last_op_price():
    try:
        return session.query(Order).all()[-1].price
    except Exception:
        return None
