"""
Main routes blueprint for todo app
"""

from flask import Blueprint, render_template, request, jsonify
from pydantic import ValidationError
from ..models import TaskManager

main_bp = Blueprint('main', __name__)
task_manager = TaskManager()


@main_bp.route('/')
def index():
    """Render the main todo interface"""
    return render_template('index.html')


@main_bp.route('/api/tasks', methods=['POST'])
def create_task():
    """API endpoint for creating tasks"""
    try:
        data = request.get_json()
        if not data or 'description' not in data:
            return jsonify({'error': 'Description is required'}), 400
        
        task = task_manager.create_task(data['description'])
        return jsonify(task.to_dict()), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@main_bp.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """API endpoint for updating task completion status"""
    try:
        data = request.get_json()
        if not data or 'completed' not in data:
            return jsonify({'error': 'Completed status is required'}), 400
        
        # For now, return success - actual task storage will be client-side
        return jsonify({
            'id': task_id,
            'completed': data['completed'],
            'message': 'Task updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@main_bp.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """API endpoint for deleting tasks"""
    try:
        # For now, return success - actual task storage will be client-side
        return jsonify({
            'id': task_id,
            'message': 'Task deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500