# Dark Forest Interactive

A minimalist website explaining the Dark Forest theory from Liu Cixin's "The Dark Forest". Features a clean, cyberpunk-inspired design with neon effects and smooth animations.

## Features

- Minimalist, dark theme design
- Neon glow effects and animations
- Responsive layout
- Social media integration
- Clean, readable typography

## Setup

1. Install Python 3.11 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```
Edit `.env` with your settings:
- `SECRET_KEY`: Your Flask secret key
- `TWITTER_URL`: Your Twitter profile URL
- `TELEGRAM_URL`: Your Telegram group/channel URL
- `CHART_URL`: Your chart/analytics URL

## Development Guide

### Setting Up Development Environment

1. Create a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
pip install pytest python-dotenv flake8 black
```

3. Configure VS Code settings (optional):
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true
}
```

### Project Organization

The project follows a modular structure:
- `app.py`: Core Flask application and routing
- `templates/`: Jinja2 templates using template inheritance
- `static/`: CSS and static assets with modular organization

### Development Workflow

1. **Making Changes**
   - Work on a feature branch
   - Follow PEP 8 style guide
   - Use meaningful commit messages

2. **Testing Changes**
   ```bash
   # Run Flask in debug mode
   export FLASK_ENV=development  # Linux/Mac
   set FLASK_ENV=development    # Windows
   flask run
   ```

3. **Code Style**
   ```bash
   # Format code
   black .

   # Check style
   flake8
   ```

### Common Development Tasks

1. **Adding New Routes**
   ```python
   @app.route('/new-path')
   def new_route():
       return render_template('new.html')
   ```

2. **Adding CSS Features**
   ```css
   /* Add new animation */
   @keyframes newEffect {
       from { /* initial state */ }
       to { /* final state */ }
   }

   /* Add new component */
   .new-component {
       animation: newEffect 2s ease infinite;
   }
   ```

3. **Template Modifications**
   ```html
   {% extends "base.html" %}
   {% block content %}
   <!-- New content here -->
   {% endblock %}
   ```

### Best Practices

1. **Flask**
   - Use blueprints for larger applications
   - Keep routes clean and focused
   - Handle errors gracefully

2. **CSS**
   - Follow BEM naming convention
   - Keep animations performant
   - Test on multiple devices

3. **Security**
   - Never commit `.env` files
   - Use secure session cookies
   - Implement CSRF protection

### Debugging Tips

1. **Flask Debug Mode**
   - Automatic reloading
   - Detailed error pages
   - Interactive debugger

2. **Common Issues**
   - Port already in use: Change port in `app.run()`
   - Module not found: Check virtual environment
   - Template not found: Check file paths

3. **Browser Tools**
   - Use Chrome DevTools for CSS debugging
   - Check Network tab for request issues
   - Monitor Console for JavaScript errors

## Running the Website

### Windows
Double-click `run_website.bat` or run:
```bash
python app.py
```

### Linux/Mac
```bash
python app.py
```

The website will be available at `http://localhost:5000`

## Project Structure

```
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create from .env.example)
├── Procfile           # Deployment configuration
├── static/            # Static assets
│   ├── style.css      # Website styles
│   └── images/        # Image assets
└── templates/         # HTML templates
    ├── index.html     # Main page
    ├── 404.html      # Error page
    └── 500.html      # Server error page
```

## Customization

### Changing Colors
Edit the CSS variables in `static/style.css`:
```css
:root {
    --neon-text: #00ff9d;    /* Main text color */
    --neon-border: #00ffd5;  /* Border and glow color */
}
```

### Social Links
Update the URLs in your `.env` file:
```
TWITTER_URL=https://twitter.com/your-account
TELEGRAM_URL=https://t.me/your-group
CHART_URL=https://your-chart-url
```

## Deployment

The project is ready for deployment on platforms like:
- Heroku (using Procfile)
- PythonAnywhere
- Any platform supporting Python/Flask

## License

MIT License - Feel free to use, modify, and distribute as needed.

## Credits

- Design inspired by cyberpunk aesthetics
- Dark Forest theory by Liu Cixin
- Built with Flask and modern CSS