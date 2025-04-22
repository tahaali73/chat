from app import create_app
from app.extensions import socketio
import eventlet
from eventlet import wsgi




app = create_app()
if __name__ == 'run':
    app.debug = True
    socketio.run(
        app, 
        host='127.0.0.1', 
        port=8000, 
        debug=True, 
        use_reloader=True
    )
    