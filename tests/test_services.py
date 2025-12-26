import pytest
from src.database.db import db, Base
from src.database.models import User, Identity, Student, LoginLog, DualAuthToken
from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.config import Config
from sqlalchemy import text

# Override Config for testing
Config.DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def setup_database():
    db.reset_engine(Config.DATABASE_URL)
    db.init_db()
    yield
    Base.metadata.drop_all(db.engine)

@pytest.fixture(autouse=True)
def clean_db(setup_database):
    """Clean up tables before each test to ensure isolation."""
    session = db.get_session()
    try:
        # Delete in order of dependencies
        session.query(LoginLog).delete()
        session.query(DualAuthToken).delete()
        session.query(Student).delete()
        session.query(User).delete()
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@pytest.fixture
def user_service():
    return UserService()

@pytest.fixture
def auth_service():
    return AuthService()

def test_create_user(user_service):
    success, msg = user_service.create_user(
        identifier="admin1",
        account="admin1",
        password="password123",
        identity=Identity.ADMIN
    )
    assert success is True
    assert msg == "User created successfully"
    
    # Try duplicate identifier
    success, msg = user_service.create_user(
        identifier="admin1",
        account="admin2",
        password="password123",
        identity=Identity.ADMIN
    )
    assert success is False
    assert "already exists" in msg

    # Try duplicate account
    success, msg = user_service.create_user(
        identifier="admin2",
        account="admin1",
        password="password123",
        identity=Identity.ADMIN
    )
    assert success is False
    assert "already exists" in msg

def test_create_student(user_service):
    success, msg = user_service.create_user(
        identifier="student1",
        account="student1",
        password="password123",
        identity=Identity.STUDENT,
        name="John Doe",
        major_id=101,
        class_id=2024,
        enrollment_time="2024-09-01"
    )
    assert success is True
    
    session = db.get_session()
    student = session.query(Student).filter_by(identifier="student1").first()
    assert student is not None
    assert student.name == "John Doe"
    assert student.major_id == 101
    session.close()

def test_login_success_and_logging(auth_service, user_service):
    user_service.create_user("user1", "user1", "pass123", Identity.TEACHER)
    
    status, user, msg = auth_service.login("user1", "pass123")
    assert status == 3
    assert user.account == "user1"
    
    # Check log
    session = db.get_session()
    log = session.query(LoginLog).filter_by(identifier="user1").first()
    assert log is not None
    assert log.succeed is True
    assert log.detail == "Login Success"
    session.close()

def test_login_failure_and_banning(auth_service, user_service):
    user_service.create_user("target", "target", "secret", Identity.GUARD)
    
    # 4 failed attempts
    for _ in range(4):
        status, user, msg = auth_service.login("target", "wrong")
        assert status == 1
    
    session = db.get_session()
    user = session.query(User).filter_by(account="target").first()
    assert user.num_consecutive_failure == 4
    assert user.banned is False
    session.close()
    
    # 5th failed attempt
    status, user, msg = auth_service.login("target", "wrong")
    assert status == 1
    
    session = db.get_session()
    user = session.query(User).filter_by(account="target").first()
    assert user.banned is True
    session.close()
    
    # Attempt login after banned
    status, user, msg = auth_service.login("target", "secret")
    assert status == 2
    assert "banned" in msg

def test_2fa_verification(auth_service, user_service):
    user_service.create_user("2fa_user", "2fa_user", "pass", Identity.ADMIN)
    
    # Enable 2FA for this user manually for testing
    session = db.get_session()
    user = session.query(User).filter_by(account="2fa_user").first()
    user.dual_authentication = True
    
    # Create a token
    token = DualAuthToken(identifier=user.identifier, token="123456")
    session.add(token)
    session.commit()
    session.close()
    
    # Login should return status 4
    status, user, msg = auth_service.login("2fa_user", "pass")
    assert status == 4
    
    # Verify 2FA
    assert auth_service.verify_2fa("2fa_user", "123456") is True
    assert auth_service.verify_2fa("2fa_user", "wrong_token") is False

def test_login_unknown_user(auth_service):
    status, user, msg = auth_service.login("ghost", "any")
    assert status == 0
    assert "not exist" in msg

