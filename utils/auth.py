import bcrypt
import streamlit as st
from sqlalchemy.orm import Session
from utils.database import User, get_db

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(db: Session, email: str, username: str, password: str):
    """Register new user"""
    # Check if user exists
    existing = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    
    if existing:
        return False, "Email or username already exists"
    
    # Create new user
    hashed_pw = hash_password(password)
    user = User(email=email, username=username, password_hash=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return True, user.id

def login_user(db: Session, username: str, password: str):
    """Login user"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return False, "Invalid username or password"
    
    if not verify_password(password, user.password_hash):
        return False, "Invalid username or password"
    
    return True, user

def get_current_user(db: Session):
    """Get current logged in user from session"""
    if "user_id" not in st.session_state:
        return None
    
    user = db.query(User).filter(User.id == st.session_state.user_id).first()
    return user