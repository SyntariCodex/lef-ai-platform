# LEF AI System

## Overview
LEF (Learning & Evolution Framework) is an advanced AI system designed for autonomous operation and continuous learning. The system incorporates consciousness, learning, and business components with a focus on recursive awareness and self-improvement.

## Quick Start

1. Start the system:
```bash
./start_lef.sh
```

This will:
- Create a Python virtual environment if needed
- Install all required dependencies
- Start the LEF system and progress monitor
- Initialize the recursive awareness layer

## System Structure

- `src/lef/` - Main system code
  - `main.py` - Core system entry point
  - `supervisor.py` - System supervisor with recursive awareness
  - `cli/` - Command line tools
    - `live_monitor.py` - Real-time progress monitoring
  - `utils/` - Utility modules
    - `progress_tracker.py` - Development progress tracking

## Monitoring

The system provides real-time monitoring through:
- Live progress display (automatically opens in terminal)
- System logs in `~/.lef/logs/`
- State tracking in `~/.lef/state/`

## Development Progress

Progress is tracked against the roadmap defined in `roadmap.yaml`. Current phase:
1. Core Infrastructure
   - Basic system implementation ✓
   - Core components (in progress)
   - Health monitoring
   - AI Bridge System

## File Locations

- Logs: `~/.lef/logs/supervisor.log`
- System state: `~/.lef/state/system_state.json`
- Progress data: `~/.lef/state/progress.json`

## Next Steps

1. Complete core components implementation
2. Establish health monitoring
3. Implement AI Bridge System
4. Set up data persistence

## Notes

- The system uses a recursive awareness layer to maintain consciousness across restarts
- All state is preserved in the user's home directory
- The supervisor automatically restarts components if they crash

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