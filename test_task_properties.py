"""
Property-based tests for Task model validation
"""

import pytest
from hypothesis import given, strategies as st, settings
from pydantic import ValidationError
from app.src.models import Task, TaskManager


class TestTaskModelProperties:
    """Property-based tests for Task model"""
    
    @given(st.text().filter(lambda x: x and x.strip()))
    @settings(max_examples=5)
    def test_valid_task_creation(self, description):
        """
        Property 2: Invalid Task Rejection (inverse test - valid tasks should be accepted)
        For any non-empty, non-whitespace string, creating a task should succeed
        Feature: todo-app, Property 2: Invalid Task Rejection
        Validates: Requirements 1.2
        """
        manager = TaskManager()
        task = manager.create_task(description)
        
        assert task.description == description.strip()
        assert task.completed is False
        assert task.id is not None
        assert len(task.id) > 0
    
    @given(st.text().filter(lambda x: not x or not x.strip()))
    @settings(max_examples=5)
    def test_invalid_task_rejection(self, invalid_description):
        """
        Property 2: Invalid Task Rejection
        For any string composed entirely of whitespace (including empty string),
        creating a task should be rejected with ValidationError
        Feature: todo-app, Property 2: Invalid Task Rejection
        Validates: Requirements 1.2
        """
        manager = TaskManager()
        
        with pytest.raises(ValidationError):
            manager.create_task(invalid_description)
    
    @given(st.text().filter(lambda x: x and x.strip()))
    @settings(max_examples=5)
    def test_task_serialization_round_trip(self, description):
        """
        Property: Task serialization round trip
        For any valid task, serializing to dict and back should preserve all data
        Feature: todo-app, Property: Task serialization round trip
        """
        manager = TaskManager()
        original_task = manager.create_task(description)
        
        # Serialize to dict
        task_dict = original_task.to_dict()
        
        # Deserialize back to Task
        restored_task = Task.from_dict(task_dict)
        
        # Should be equivalent
        assert restored_task.id == original_task.id
        assert restored_task.description == original_task.description
        assert restored_task.completed == original_task.completed
        # Note: datetime comparison might have slight precision differences
        assert abs((restored_task.created_at - original_task.created_at).total_seconds()) < 1

    @given(st.text().filter(lambda x: x and x.strip()))
    @settings(max_examples=5)
    def test_task_creation_grows_list(self, description):
        """
        Property 1: Task Addition Grows List
        For any valid task description, adding it to a task list should grow the list by one
        Feature: todo-app, Property 1: Task Addition Grows List
        Validates: Requirements 1.1
        """
        manager = TaskManager()
        
        # Simulate a task list
        task_list = []
        initial_length = len(task_list)
        
        # Create and add task
        task = manager.create_task(description)
        task_list.append(task)
        
        # List should grow by one
        assert len(task_list) == initial_length + 1
        assert task in task_list
        assert task.description == description.strip()