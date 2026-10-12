import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
<<<<<<< HEAD
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Admin#123456")
=======
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
>>>>>>> 823532235b4f7d7c6b84d50d9fa70b9678f3d37a
    DB_NAME = os.getenv("DB_NAME", "enrutate_db")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 8001))
