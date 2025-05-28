from cryptography.fernet import Fernet
from base64 import b64encode, b64decode
import os
from flask import current_app

def get_key():
    """Get or create encryption key."""
    key = current_app.config.get('ENCRYPTION_KEY')
    if not key:
        key = Fernet.generate_key()
        current_app.config['ENCRYPTION_KEY'] = key
    return key

def encrypt_password(password):
    """Encrypt a password string."""
    f = Fernet(get_key())
    return b64encode(f.encrypt(password.encode())).decode()

def decrypt_password(encrypted_password):
    """Decrypt an encrypted password string."""
    f = Fernet(get_key())
    return f.decrypt(b64decode(encrypted_password)).decode() 