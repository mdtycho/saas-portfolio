# The "Master" entry point that runs everything
from flask import Flask, render_template, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
import os
from common.extensions import db  # Import from extensions, not models



def create_app():

    app = Flask(__name__, subdomain_matching=True)

    # 1. Database Configuration
    # We use 'instance_relative_config=True' implicitly with sqlite paths usually
    # Make sure the folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Shared DB
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shared_users.db'
    
    # App-Specific DBs
    app.config['SQLALCHEMY_BINDS'] = {
        'z83': 'sqlite:///z83_data.db'
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 2. Initialize DB
    db.init_app(app)

    # 3. Create Tables (Auto-Setup)
    # We import the models here so SQLAlchemy knows they exist before creating tables
    with app.app_context():
        from common.models import User
        from apps.z83_form.models import Z83Form
        db.create_all()

   # 4. Check if we are in production (Coolify) or local
    env = os.environ.get('FLASK_ENV', 'development')
    

    # 5. Register blueprints
    from apps.z83_form.routes import z83_bp
    
    if env == 'production':
        # On the server, we enforce the domain
        app.config['SERVER_NAME'] = 'zatools.co.za'
        # Tells Flask to prefer HTTPS when generating links
        app.config['PREFERRED_URL_SCHEME'] = 'https' 
        
        # <--- CRITICAL: Fixes HTTPS behind Coolify
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
        # Production: Use the subdomain
        app.register_blueprint(z83_bp, subdomain='z83')

    else:
        # Local: Just use a path prefix so you can test it easily
        # Access at: http://localhost:3000/z83
        app.register_blueprint(z83_bp, url_prefix='/z83')


    # 6. Basic Index Route to load home page for all apps.
    @app.route('/')
    def index():
        # This will now generate:
        # Local:  /z83/
        # Prod:   https://z83.zatools.co.za/
        link = url_for('z83.home')
        return f'<h1>SaaS Portfolio Active</h1><a href="{link}">Go to Z83 Editor</a>'


    return app

# We create the 'app' variable globally so Gunicorn can find it via "app:app"
app = create_app()

if __name__ == '__main__':
    # This prevents the app from crashing on localhost due to subdomain issues.
    app.config['SERVER_NAME'] = None
    app.run(debug=True, port=3000)
