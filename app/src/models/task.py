"""
Task model with Pydantic validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import uuid


class Task(BaseModel):
    """Task model with validation"""
    
    id: str = Field(..., description="Unique identifier for the task")
    description: str = Field(..., min_length=1, description="Task description")
    completed: bool = Field(default=False, description="Completion status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate task description is not empty or whitespace-only"""
        if not v or not v.strip():
            raise ValueError('Task description cannot be empty or whitespace-only')
        return v.strip()
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create task from dictionary"""
        # Handle datetime parsing if it's a string
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class TaskManager:
    """Handles task operations and validation"""
    
    def create_task(self, description: str) -> Task:
        """Create a new task with validation"""
        task_id = self.generate_task_id()
        return Task(id=task_id, description=description)
    
    def validate_task_description(self, description: str) -> bool:
        """Validate task description is not empty or whitespace-only"""
        return bool(description and description.strip())
    
    def generate_task_id(self) -> str:
        """Generate unique task identifier"""
        return str(uuid.uuid4())