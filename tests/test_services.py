import pytest
from src.database.db import db, Base
from src.database.models import User, Identity
from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.config import Config
import os

# Override Config for testing
Config.DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def setup_database():
    # Use reset_engine to swap the singleton's engine to memory
    db.reset_engine(Config.DATABASE_URL)
    db.init_db()
    
    yield
    
    # Teardown
    Base.metadata.drop_all(db.engine)

@pytest.fixture
def user_service(setup_database):
    return UserService()

@pytest.fixture
def auth_service(setup_database):
    return AuthService()

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

def test_login_success(auth_service, user_service):
    # Ensure user exists (tests might run validation order, so best to create again or rely on fixture state)
    # Since we use module scope for DB but function scope for services (stateless), DB persists across tests in this file.
    # But test_create_user runs first usually.
    # Let's simple check if user needs creating
    if not user_service.get_user_by_account("admin"):
        user_service.create_user("admin", "admin", "password123", Identity.ADMIN)

    status, user, msg = auth_service.login("admin", "password123")
    assert status == 3
    assert user.account == "admin"

def test_login_failure(auth_service):
    status, user, msg = auth_service.login("admin", "wrongpassword")
    assert status == 1

def test_login_unknown(auth_service):
    status, user, msg = auth_service.login("unknown", "password")
    assert status == 0
