# Student Management System

A Python-based Student Management System built with PyQt5 and SQLAlchemy.

## Features
-   User Authentication (Login, 2FA support)
-   Role-based Access Control (Student, Teacher, Admin, etc.)
-   Student Information Management
-   Secure Password Hashing
-   Data persistence with SQLite (extensible to MySQL)

## Structure
The project has been refactored into a modern structure:

```text
student-manage-system/
├── src/
│   ├── database/       # ORM Models (SQLAlchemy) & DB Connection
│   ├── services/       # Business Logic (Auth, User Management)
│   ├── ui/             # PyQt5 User Interface
│   ├── utils/          # Logging, Config
│   └── main.py         # Application Entry Point
├── tests/              # Unit Tests
├── requirements.txt    # Dependencies
└── README.md
```

## Setup & Running

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application**:
    ```bash
    python -m src.main
    ```
    *Note: On the first run, the system will automatically create a local `student_system.db` SQLite database and seed an initial Admin user.*

3.  **Initial Credentials**:
    -   **Account**: `admin`
    -   **Password**: `admin123`

## Configuration
Configuration is handled in `src/config.py`. You can create a `.env` file to override defaults:

```env
DATABASE_URL=sqlite:///student_system.db
DEBUG=True
SECRET_KEY=your-secret-key
```

## Testing
Run automated tests with `pytest`:
```bash
pytest tests/
```
