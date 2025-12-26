from PyQt5.QtWidgets import QDialog, QMessageBox, QLineEdit
from PyQt5.uic import loadUi
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.database.models import Identity
import os

# Assuming we might want to load UI from .ui file or build it here. 
# For "Best Practice" refactor without .ui files dependence (to avoid path issues), 
# I will build a simple UI class or load the existing one if path is correct.
# Given the user wants "better implementation", separating logic from UI definition is key.
# But reusing existing .ui files saves time on layout. 
# Let's try to load the existing .ui file but mapped correctly, 
# OR build a clean one code-only to ensure it works without complex path resolution for now.
# Let's stick to code-only for the refactor to ensure it runs standalone easily.

from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QPushButton, QFormLayout)

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System - Login")
        self.setGeometry(100, 100, 300, 200)
        
        self.auth_service = AuthService()

        layout = QVBoxLayout()
        
        self.form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.form_layout.addRow("Account:", self.username_input)
        self.form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(self.form_layout)
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)
        
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)

    def handle_login(self):
        account = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        status, user, msg = self.auth_service.login(account, password)
        
        self.status_label.setText(msg)
        
        if status == 3: # Success
            self.accept()
            # Here we would open the main window based on identity
            # For now, just show success info
            QMessageBox.information(self, "Success", f"Welcome {user.account} ({user.identity.name})")
        elif status == 4: # 2FA
             QMessageBox.information(self, "2FA Required", "Two-factor authentication is required (not fully implemented in UI refactor yet).")
        else:
            QMessageBox.warning(self, "Login Failed", msg)
