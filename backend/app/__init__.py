"""Fabrique d'application Flask."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from .config import Config
from .errors import ApiError


def create_app(config_object: type[Config] = Config) -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_object)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=False,
    )

    from .api import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    _register_error_handlers(app)
    _register_frontend(app)

    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        return jsonify(error.to_dict()), error.status

    @app.errorhandler(404)
    def handle_not_found(_error):
        return (
            jsonify(
                {"error": {"code": "not_found", "message": "Ressource introuvable."}}
            ),
            404,
        )

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return (
            jsonify(
                {
                    "error": {
                        "code": "method_not_allowed",
                        "message": "Méthode HTTP non autorisée.",
                    }
                }
            ),
            405,
        )

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):
        app.logger.exception("Erreur inattendue", exc_info=error)
        return (
            jsonify(
                {
                    "error": {
                        "code": "internal_error",
                        "message": "Erreur interne du serveur.",
                    }
                }
            ),
            500,
        )


def _register_frontend(app: Flask) -> None:
    """Sert le build React en production, si présent.

    En développement, le frontend tourne via Vite et proxifie `/api`.
    """

    dist: Path = app.config["FRONTEND_DIST"]

    @app.get("/")
    @app.get("/<path:path>")
    def serve_frontend(path: str = ""):
        if not dist.exists():
            return (
                jsonify(
                    {
                        "name": "Cahier PCT API",
                        "message": "Build frontend absent. Lancez `npm run dev` dans frontend/.",
                        "docs": "/api/meta",
                    }
                ),
                200,
            )

        candidate = dist / path
        if path and candidate.is_file():
            return send_from_directory(dist, path)
        return send_from_directory(dist, "index.html")
