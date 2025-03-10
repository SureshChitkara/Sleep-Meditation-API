import os

class Config:
    # Database configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("DB_NAME", "sleep_meditation")

    # Secret key for JWT authentication
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key")

    # Debug mode
    DEBUG = True
