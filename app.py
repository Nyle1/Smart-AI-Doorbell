# Compatibility entry point: starts the combined Flask dashboard.
from smart_system import app, socketio

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000,
                 debug=False, use_reloader=False,
                 allow_unsafe_werkzeug=True)
