# Global settings (Secret keys, Debug mode)
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me')
    DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'
