from flask import Flask, send_from_directory
from flask_cors import CORS
import logging
import os
from app.config.config import config

# Import all controllers
from app.controllers.login_controller import login_bp
from app.controllers.attendance_controller import attendance_bp
from app.controllers.attendance_table_controller import attendance_table_bp
from app.controllers.timetable_controller import timetable_bp
from app.controllers.diagnostic_controller import diagnostic_bp
from app.controllers.other_controllers import (
    web_bp, profile_bp, results_bp, status_bp, logout_bp
)

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configure CORS
    cors_origins = config.cors_allowed_origins.split(',') if config.cors_allowed_origins != '*' else '*'
    cors_methods = config.cors_allowed_methods.split(',')
    cors_headers = config.cors_allowed_headers.split(',') if config.cors_allowed_headers != '*' else '*'
    
    CORS(app, 
         origins=cors_origins,
         methods=cors_methods,
         allow_headers=cors_headers,
         supports_credentials=config.cors_allow_credentials)
    
    # Configure minimal logging - only critical errors
    logging.basicConfig(
        level=logging.CRITICAL,
        format='%(levelname)s: %(message)s'
    )
    
    # Set werkzeug (Flask) logger to ERROR only (suppress INFO logs)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    
    # Register blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(attendance_table_bp)
    app.register_blueprint(timetable_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(diagnostic_bp)
    
    # Root route - API info
    @app.route('/')
    def index():
        return {
            "name": "ETLabsHR Python API",
            "version": "2.0.0",
            "status": "running",
            "endpoints": {
                "health": "/health",
                "login": "/api/login",
                "profile": "/api/profile",
                "attendance": "/api/attendance",
                "attendance_table": "/api/attendance-table",
                "timetable": "/api/timetable",
                "results": "/api/results",
                "status": "/api/status",
                "logout": "/api/logout",
                "dns_test": "/api/diagnostic/dns-test",
                "network_info": "/api/diagnostic/network-info"
            }
        }, 200
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "message": "ETLabsHR Python API is running"}, 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Not found", "message": "The requested resource was not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error", "message": "An unexpected error occurred"}, 500
    
    return app

# Create app instance for Gunicorn
app = create_app()

def main():
    """Main entry point for direct execution"""
    # Start the application
    port = config.port
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    main()