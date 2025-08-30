"""
Flask routes for the web application
"""

import os
from flask import render_template


def register_routes(app):
    """Register all Flask routes"""
    
    # Get version from VERSION file
    version_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'VERSION')
    try:
        with open(version_path, 'r') as f:
            version = f.read().strip()
    except (FileNotFoundError, IOError):
        version = "0.0.0"  # Fallback version
        
    # Store version in app config for use in versioned_static
    app.config['VERSION'] = version

    # Helper function to get files from a directory with a specific extension
    def get_files(directory, extension):
        """Get all files in a directory with a specific extension"""
        static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static')
        full_dir = os.path.join(static_dir, directory)
        if not os.path.exists(full_dir):
            return []
        
        files = []
        for file in os.listdir(full_dir):
            if file.endswith(extension):
                files.append(os.path.join(directory, file))
        return files
    
    # Add get_files function to jinja environment
    app.jinja_env.globals.update(get_files=get_files)

    @app.route('/')
    def index():
        return render_template('index.html', version=version)

    @app.route('/bribery/<game_id>')
    def bribery_game_page(game_id):
        return render_template('game.html', game_id=game_id, version=version)
    
    # Keep the old route for backwards compatibility (optional)
    @app.route('/game/<game_id>')
    def game_page_redirect(game_id):
        from flask import redirect
        return redirect(f'/bribery/{game_id}')
    
    # Vue.js app routes
    @app.route('/vue')
    @app.route('/vue/game/<game_id>')
    def vue_app(game_id=None):
        return render_template('vue_app.html', version=version)
    
    # Handle 404 errors for Vue routes by returning the Vue app
    @app.errorhandler(404)
    def not_found(e):
        path = str(e).split(" ")[2]
        if path.startswith("/vue/"):
            return render_template('vue_app.html', version=version)
        return render_template('index.html', version=version), 404
