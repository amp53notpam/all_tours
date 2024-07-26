"""App entry point."""
from tours import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, passthrough_errors=True, use_debugger=False, use_reloader=False, host="0.0.0.0", port=5000)
