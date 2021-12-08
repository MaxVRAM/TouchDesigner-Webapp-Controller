from flask import Flask, render_template, session, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect
from threading import Lock
from os import path, getenv
from datetime import datetime as dt
import json, requests, time

#https://medium.com/swlh/implement-a-websocket-using-flask-and-socket-io-python-76afa5bbeae1

ws_ip = getenv('TD_SOCKET_IP')
ws_port = getenv('TD_SOCKET_PORT')
ws_secret = getenv('TD_SOCKET_SECRET')
async_mode = None

app = Flask(__name__)
app.config['SECRTET_KEY'] = ws_secret
socket_ = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html',
                            sync_mode=socket_.async_mode)

@socket_.on('my_event', namespace='/web_client')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': message['data'], 'count': session['receive_count']})

@socket_.on('my_broadcast_event', namespace='/web_client')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': message['data'], 'count': session['receive_count']}, broadcast=True)

@socket_.on('disconnect_request', namespace='/web_client')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()
    
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Disconnected!', 'count': session['receive_count']}, callback=can_disconnect)


if __name__ == '__main__':
    socket_.run(app, debug=True)
    #app.run(debug=True)