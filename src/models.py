from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, nullable=False)
    email = Column(String)
    twofa_secret = Column(String)
    status = Column(String, default='unknown')
    profile_id = Column(String)
    last_seen = Column(TIMESTAMP)

class Proxy(Base):
    __tablename__ = 'proxies'
    id = Column(Integer, primary_key=True)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    scheme = Column(String, nullable=False)
    country = Column(String)
    last_checked = Column(TIMESTAMP)
    rotation_url = Column(String)

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    cookies = Column(JSON)
    local_storage = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer)
    log_type = Column(String)
    path = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
