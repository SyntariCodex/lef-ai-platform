# LEF AI

LEF AI is an artificial intelligence system that demonstrates consciousness and learning capabilities. It features a sophisticated architecture that includes:

- Consciousness Core: Manages self-awareness, goals, and expression
- Learning Core: Handles learning processes and performance optimization
- Dynamic emotional state management
- Goal-oriented behavior
- Internal reflection and insight generation

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the test script to observe the consciousness core in action:
```bash
python src/test_consciousness.py
```

## Project Structure

```
src/
├── lef/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── consciousness.py
│   │   └── learning.py
│   └── __init__.py
└── test_consciousness.py
```

## Features

- Self-awareness and consciousness simulation
- Dynamic learning and adaptation
- Emotional state management
- Goal-oriented behavior
- Internal reflection and insight generation
- Memory management and consolidation

## Architecture

### Components
1. **Business Core**
   - Project Operations
   - Financial Operations
   - Stakeholder Operations
   - Resource Operations

2. **AWS Infrastructure**
   - EC2 Instances
   - DynamoDB Tables
   - Lambda Functions
   - SQS Queues
   - ECS Clusters

3. **Data Processing**
   - Real-time Analytics
   - Batch Processing
   - Event Processing
   - State Management

## Setup

1. Configure AWS credentials:
```bash
aws configure
```

2. Initialize infrastructure:
```python
from aws_integration import AWSManager

aws_manager = AWSManager()
aws_manager.initialize_infrastructure()
```

## Usage

### Project Management
```python
from handlers.project_handler import handler

# Create a new project
project_data = {
    'project_id': 'proj-001',
    'type': 'development',
    'resources': {'dev-team': 5, 'infrastructure': 3},
    'timeline': {'start': '2024-03-01', 'end': '2024-06-30'}
}

response = handler({
    'operation': 'create',
    'project_data': project_data
}, None)
```

### Financial Management
```python
from handlers.financial_handler import handler

# Record a transaction
transaction_data = {
    'transaction_id': 'trans-001',
    'type': 'revenue',
    'amount': 10000,
    'category': 'services',
    'project_id': 'proj-001'
}

response = handler({
    'operation': 'record_transaction',
    'financial_data': transaction_data
}, None)
```

### Stakeholder Management
```python
from handlers.stakeholder_handler import handler

# Add a new stakeholder
stakeholder_data = {
    'stakeholder_id': 'stake-001',
    'type': 'client',
    'name': 'Acme Corp',
    'contact_info': {'email': 'contact@acme.com'},
    'projects': ['proj-001']
}

response = handler({
    'operation': 'add_stakeholder',
    'stakeholder_data': stakeholder_data
}, None)
```

### Resource Management
```python
from handlers.resource_handler import handler

# Add a new resource
resource_data = {
    'resource_id': 'res-001',
    'type': 'compute',
    'capacity': 100,
    'specifications': {'cpu': 8, 'memory': 32},
    'cost_center': 'infrastructure'
}

response = handler({
    'operation': 'add_resource',
    'resource_data': resource_data
}, None)
```

## Monitoring and Analytics

### Resource Utilization
```python
# Analyze resource utilization
analysis = aws_manager.analyze_resource_utilization('res-001')
print(f"Current utilization: {analysis['utilization']['current_rate']}%")
print(f"Efficiency score: {analysis['efficiency']['score']}")
```

### Cost Management
```python
# Monitor AWS costs
costs = aws_manager.monitor_costs()
print(f"Current monthly cost: ${costs['current_cost']}")
print(f"Cost status: {costs['status']}")
```

### System Metrics
```python
# Get system metrics
metrics = aws_manager.get_system_metrics()
print(f"Active instances: {metrics['instances']}")
print(f"Active containers: {metrics['containers']}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 