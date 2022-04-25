from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine

# 宣告對映
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)


class Student(Base):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)

    def __init__(self, name=None):
        self.name = name


class Movie(Base):
    __tablename__ = 'movies'

    test = Column(String(255), primary_key=True)
    title = Column(String(255), nullable=False)
    year = Column(Integer)
    hello = Column(String(255))

    def __init__(self, test=None, title=None, year=None, hello = None):
        self.test = test
        self.hello = hello
        self.title = title
        self.year = year

    def __repr__(self):
        return "Movie(%r, %r)" % (self.title, self.year)

# 連結SQLite3資料庫example.db
engine = create_engine('sqlite:///example.db')

# 建立Schema
Base.metadata.create_all(engine)    # 相當於Create Table