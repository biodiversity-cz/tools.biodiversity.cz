from flask import Flask
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .routes.main import main_bp
    from .routes.herbarium import herbarium_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(herbarium_bp, url_prefix='/herbarium')

    return app
