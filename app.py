# The "Master" entry point that runs everything
from flask import Flask
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    from apps.z83_form import z83_bp
    app.register_blueprint(z83_bp, url_prefix='/z83')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config.get('DEBUG', False))
