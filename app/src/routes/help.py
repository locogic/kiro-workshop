"""
Help routes blueprint for todo app
"""

from flask import Blueprint, render_template

help_bp = Blueprint('help', __name__)


@help_bp.route('/help')
def help_page():
    """Render the help page"""
    return render_template('help.html')