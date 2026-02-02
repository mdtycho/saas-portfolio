# The "Master" entry point that runs everything
from flask import Flask, render_template
import os


def create_app():
    app = Flask(__name__)

   # Check if we are in production (Coolify) or local
    env = os.environ.get('FLASK_ENV', 'development')

    if env == 'production':
        # On the server, we enforce the domain
        app.config['SERVER_NAME'] = 'zatools.co.za'
    else:
        # Locally, we don't set SERVER_NAME so localhost:8000 still works.
        # BUT: Subdomains won't work locally unless you edit /etc/hosts.
        pass

    # Register blueprints
    from apps.z83_form.routes import z83_bp
    
    if env == 'production':
        # Production: Use the subdomain
        app.register_blueprint(z83_bp, subdomain='z83')
    else:
        # Local: Just use a path prefix so you can test it easily
        # Access at: http://localhost:3000/z83
        app.register_blueprint(z83_bp, url_prefix='/z83')



    @app.route('/')
    def index():
        return "<h1>SaaS Portfolio Active</h1><a href='/z83'>Go to Z83 Editor</a>"

    return app

# We create the 'app' variable globally so Gunicorn can find it via "app:app"
app = create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=3000)
