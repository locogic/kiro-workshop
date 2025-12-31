"""
Contact routes for Todo App
"""

from flask import Blueprint, render_template, abort

# Create the contact blueprint
contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact')
def contact_page():
    """Render the contact page with support information"""
    try:
        return render_template('contact.html')
    except Exception as e:
        # Log the error for debugging (in production, use proper logging)
        print(f"Error rendering contact page: {str(e)}")
        abort(500)