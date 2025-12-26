from sqlalchemy.orm import Session
from src.database.models import User, Identity, Student
from src.database.db import db
from src.utils.logger import setup_logger
import bcrypt

logger = setup_logger(__name__)

class UserService:
    def __init__(self, session: Session = None):
        self.session = session or db.get_session()

    def create_user(self, identifier, account, password, identity: Identity, **kwargs):
        """
        Creates a new user. 
        **kwargs handles specific role data (e.g. major_id for students)
        """
        try:
            # Check if user exists
            existing_user = self.session.query(User).filter((User.identifier == identifier) | (User.account == account)).first()
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
            self.session.add(new_user)
            
            # Handle specifics (Example: Student)
            if identity == Identity.STUDENT:
                student = Student(
                    identifier=identifier,
                    major_id=kwargs.get('major_id', 0),
                    name=kwargs.get('name', ''),
                    class_id=kwargs.get('class_id', 0),
                    enrollment_time=kwargs.get('enrollment_time', '')
                )
                self.session.add(student)
            
            self.session.commit()
            logger.info(f"User {account} created successfully.")
            return True, "User created successfully"
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating user: {e}")
            return False, f"Server Error: {e}"
        finally:
            self.session.close()

    def get_user_by_account(self, account):
        return self.session.query(User).filter_by(account=account).first()
