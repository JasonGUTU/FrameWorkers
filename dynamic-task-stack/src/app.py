# Main Flask application for Dynamic Task Stack

from flask import Flask
from flask_cors import CORS
from .routes import create_blueprint


def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Enable CORS for frontend integration
    CORS(app)
    
    # Load configuration if provided
    if config:
        app.config.update(config)
    
    # Register blueprint
    bp = create_blueprint()
    app.register_blueprint(bp)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
