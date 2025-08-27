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

    @app.route('/')
    def index():
        return render_template('index.html', version=version)

    @app.route('/test')
    def frontend_test():
        return render_template('frontend_test.html')

    @app.route('/bribery/<game_id>')
    def bribery_game_page(game_id):
        return render_template('game.html', game_id=game_id, version=version)
        
    @app.route('/instructions')
    def instructions_page():
        return render_template('instructions.html', version=version)
    
    # Keep the old route for backwards compatibility (optional)
    @app.route('/game/<game_id>')
    def game_page_redirect(game_id):
        from flask import redirect
        return redirect(f'/bribery/{game_id}')
