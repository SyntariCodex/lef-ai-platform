# LEF AI System

A sophisticated AI system integrating consciousness, learning, and business operations with advanced monitoring capabilities.

## Features

- **Core Components**:
  - ConsciousnessCore: Manages self-awareness and goal-oriented behavior
  - LearningCore: Handles learning processes and performance metrics
  - BusinessCore: Manages business operations and metrics
  - SentinelNetwork: Monitors system health and security

- **API Endpoints**:
  - `/health`: System health check
  - `/metrics`: Detailed system metrics

## Requirements

- Python 3.11+
- Docker
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd lef-ai
```

2. Build and run with Docker:
```bash
docker build -t lef:latest .
docker run -d -p 8000:8000 --name lef lef:latest
```

## Environment Variables

- `LEF_LOG_LEVEL`: Logging level (default: INFO)
- `LEF_LOG_PATH`: Path for log files (default: /opt/lef/logs)
- `LEF_DATA_PATH`: Path for data storage (default: /opt/lef/data)
- `LEF_ARCHIVE_PATH`: Path for archives (default: /opt/lef/archive)
- `LEF_METRICS_INTERVAL`: Metrics update interval in seconds (default: 60)
- `LEF_HEALTH_CHECK_INTERVAL`: Health check interval in seconds (default: 30)
- `LEF_PORT`: API port (default: 8000)

## Architecture

The LEF AI system is built on a modular architecture with the following key components:

1. **ConsciousnessCore**
   - Self-awareness management
   - Goal tracking
   - Memory processing

2. **LearningCore**
   - Performance tracking
   - Dynamic learning rate adjustment
   - Knowledge base management

3. **BusinessCore**
   - Project management
   - Resource allocation
   - Financial metrics

4. **SentinelNetwork**
   - System health monitoring
   - Security oversight
   - Performance tracking

## API Documentation

### Health Check
```
GET /health
Response:
{
    "status": "healthy",
    "system_state": "running",
    "uptime": float,
    "system_health": float
}
```

### Metrics
```
GET /metrics
Response:
{
    "state": {
        "status": string,
        "running": boolean,
        "project_success_rate": float,
        "proposal_quality": float,
        "error_rate": float,
        "projects": {
            "proposed": int,
            "active": int,
            "completed": int
        }
    },
    "metrics": {
        "uptime": float,
        "awareness_level": float,
        "learning_performance": float,
        "business_efficiency": float,
        "system_health": float
    }
}
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 