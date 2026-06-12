from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger
from config import config
from extensions import db, jwt, bcrypt
import os

def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    # Swagger config
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/",
    }

    swagger_template = {
        "info": {
            "title": "Task Manager API",
            "description": "Scalable REST API with JWT Authentication and Role-Based Access Control",
            "version": "1.0.0",
            "contact": {"name": "Backend Intern Assignment"}
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT token. Format: **Bearer &lt;token&gt;**"
            }
        },
        "basePath": "/api/v1",
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    # Register blueprints (API versioning via /api/v1)
    from routes.auth import auth_bp
    from routes.tasks import tasks_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(tasks_bp, url_prefix="/api/v1/tasks")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")

    # Health check
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "version": "1.0.0"}), 200

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Route not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500

    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return jsonify({"error": "Missing or invalid token", "reason": reason}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "Invalid token", "reason": reason}), 401

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "development")
    app = create_app(env)
    app.run(debug=True, port=5000)
