"""
Flask application factory
"""

from flask import Flask, render_template


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
    from .routes.contact import contact_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(contact_bp)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404 if app.config.get('TESTING') else render_template('index.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app