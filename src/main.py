import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from src.database.db import db
from src.ui.login_window import LoginWindow
from src.services.user_service import UserService
from src.database.models import Identity

def seed_data():
    """Seed initial data if empty"""
    session = db.get_session()
    user_service = UserService(session)
    # Check if admin exists
    admin = user_service.get_user_by_account("admin")
    if not admin:
        print("Seeding admin user...")
        user_service.create_user("admin", "admin", "admin123", Identity.ADMIN)
    session.close()

def main():
    # Initialize DB
    db.init_db()
    
    # Seed Data
    seed_data()
    
    app = QApplication(sys.argv)
    
    window = LoginWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
