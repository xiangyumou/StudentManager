from sqlalchemy.orm import Session
from src.database.models import User, Identity, Student
from src.database.db import db
from src.utils.logger import setup_logger
import bcrypt

logger = setup_logger(__name__)

class UserService:
    def __init__(self):
        pass

    def create_user(self, identifier, account, password, identity: Identity, **kwargs):
        """
        Creates a new user. 
        **kwargs handles specific role data (e.g. major_id for students)
        """
        session = db.get_session()
        try:
            # Check if user exists
            existing_user = session.query(User).filter((User.identifier == identifier) | (User.account == account)).first()
            if existing_user:
                return False, "User already exists"

            # Hash password
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            new_user = User(
                identifier=identifier,
                account=account,
                password=hashed_pw,
                identity=identity
            )
            session.add(new_user)
            
            # Handle specifics (Example: Student)
            if identity == Identity.STUDENT:
                student = Student(
                    identifier=identifier,
                    major_id=kwargs.get('major_id', 0),
                    name=kwargs.get('name', ''),
                    class_id=kwargs.get('class_id', 0),
                    enrollment_time=kwargs.get('enrollment_time', '')
                )
                session.add(student)
            
            session.commit()
            logger.info(f"User {account} created successfully.")
            return True, "User created successfully"
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating user: {e}")
            return False, f"Server Error: {e}"
        finally:
            session.close()

    def get_user_by_account(self, account):
        session = db.get_session()
        try:
            return session.query(User).filter_by(account=account).first()
        finally:
            session.close()
