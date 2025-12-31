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
    # Check if this is a form submission (no JavaScript) or JSON API call
    if request.content_type and 'application/json' in request.content_type:
        # Handle JSON API request
        try:
            # Validate request content type
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body is required'}), 400
                
            if 'description' not in data:
                return jsonify({'error': 'Description field is required'}), 400
            
            description = data['description']
            if not isinstance(description, str):
                return jsonify({'error': 'Description must be a string'}), 400
                
            if not description.strip():
                return jsonify({'error': 'Description cannot be empty or whitespace only'}), 400
            
            task = task_manager.create_task(description)
            return jsonify(task.to_dict()), 201
            
        except ValidationError as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        except Exception as e:
            # Log the error for debugging (in production, use proper logging)
            print(f"Error creating task: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    else:
        # Handle form submission (progressive enhancement)
        try:
            description = request.form.get('description', '').strip()
            if not description:
                # Redirect back with error message (in a real app, use flash messages)
                return render_template('index.html', error='Please enter a task description'), 400
            
            task = task_manager.create_task(description)
            # Redirect back to main page (in a real app, show success message)
            return render_template('index.html', success=f'Task "{description}" added successfully'), 201
            
        except ValidationError as e:
            return render_template('index.html', error=f'Validation error: {str(e)}'), 400
        except Exception as e:
            # Log the error for debugging (in production, use proper logging)
            print(f"Error creating task: {str(e)}")
            return render_template('index.html', error='An error occurred while adding the task'), 500


@main_bp.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """API endpoint for updating task completion status"""
    try:
        # Validate task_id format
        if not task_id or not task_id.strip():
            return jsonify({'error': 'Task ID is required'}), 400
        
        # Validate request content type
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        if 'completed' not in data:
            return jsonify({'error': 'Completed field is required'}), 400
        
        completed = data['completed']
        if not isinstance(completed, bool):
            return jsonify({'error': 'Completed must be a boolean value'}), 400
        
        # For now, return success - actual task storage will be client-side
        return jsonify({
            'id': task_id,
            'completed': completed,
            'message': 'Task updated successfully'
        }), 200
        
    except Exception as e:
        # Log the error for debugging (in production, use proper logging)
        print(f"Error updating task {task_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@main_bp.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """API endpoint for deleting tasks"""
    try:
        # Validate task_id format
        if not task_id or not task_id.strip():
            return jsonify({'error': 'Task ID is required'}), 400
        
        # For now, return success - actual task storage will be client-side
        return jsonify({
            'id': task_id,
            'message': 'Task deleted successfully'
        }), 200
        
    except Exception as e:
        # Log the error for debugging (in production, use proper logging)
        print(f"Error deleting task {task_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500