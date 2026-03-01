"""
run.py — Entry point for the Gym Management GraphQL API.

Usage:
    python run.py
"""
from app import create_app

app = create_app()
appURL = "http://127.0.0.1:8080/graphql"

if __name__ == "__main__":
    app.run(debug=True, port=8080)
