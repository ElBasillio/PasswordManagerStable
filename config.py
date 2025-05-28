import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'passwords.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Encryption key for passwords
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or Fernet.generate_key()
    
    # Налаштування для статичних файлів та шаблонів
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    
    # Налаштування безпеки
    SESSION_COOKIE_SECURE = False  # Змініть на True для production
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False  # Змініть на True для production
    REMEMBER_COOKIE_HTTPONLY = True 