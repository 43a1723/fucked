from flask import Flask, request
from datetime import datetime, timedelta

app = Flask(__name__)

SESSIONS = {}

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    if not data or 'username' not in data or 'ip' not in data or 'session' not in data:
        return {'status': 'error', 'message': 'Invalid data'}, 400

    session_id = data['session']
    SESSIONS[session_id] = {
        'username': data['username'],
        'ip': data['ip'],
        'last_seen': datetime.utcnow()
    }
    return {'status': 'success'}

@app.route('/gettext', methods=['GET'])
def gettext():
    now = datetime.utcnow()
    active_sessions = {
        sid: info for sid, info in SESSIONS.items()
        if now - info['last_seen'] < timedelta(seconds=15)
    }
    raw = '\n'.join(
        f"{sid} | {info['username']} | {info['ip']}"
        for sid, info in active_sessions.items()
    )
    return raw, 200, {'Content-Type': 'text/plain'}
