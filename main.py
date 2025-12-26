import sys
import os

# Add src to path is not strictly needed if running from root as package, but ensuring . is in path helps
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from src.database.db import db
from src.ui.login_window import LoginWindow
from src.services.user_service import UserService
from src.database.models import Identity

import argparse

def seed_data(reset_admin=False):
    """Seed initial data if empty. If reset_admin is True, forces admin password to admin123."""
    user_service = UserService()
    # Check if admin exists
    admin = user_service.get_user_by_account("admin")
    if not admin:
        print("Seeding admin user...")
        user_service.create_user("admin", "admin", "admin123", Identity.ADMIN)
    elif reset_admin:
        print("Resetting admin password to 'admin123'...")
        from src.database.db import db
        import bcrypt
        session = db.get_session()
        try:
            admin_user = session.query(User).filter_by(account="admin").first()
            hashed_pw = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin_user.password = hashed_pw
            admin_user.banned = False
            admin_user.num_consecutive_failure = 0
            session.commit()
            print("Admin password reset successfully.")
        except Exception as e:
            session.rollback()
            print(f"Error resetting admin: {e}")
        finally:
            session.close()
    else:
        print("Admin user already exists. Use --reset-admin to reset password.")

def main():
    parser = argparse.ArgumentParser(description="Student Management System")
    parser.add_argument("--reset-admin", action="store_true", help="Reset admin password to admin123")
    args = parser.parse_args()

    # Initialize DB
    db.init_db()
    
    # Seed Data
    seed_data(reset_admin=args.reset_admin)
    
    app = QApplication(sys.argv)
    
    window = LoginWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
