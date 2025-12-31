"""
Flask application factory
"""

from flask import Flask


def create_app(config=None):
    """
    Application factory pattern for creating Flask app instances
    
    Args:
        config: Configuration object or dictionary
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configure the app
    if config:
        app.config.update(config)
    
    # Initialize extensions
    # Extensions will be initialized here as needed
    
    # Register blueprints
    from .routes.main import main_bp
    from .routes.help import help_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(help_bp)
    
    return app