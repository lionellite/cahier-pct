"""Blueprint de l'API HTTP."""

from __future__ import annotations

from flask import Blueprint

from .routes import register_routes

api_bp = Blueprint("api", __name__)
register_routes(api_bp)
