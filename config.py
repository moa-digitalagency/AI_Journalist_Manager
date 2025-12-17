import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    ELEVEN_LABS_API_KEY = os.environ.get('ELEVEN_LABS_API_KEY')
    
    SUMMARY_HOUR = int(os.environ.get('SUMMARY_HOUR', 8))
    SUMMARY_MINUTE = int(os.environ.get('SUMMARY_MINUTE', 0))
