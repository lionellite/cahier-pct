"""Point d'entrée du serveur de développement."""

from __future__ import annotations

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=app.config["PORT"],
        debug=app.config["FLASK_DEBUG"],
    )
