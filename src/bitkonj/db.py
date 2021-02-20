import os
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

COIN = os.getenv("COIN")
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

if COIN == 'BTC':
    engine = create_engine('sqlite:///bitkonj_btc.db')
elif COIN == 'ETH':
    engine = create_engine('sqlite:///bitkonj_eth.db')
elif COIN == 'AVAX':
    engine = create_engine('sqlite:///bitkonj_avax.db')
elif COIN == 'XRP':
    engine = create_engine('sqlite:///bitkonj_xrp.db')
elif COIN == 'DASH':
    engine = create_engine('sqlite:///bitkonj_dash.db')
elif COIN == 'LTC':
    engine = create_engine('sqlite:///bitkonj_ltc.db')
elif COIN == 'ADA':
    engine = create_engine('sqlite:///bitkonj_ada.db')
elif COIN == 'SC':
    engine = create_engine('sqlite:///bitkonj_sc.db')
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

def get_ma(ticks):
    try:
        prices = [i.price for i in session.query(Tick).all()[-(ticks + 1):-1]]
        return sum(prices) / ticks
    except Exception:
        return None
