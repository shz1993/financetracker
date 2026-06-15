import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import streamlit as st

# Database setup
DATABASE_URL = st.secrets.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/finance_tracker")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    transactions = relationship("Transaction", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    icon = Column(String(10), default="💰")
    
    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    amount = Column(Float, nullable=False)
    description = Column(String(200))
    date = Column(Date, nullable=False)
    type = Column(String(10), nullable=False)  # 'expense' or 'income'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

def init_db():
    """Create tables and default categories"""
    Base.metadata.create_all(bind=engine)
    
    # Add default categories if not exists
    db = SessionLocal()
    default_categories = [
        ("🍔 Food", "🍔"), ("🏠 Rent", "🏠"), ("🚗 Transport", "🚗"),
        ("📱 Utilities", "📱"), ("🎉 Entertainment", "🎉"), ("💊 Health", "💊"),
        ("📚 Education", "📚"), ("🛍️ Shopping", "🛍️"), ("💰 Salary", "💰"),
        ("💵 Investment", "💵"), ("🎁 Gift", "🎁"), ("❓ Other", "❓")
    ]
    
    for cat_name, icon in default_categories:
        exists = db.query(Category).filter(Category.name == cat_name).first()
        if not exists:
            db.add(Category(name=cat_name, icon=icon))
    db.commit()
    db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()