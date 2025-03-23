# LEF UI Package

This package provides the web-based user interface for the LEF (Learning Feedback) system.

## Features

- Real-time system status monitoring
- Task management interface
- WebSocket-based live updates
- Modern, responsive design
- Dark mode support
- Accessibility features

## Structure

```
src/lef/ui/
├── __init__.py          # Package initialization
├── routes.py            # FastAPI routes and WebSocket handlers
├── static/             # Static files
│   ├── css/           # Stylesheets
│   │   └── styles.css # Main styles
│   ├── js/            # JavaScript files
│   │   └── app.js     # Main application logic
│   └── templates/     # HTML templates
│       ├── index.html # Main UI page
│       └── task_form.html # Task creation form
└── requirements.txt    # UI-specific dependencies
```

## Dependencies

- FastAPI
- Jinja2
- aiofiles
- WebSocket support
- TailwindCSS (CDN)
- Font Awesome (CDN)

## Usage

The UI is automatically mounted at `/ui` when the LEF system starts. Access it through your web browser at:

```
http://localhost:8000/ui
```

## Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the development server:
   ```bash
   uvicorn src.lef.api:app --reload
   ```

3. Access the UI at `http://localhost:8000/ui`

## Features

### System Status
- Real-time monitoring of system components
- Resource usage tracking (CPU, Memory, Disk)
- Component health indicators

### Task Management
- Create new tasks
- Update task status
- Track task progress
- View task dependencies

### UI Features
- Responsive design for all screen sizes
- Dark mode support
- Real-time updates via WebSocket
- Toast notifications
- Loading indicators
- Keyboard shortcuts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 