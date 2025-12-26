from sqlalchemy.orm import Session
from src.database.models import User, LoginLog, DualAuthToken
from src.database.db import db
from src.utils.logger import setup_logger
import bcrypt
from datetime import datetime

logger = setup_logger(__name__)

class AuthService:
    def __init__(self, session: Session = None):
        self.session = session or db.get_session()

    def login(self, account, password):
        """
        Returns:
            status_code (int):
                0: Account not found
                1: Password error
                2: Account banned
                3: Login Success
                4: Login Success (Wait for 2FA)
            user_obj (User): User object if relevant, else None
            message (str): Debug/User message
        """
        try:
            user = self.session.query(User).filter_by(account=account).first()
            
            if not user:
                self._log_attempt(None, False, "Account User Not Found", 0)
                return 0, None, "Account does not exist"
            
            if user.banned:
                self._log_attempt(user.identifier, False, "Account Banned", 2)
                return 2, None, "Account is banned"
            
            # Check Password
            # Note: For migration compatibility, we should nominally check if it matches plain text 
            # if we didn't migrate passwords. But for this refactor, we assume new DB.
            # If migrating, we'd need a "is_legacy_hash" check.
            if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                # Increment failure count
                user.num_consecutive_failure += 1
                if user.num_consecutive_failure >= 5: # Ban after 5 attempts
                    user.banned = True
                self.session.commit()
                self._log_attempt(user.identifier, False, "Password Incorrect", 1)
                return 1, None, "Incorrect password"

            # Reset failure count on success
            user.num_consecutive_failure = 0
            
            if user.dual_authentication:
                self.session.commit()
                return 4, user, "Dual Authentication Required"
            
            self.session.commit()
            self._log_attempt(user.identifier, True, "Login Success", 3)
            return 3, user, "Login Successful"
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return -1, None, f"Server Error: {e}"
        finally:
            self.session.close()

    def verify_2fa(self, identifier, token):
        try:
            auth_token_entry = self.session.query(DualAuthToken).filter_by(identifier=identifier).first()
            if auth_token_entry and auth_token_entry.token == token:
                self._log_attempt(identifier, True, "2FA Success", 6)
                return True
            self._log_attempt(identifier, False, "2FA Failed", 5)
            return False
        finally:
            self.session.close()

    def _log_attempt(self, identifier, success, detail, signal):
        try:
            log = LoginLog(
                identifier=identifier,
                succeed=success,
                detail=detail,
                dual_authentication=(signal >= 4)
            )
            # Create a new session for logging to ensure it persists even if main transaction fails
            log_session = db.get_session()
            log_session.add(log)
            log_session.commit()
            log_session.close()
        except Exception as e:
            logger.error(f"Failed to write login log: {e}")
