"""
Help routes blueprint for todo app
"""

from flask import Blueprint, render_template, abort

help_bp = Blueprint('help', __name__)


@help_bp.route('/help')
def help_page():
    """Render the help page"""
    try:
        return render_template('help.html')
    except Exception as e:
        # Log the error for debugging (in production, use proper logging)
        print(f"Error rendering help page: {str(e)}")
        abort(500)