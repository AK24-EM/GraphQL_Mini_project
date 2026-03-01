import json
from flask import Flask, request, jsonify
from .database import init_db
from .schema import schema

# Minimal GraphiQL HTML served at GET /graphql
GRAPHIQL_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Gym API — GraphiQL</title>
  <link href="https://unpkg.com/graphiql@3/graphiql.min.css" rel="stylesheet" />
</head>
<body style="margin:0;">
  <div id="graphiql" style="height:100vh;"></div>
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/graphiql@3/graphiql.min.js"></script>
  <script>
    const fetcher = GraphiQL.createFetcher({ url: window.location.href });
    ReactDOM.createRoot(document.getElementById('graphiql')).render(
      React.createElement(GraphiQL, { fetcher })
    );
  </script>
</body>
</html>"""


def create_app():
    app = Flask(__name__)

    # Connect to MongoDB
    init_db()

    @app.route("/graphql", methods=["GET", "POST"])
    def graphql_view():
        # Serve GraphiQL UI on GET requests
        if request.method == "GET":
            return GRAPHIQL_HTML, 200, {"Content-Type": "text/html"}

        # Execute GraphQL operation on POST
        data = request.get_json(silent=True) or {}
        query = data.get("query", "")
        variables = data.get("variables")
        operation_name = data.get("operationName")

        result = schema.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
        )

        response = {}
        if result.data is not None:
            response["data"] = result.data
        if result.errors:
            response["errors"] = [
                {"message": str(e)} for e in result.errors
            ]

        status_code = 200 if not result.errors else 400
        return jsonify(response), status_code

    @app.route("/")
    def index():
        return (
            "<h2>🏋️ Gym Management GraphQL API</h2>"
            "<p>Visit <a href='/graphql'>/graphql</a> to open the GraphiQL playground.</p>"
        )

    return app
