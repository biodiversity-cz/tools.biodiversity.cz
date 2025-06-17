import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULT_FOLDER = os.path.join(BASE_DIR, 'results')

class Config:
    UPLOAD_FOLDER = UPLOAD_FOLDER
    RESULT_FOLDER = RESULT_FOLDER

