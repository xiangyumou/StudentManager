from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from src.database.db import Base

class Identity(enum.Enum):
    STUDENT = 0
    TEACHER = 1
    COUNSELOR = 2
    GUARD = 3
    ADMIN = 4
    SUPER_ADMIN = 5

class User(Base):
    __tablename__ = 'users'

    identifier = Column(String(50), primary_key=True)
    account = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False) # Hashed password
    identity = Column(Enum(Identity), nullable=False)
    banned = Column(Boolean, default=False)
    num_consecutive_failure = Column(Integer, default=0)
    dual_authentication = Column(Boolean, default=False)

    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False)
    login_logs = relationship("LoginLog", back_populates="user")
    dual_auth_token = relationship("DualAuthToken", back_populates="user", uselist=False)

class DualAuthToken(Base):
    __tablename__ = 'dual_auth_tokens'
    
    identifier = Column(String(50), ForeignKey('users.identifier'), primary_key=True)
    token = Column(String(100), nullable=False)
    
    user = relationship("User", back_populates="dual_auth_token")

class Student(Base):
    __tablename__ = 'student_inf'

    identifier = Column(String(50), ForeignKey('users.identifier'), primary_key=True)
    major_id = Column(Integer)
    name = Column(String(100))
    class_id = Column(Integer)
    enrollment_time = Column(String(20)) # Keeping as string for now to match legacy, or could be Date

    user = relationship("User", back_populates="student_profile")

class LoginLog(Base):
    __tablename__ = 'login_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    identifier = Column(String(50), ForeignKey('users.identifier'))
    login_time = Column(DateTime, default=datetime.now)
    succeed = Column(Boolean)
    detail = Column(String(255)) # Success message or error reason
    dual_authentication = Column(Boolean) # If dual auth was required/used

    user = relationship("User", back_populates="login_logs")
