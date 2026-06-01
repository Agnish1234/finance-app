import os
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()

class Config:
    """Base configuration class."""
    # Secret key for session security (must be overridden in production)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database URL: can be SQLite locally, PostgreSQL on Render
    # Default to SQLite for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    
    # Turn off modification tracking to save memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False