from sqlalchemy import Column, Integer, ForeignKey, VARCHAR, UniqueConstraint, SMALLINT, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    login = Column(VARCHAR(30), nullable=False)
    password = Column(VARCHAR(300), nullable=False)
    name = Column(VARCHAR(100), nullable=False)
    surname = Column(VARCHAR(100), nullable=True)
    secname = Column(VARCHAR(100), nullable=True)
    address = Column(VARCHAR(200))
    phone = Column(VARCHAR(30))
    role = Column(VARCHAR(300), nullable=False)

    UniqueConstraint(login, name="login")


class Bas(Base):
    __tablename__ = 'bas'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    # user_id = Column(Integer, ForeignKey(f"{User.__tablename__}.{User.id.name}"), nullable=False)
    user_id = Column(VARCHAR(100), nullable=True)
    products = Column(VARCHAR(500), nullable=True)

    # user = relationship('User', backref='user_bas')


class Product(Base):
    __tablename__ = 'product'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    name = Column(VARCHAR(100), nullable=False)
    image = Column(VARCHAR(100), nullable=False)
    description = Column(VARCHAR(300), nullable=False)
    price = Column(Integer, nullable=False)

    UniqueConstraint(name, name="name")
