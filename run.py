from app import create_app
from app.extensions import socketio





if __name__ == "__main__":
    app = create_app()
    socketio.run(app,debug=True)
    