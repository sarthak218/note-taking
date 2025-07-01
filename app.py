from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_socketio import SocketIO, emit
from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = 'secret_key_for_session'
socketio = SocketIO(app)

user_notes = {}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        company = request.form['company']
        session['username'] = username
        session['company'] = company
        return redirect(url_for('notes'))
    return render_template('login.html')

@app.route('/notes')
def notes():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    return render_template('notes.html', username=username, company=session.get('company'))

@app.route('/download/<username>')
def download_note(username):
    if username in user_notes:
        note_content = user_notes[username]['note']
        file_stream = BytesIO()
        file_stream.write(note_content.encode('utf-8'))
        file_stream.seek(0)
        return send_file(file_stream, as_attachment=True, download_name=f"{username}_note.txt", mimetype='text/plain')
    return "User not found", 404

@socketio.on('register_user')
def handle_register(data):
    user = data['user']
    company = data['company']
    if user not in user_notes:
        user_notes[user] = {'company': company, 'note': ''}
    emit('update_notes', user_notes, broadcast=False)
    emit('update_notes', user_notes, broadcast=True, include_self=False)

@socketio.on('note_update')
def handle_note_update(data):
    user = data['user']
    note = data['note']
    if user in user_notes:
        user_notes[user]['note'] = note
        emit('update_notes', user_notes, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
