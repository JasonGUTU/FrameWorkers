# Main Flask application for Frameworks Backend

from flask import Flask
from flask_cors import CORS
from .task_stack import create_blueprint
from .assistant import create_assistant_blueprint


def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Enable CORS for frontend integration
    CORS(app)
    
    # Load configuration if provided
    if config:
        app.config.update(config)
    
    # Register blueprints
    # Task Stack routes (existing)
    task_bp = create_blueprint()
    app.register_blueprint(task_bp)
    
    # Assistant routes (new - isolated)
    assistant_bp = create_assistant_blueprint()
    app.register_blueprint(assistant_bp)
    
    return app


if __name__ == '__main__':
    app = create_app()
    # Keep local shortcut consistent with run.py default.
    app.run(host='0.0.0.0', port=5002, debug=True)
