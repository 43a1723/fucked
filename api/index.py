from flask import Flask, request
from datetime import datetime, timedelta

app = Flask(__name__)
SESSIONS = {}
LAST_REQUEST = {}  # Dùng để lưu thời gian upload gần nhất của mỗi session hoặc IP
# lmao
@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = request.get_json(force=True)
        session_id = str(data['session'])
        username = str(data['username'])
        ip = str(data['ip'])

        now = datetime.utcnow()
        last = LAST_REQUEST.get(session_id)

        # Anti-spam: cách tối thiểu giữa 2 lần gửi là 5 giây
        if last and (now - last).total_seconds() < 5:
            return {'status': 'error', 'message': 'Too many requests'}, 429

        # Cập nhật thông tin session
        SESSIONS[session_id] = {
            'username': username,
            'ip': ip,
            'last_seen': now
        }
        LAST_REQUEST[session_id] = now

        return {'status': 'success'}, 200

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

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
