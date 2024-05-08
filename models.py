from database import Base
from sqlalchemy import  Column, ForeignKey, Integer, String,Boolean

class hisseler(Base):
    __tablename__="hisseler"
    id=Column(Integer, primary_key=True,index=True)
    kod=Column(String,unique=True)
    ad=Column(String, unique=True)
    fiyat = Column(Integer)
    hacim=Column(Integer)