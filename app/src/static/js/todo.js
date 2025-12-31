/**
 * TodoApp JavaScript Class
 * Manages task list operations and client-side functionality
 */

class TodoApp {
    constructor() {
        this.tasks = [];
        this.storage = new LocalStorageManager();
        this.taskIdCounter = 1;
        
        // Initialize the app
        this.init();
    }
    
    /**
     * Initialize the TodoApp
     */
    init() {
        // Load existing tasks from storage
        this.loadTasks();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Render initial task list
        this.renderTasks();
    }
    
    /**
     * Load tasks from local storage
     */
    loadTasks() {
        const savedTasks = this.storage.loadTasks();
        if (savedTasks && Array.isArray(savedTasks)) {
            this.tasks = savedTasks;
            // Update counter to avoid ID conflicts
            if (this.tasks.length > 0) {
                const maxId = Math.max(...this.tasks.map(task => parseInt(task.id.replace('task-', '')) || 0));
                this.taskIdCounter = maxId + 1;
            }
        }
    }
    
    /**
     * Generate a unique task ID
     * @returns {string} Unique task identifier
     */
    generateTaskId() {
        return `task-${this.taskIdCounter++}`;
    }
    
    /**
     * Add a new task to the list
     * @param {string} description - Task description
     * @returns {Promise<Object|null>} Created task object or null if invalid
     */
    async addTask(description) {
        // Validate task description (Requirements 1.2)
        if (!this.validateTaskDescription(description)) {
            this.showError('Please enter a valid task description.');
            return null;
        }
        
        try {
            // Call API endpoint via fetch (Requirements 1.1)
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    description: description.trim()
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Failed to create task:', errorData.error);
                this.showError('Failed to create task. Please try again.');
                return null;
            }
            
            const newTask = await response.json();
            
            // Add to local tasks array
            this.tasks.push(newTask);
            
            // Save to storage
            this.saveTasks();
            
            // Update UI immediately after operation (Requirements 1.1)
            this.renderTasks();
            
            return newTask;
            
        } catch (error) {
            console.error('Network error creating task:', error);
            this.showError('Network error. Task saved locally but may not sync until connection is restored.');
            
            // Fallback to local-only creation
            const newTask = {
                id: this.generateTaskId(),
                description: description.trim(),
                completed: false,
                created_at: new Date().toISOString()
            };
            
            this.tasks.push(newTask);
            this.saveTasks();
            this.renderTasks();
            
            return newTask;
        }
    }
    
    /**
     * Toggle task completion status
     * @param {string} taskId - ID of task to toggle
     * @returns {Promise<boolean>} Success status
     */
    async toggleTask(taskId) {
        const task = this.findTaskById(taskId);
        if (!task) {
            this.showError('Task not found.');
            return false;
        }
        
        const newCompletedStatus = !task.completed;
        
        try {
            // Call API endpoint via fetch to persist changes (Requirements 3.1, 3.4)
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    completed: newCompletedStatus
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Failed to update task:', errorData.error);
                this.showError('Failed to update task. Please try again.');
                return false;
            }
            
            // Update local task status
            task.completed = newCompletedStatus;
            
            // Save to storage
            this.saveTasks();
            
            // Update visual appearance for completed tasks (Requirements 3.2)
            this.renderTasks();
            
            return true;
            
        } catch (error) {
            console.error('Network error updating task:', error);
            this.showError('Network error. Task updated locally but may not sync until connection is restored.');
            
            // Fallback to local-only update
            task.completed = newCompletedStatus;
            this.saveTasks();
            this.renderTasks();
            return true;
        }
    }
    
    /**
     * Delete a task from the list
     * @param {string} taskId - ID of task to delete
     * @returns {Promise<boolean>} Success status
     */
    async deleteTask(taskId) {
        const taskIndex = this.tasks.findIndex(task => task.id === taskId);
        if (taskIndex === -1) {
            this.showError('Task not found.');
            return false;
        }
        
        try {
            // Call API endpoint via fetch to persist changes (Requirements 4.1, 4.2, 4.3)
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Failed to delete task:', errorData.error);
                this.showError('Failed to delete task. Please try again.');
                return false;
            }
            
            // Remove task from UI and storage (Requirements 4.1, 4.2, 4.3)
            this.tasks.splice(taskIndex, 1);
            
            // Save to storage
            this.saveTasks();
            
            // Re-render tasks
            this.renderTasks();
            
            return true;
            
        } catch (error) {
            console.error('Network error deleting task:', error);
            this.showError('Network error. Task deleted locally but may not sync until connection is restored.');
            
            // Fallback to local-only deletion
            this.tasks.splice(taskIndex, 1);
            this.saveTasks();
            this.renderTasks();
            return true;
        }
    }
    
    /**
     * Find task by ID
     * @param {string} taskId - Task ID to find
     * @returns {Object|null} Task object or null if not found
     */
    findTaskById(taskId) {
        return this.tasks.find(task => task.id === taskId) || null;
    }
    
    /**
     * Validate task description
     * @param {string} description - Description to validate
     * @returns {boolean} True if valid, false otherwise
     */
    validateTaskDescription(description) {
        // Check if description exists and is not empty or whitespace-only
        return description && 
               typeof description === 'string' && 
               description.trim().length > 0;
    }
    
    /**
     * Save tasks to storage
     */
    saveTasks() {
        this.storage.saveTasks(this.tasks);
    }
    
    /**
     * Render tasks in the UI
     */
    renderTasks() {
        const taskList = document.getElementById('task-list');
        if (!taskList) {
            console.warn('Task list element not found');
            return;
        }
        
        // Clear existing tasks
        taskList.innerHTML = '';
        
        // Show empty state if no tasks
        if (this.tasks.length === 0) {
            this.showEmptyState();
            return;
        }
        
        // Render each task
        this.tasks.forEach(task => {
            const taskElement = this.createTaskElement(task);
            taskList.appendChild(taskElement);
        });
    }
    
    /**
     * Create DOM element for a task
     * @param {Object} task - Task object
     * @returns {HTMLElement} Task DOM element
     */
    createTaskElement(task) {
        const taskDiv = document.createElement('div');
        taskDiv.className = `task-item ${task.completed ? 'completed' : ''}`;
        taskDiv.dataset.taskId = task.id;
        
        taskDiv.innerHTML = `
            <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''}>
            <span class="task-description">${this.escapeHtml(task.description)}</span>
            <button class="delete-btn" type="button">Delete</button>
        `;
        
        return taskDiv;
    }
    
    /**
     * Show empty state message
     */
    showEmptyState() {
        const taskList = document.getElementById('task-list');
        if (taskList) {
            taskList.innerHTML = '<div class="empty-state">No tasks yet. Add your first task above!</div>';
        }
    }
    
    /**
     * Show error message to user
     * @param {string} message - Error message to display
     */
    showError(message) {
        // Remove any existing error messages
        this.clearError();
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        const container = document.querySelector('.todo-container') || document.querySelector('.container');
        if (container) {
            container.insertBefore(errorDiv, container.firstChild);
            
            // Auto-remove error after 5 seconds
            setTimeout(() => {
                this.clearError();
            }, 5000);
        }
    }
    
    /**
     * Clear error messages
     */
    clearError() {
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
    }
    
    /**
     * Clear input field and focus it
     */
    clearInput() {
        const input = document.getElementById('task-input');
        if (input) {
            input.value = '';
            input.focus();
        }
    }
    
    /**
     * Set up event listeners for UI interactions
     */
    setupEventListeners() {
        // Task form submission - prevent default and call API endpoints via fetch
        const taskForm = document.getElementById('task-form');
        if (taskForm) {
            taskForm.addEventListener('submit', async (e) => {
                e.preventDefault(); // Prevent default form submission
                const input = document.getElementById('task-input');
                if (input && input.value.trim()) {
                    await this.addTask(input.value);
                    this.clearInput(); // Clear input and focus for next entry (Requirements 1.3)
                }
            });
        }
        
        // Task list interactions (using event delegation)
        const taskList = document.getElementById('task-list');
        if (taskList) {
            taskList.addEventListener('click', async (e) => {
                const taskItem = e.target.closest('.task-item');
                if (!taskItem) return;
                
                const taskId = taskItem.dataset.taskId;
                
                if (e.target.classList.contains('task-checkbox')) {
                    // Add click handlers for task checkboxes (Requirements 3.1, 3.2, 3.4)
                    await this.toggleTask(taskId);
                } else if (e.target.classList.contains('delete-btn')) {
                    await this.deleteTask(taskId);
                }
            });
        }
    }
    
    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

/**
 * LocalStorageManager Class
 * Handles saving and loading tasks from browser local storage
 */
class LocalStorageManager {
    constructor() {
        this.storageKey = 'todo-app-tasks';
        this.warningShown = false;
    }
    
    /**
     * Check if localStorage is available
     * @returns {boolean} True if available, false otherwise
     */
    isAvailable() {
        try {
            const test = '__localStorage_test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (e) {
            return false;
        }
    }
    
    /**
     * Save tasks to localStorage
     * @param {Array} tasks - Array of task objects
     */
    saveTasks(tasks) {
        if (!this.isAvailable()) {
            this.showStorageWarning();
            return;
        }
        
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(tasks));
        } catch (e) {
            console.error('Failed to save tasks to localStorage:', e);
            this.showStorageWarning();
        }
    }
    
    /**
     * Load tasks from localStorage
     * @returns {Array|null} Array of tasks or null if not available
     */
    loadTasks() {
        if (!this.isAvailable()) {
            this.showStorageWarning();
            return null;
        }
        
        try {
            const tasksJson = localStorage.getItem(this.storageKey);
            return tasksJson ? JSON.parse(tasksJson) : [];
        } catch (e) {
            console.error('Failed to load tasks from localStorage:', e);
            this.showStorageWarning();
            return null;
        }
    }
    
    /**
     * Show warning when localStorage is unavailable
     */
    showStorageWarning() {
        if (this.warningShown) return;
        
        console.warn('Local storage is not available. Tasks will not be saved between sessions.');
        
        // Show user-visible warning
        const warningDiv = document.createElement('div');
        warningDiv.className = 'storage-warning';
        warningDiv.textContent = 'Warning: Unable to save tasks. Your tasks will be lost when you close the browser.';
        
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(warningDiv, container.firstChild);
        
        this.warningShown = true;
    }
}

// Initialize the TodoApp when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.todoApp = new TodoApp();
});