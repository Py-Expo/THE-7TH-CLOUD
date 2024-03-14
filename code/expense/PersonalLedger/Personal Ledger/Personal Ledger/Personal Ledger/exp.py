from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    expensename = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    paymode = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)

    user = relationship('User', backref='expenses')
