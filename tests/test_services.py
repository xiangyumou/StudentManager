import pytest
from src.database.db import db, Base
from src.database.models import User, Identity
from src.services.user_service import UserService
from src.services.auth_service import AuthService
import os

# Use an in-memory SQLite DB for testing
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def setup_database():
    # Override the engine path or just ensure we treat current DB as disposable if using file
    # For simplicity in this env, let's use the actual DB setup but ensure we start fresh or use a separate test db file
    # Here we will re-init the global db with memory for safety
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

@pytest.fixture
def user_service(setup_database):
    return UserService(session=setup_database)

@pytest.fixture
def auth_service(setup_database):
    return AuthService(session=setup_database)

def test_create_user(user_service):
    success, msg = user_service.create_user(
        identifier="admin",
        account="admin",
        password="password123",
        identity=Identity.ADMIN
    )
    assert success is True
    
    # Try duplicate
    success, msg = user_service.create_user(
        identifier="admin",
        account="admin",
        password="password123",
        identity=Identity.ADMIN
    )
    assert success is False

def test_login_success(auth_service):
    status, user, msg = auth_service.login("admin", "password123")
    assert status == 3
    assert user.account == "admin"

def test_login_failure(auth_service):
    status, user, msg = auth_service.login("admin", "wrongpassword")
    assert status == 1

def test_login_unknown(auth_service):
    status, user, msg = auth_service.login("unknown", "password")
    assert status == 0
