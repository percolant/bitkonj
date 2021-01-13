import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy_utils import ChoiceType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from . import vars

Base = declarative_base()

COIN_TYPES = [
    ('btc', 'BTC'),
    ('eth', 'ETH')
]

class Tick(Base):
    DIR_TYPES = [
        ('rise', 'rise'),
        ('drop', 'drop'),
        ('same', 'same'),
    ]

    __tablename__ = 'tick'
    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
    coin = Column(ChoiceType(COIN_TYPES), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    direction = Column(ChoiceType(DIR_TYPES), nullable=False)

class Order(Base):
    OPERATION_TYPES = [
        ('buy', 'buy'),
        ('sell', 'sell')
    ]

    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
    coin = Column(ChoiceType(COIN_TYPES), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    operation_type = Column(ChoiceType(OPERATION_TYPES), nullable=False)


engine = create_engine('sqlite:///bitkonj.db')
Base.metadata.bind = engine
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

def init():
    if session.query(Tick).count() == 0:
        for i in range(10):
            new_tick = Tick(price=0, coin='btc', direction='same')
            session.add(new_tick)
            session.commit()

    if session.query(Order).count() == 0:
        for i in range(3):
            new_order = Order(price=0, coin='btc', operation_type='buy')
            session.add(new_order)
            session.commit()

def tick(price, coin='btc'):
    action = 'SIT'

    try:
        last_ticks100 = session.query(Tick).all()[-101:-1]
        total = 0
        for i in last_ticks100:
            total += i.price
        average_price = total / 100
    except Exception as e:
        average_price = price

    try:
        last_tick = session.query(Tick).all()[-1]
        if last_tick.price > price:
            direction = 'drop'
        elif last_tick.price < price:
            direction = 'rise'
        else:
            direction = 'same'
    except Exception as e:
        direction = 'same'

    new_tick = Tick(price=price, coin=coin, direction=direction)
    session.add(new_tick)
    session.commit()

    # try:
    #     last_ticks3 = session.query(Tick).all()[-3:-1]
    #     last_op = session.query(Order).filter(Order.coin == 'btc')[-1].operation_type
    #     if all(i.direction != 'rise' for i in last_ticks3) and direction == 'rise':
    #         if last_op != 'buy':
    #             action = 'BUY'
    #             average_price = average_price
    #     elif all(i.direction != 'drop' for i in last_ticks3) and direction == 'drop':
    #         if last_op != 'sell':
    #             action = 'SELL'
    #             average_price = average_price
    # except Exception as e:
    #     pass
    try:
        last_order = session.query(Order).filter(Order.coin == 'btc')[-1]
        if last_order.operation_type == 'buy':
            if price - last_order.price > 100:
                action = 'SELL'
            elif price - last_order.price < 0:
                if last_order.price - average_price > 200:
                    action = 'SELL'
        else:
            if last_order.price - price > 100:
                action = 'BUY'
            elif last_order.price - price < 0:
                if average_price - last_order.price > 200:
                    action = 'BUY'
    except Exception as e:
        pass

    # if action == 'BUY':
    #     try:
    #         last_sell = session.query(Order).filter(Order.operation_type == 'sell')[-1]
    #         if last_sell.price < price and average_price < last_sell.price:
    #             action = 'SIT'
    #     except Exception as e:
    #         pass

    # if action == 'SELL':
    #     try:
    #         last_buy = session.query(Order).filter(Order.operation_type == 'buy')[-1]
    #         if last_buy.price > price and average_price > last_buy.price:
    #             action = 'SIT'
    #     except Exception as e:
    #         pass

    return price, coin, action, average_price

def order(price, coin, operation_type):
    new_order = Order(price=price, coin=coin, operation_type=operation_type)
    session.add(new_order)
    session.commit()
