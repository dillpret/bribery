"""
Flask routes for the web application
"""

from flask import render_template


def register_routes(app):
    """Register all Flask routes"""

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/test')
    def frontend_test():
        return render_template('frontend_test.html')

    @app.route('/game/<game_id>')
    def game_page(game_id):
        return render_template('game.html', game_id=game_id)
