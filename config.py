import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.environ.get('SECRET_KEY', 'skyhire-secret-key-light-blue-2026')
    
    # On Vercel / serverless environments, root is read-only so store writable DB and uploads in /tmp
    if IS_VERCEL:
        db_path = '/tmp/job_tracker.db'
        upload_folder = '/tmp/uploads/resumes'
    else:
        db_path = os.path.join(BASE_DIR, 'job_tracker.db')
        upload_folder = os.path.join(BASE_DIR, 'uploads', 'resumes')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"sqlite:///{db_path}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = upload_folder
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf'}

