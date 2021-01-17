import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy_utils import ChoiceType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Tick(Base):
    COIN_TYPES = [
        ('btc', 'BTC'),
        ('eth', 'ETH')
    ]

    DIR_TYPES = [
        ('rise', 'rise'),
        ('drop', 'drop'),
        ('same', 'same')
    ]

    OP_TYPES = [
        ('SIT', 'SIT'),
        ('BUY', 'BUY'),
        ('SELL', 'SELL')
    ]

    __tablename__ = 'tick'
    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
    coin = Column(ChoiceType(COIN_TYPES), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    direction = Column(ChoiceType(DIR_TYPES), nullable=False)
    op = Column(ChoiceType(OP_TYPES), nullable=False)

engine = create_engine('sqlite:///bitkonj.db')
Base.metadata.bind = engine
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

def init():
    if session.query(Tick).count() == 0:
        for i in range(650):
            new_tick = Tick(price=0, coin='btc', direction='same', op='SIT')
            session.add(new_tick)
            session.commit()

def tick(price, last_buy, last_sell, last_action, coin='btc'):
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

    new_tick = Tick(price=price, coin=coin, direction=direction, op=action)
    session.add(new_tick)
    session.commit()

    if last_action == 'BUY' and abs(last_buy - price) < 20:
        return price, coin, action, average_price

    if last_action == 'SELL' and abs(last_sell - price) < 20:
        return price, coin, action, average_price

    try:
        if last_tick.direction == 'drop' and direction == 'rise':
            if last_sell > price:
                action = 'BUY'
            else:
                try:
                    last_ticks600 = session.query(Tick).order_by(Tick.timestamp.asc()).all()[-601:]
                    if all(i.op == 'SIT' for i in last_ticks600) and abs(price - last_sell) > 100:
                        action = 'BUY'
                    elif all(i.op == 'SIT' for i in last_ticks600[-301:-1]) and abs(price - last_sell) > 200:
                        action = 'BUY'
                    else:
                        action = 'FUCK'
                except Exception:
                    pass
        elif last_tick.direction == 'rise' and direction == 'drop':
            if last_buy < price:
                action = 'SELL'
            else:
                try:
                    last_ticks600 = session.query(Tick).order_by(Tick.timestamp.asc()).all()[-601:]
                    if all(i.op == 'SIT' for i in last_ticks600) and abs(last_buy.price - price) > 100:
                        action = 'SELL'
                    elif all(i.op == 'SIT' for i in last_ticks600[-301:-1]) and abs(last_buy.price - price) > 200:
                        action = 'SELL'
                    else:
                        action = 'FUCK'
                except Exception:
                    pass
    except Exception:
        pass

    new_tick.op = action
    session.commit()

    return price, coin, action, average_price
