// WebSocket connection
let ws = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// Toast notification system
const toast = {
    show: function(message, type = 'info') {
        const toastElement = document.createElement('div');
        toastElement.className = `toast ${type}`;
        toastElement.textContent = message;
        document.body.appendChild(toastElement);
        
        setTimeout(() => {
            toastElement.remove();
        }, 3000);
    },
    success: function(message) {
        this.show(message, 'success');
    },
    error: function(message) {
        this.show(message, 'error');
    }
};

// WebSocket connection management
function connectWebSocket() {
    if (ws) {
        ws.close();
    }

    ws = new WebSocket(`ws://${window.location.host}/ws`);
    
    ws.onopen = () => {
        console.log('Connected to WebSocket');
        reconnectAttempts = 0;
        // Request initial status
        ws.send(JSON.stringify({ action: 'get_status' }));
        ws.send(JSON.stringify({ action: 'get_tasks' }));
        toast.success('Connected to server');
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
            toast.error('Error processing server message');
        }
    };

    ws.onclose = () => {
        console.log('Disconnected from WebSocket');
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            reconnectAttempts++;
            setTimeout(connectWebSocket, 5000 * reconnectAttempts);
            toast.error(`Connection lost. Attempting to reconnect (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
        } else {
            toast.error('Failed to connect to server. Please refresh the page.');
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        toast.error('Connection error occurred');
    };
}

// Handle WebSocket messages
function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'status':
            updateSystemStatus(data.data);
            break;
        case 'tasks':
            updateTasksList(data.data);
            break;
        case 'error':
            toast.error(data.message);
            break;
        case 'success':
            toast.success(data.message);
            break;
        default:
            console.warn('Unknown message type:', data.type);
    }
}

// Update system status display
function updateSystemStatus(status) {
    document.getElementById('system-status').textContent = status.status;
    
    // Update components status
    const componentsDiv = document.getElementById('components-status');
    componentsDiv.innerHTML = Object.entries(status.components)
        .map(([name, status]) => `
            <div class="flex items-center">
                <span class="status-indicator status-${status === 'running' ? 'running' : 'error'}"></span>
                <span>${name}</span>
            </div>
        `).join('');

    // Update resource usage
    const resourcesDiv = document.getElementById('resource-usage');
    resourcesDiv.innerHTML = Object.entries(status.resources)
        .map(([name, value]) => `
            <div class="flex justify-between">
                <span>${name}</span>
                <span>${value}</span>
            </div>
        `).join('');
}

// Update tasks list display
function updateTasksList(tasks) {
    const tasksDiv = document.getElementById('tasks-list');
    tasksDiv.innerHTML = tasks.map(task => `
        <div class="task-card bg-gray-800 rounded p-4">
            <div class="flex justify-between items-center mb-2">
                <h3 class="font-semibold">${task.name}</h3>
                <span class="px-2 py-1 rounded text-sm ${
                    task.status === 'completed' ? 'bg-green-500' :
                    task.status === 'in_progress' ? 'bg-blue-500' :
                    'bg-yellow-500'
                }">${task.status}</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2.5">
                <div class="bg-blue-600 h-2.5 rounded-full" style="width: ${task.progress}%"></div>
            </div>
            <div class="mt-2 flex justify-end space-x-2">
                <button onclick="updateTask(${task.id}, 'in_progress')" class="text-blue-400 hover:text-blue-300" aria-label="Start task">
                    <i class="fas fa-play"></i>
                </button>
                <button onclick="updateTask(${task.id}, 'completed')" class="text-green-400 hover:text-green-300" aria-label="Complete task">
                    <i class="fas fa-check"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// Task management functions
function updateTask(taskId, status) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            action: 'update_task',
            task_id: taskId,
            updates: { status: status }
        }));
    } else {
        toast.error('Not connected to server');
    }
}

function refreshStatus() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'get_status' }));
        ws.send(JSON.stringify({ action: 'get_tasks' }));
    } else {
        toast.error('Not connected to server');
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    connectWebSocket();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'r' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            refreshStatus();
        }
    });
}); 