from __future__ import annotations

from app import create_app
from app.config import Config

app = create_app()

if __name__ == "__main__":
    print("Starting SmartNest Rental Flask app...")
    print(f"Open http://127.0.0.1:{Config.PORT}/")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
