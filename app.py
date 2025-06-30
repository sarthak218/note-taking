from flask import Flask, render_template_string, request, redirect, url_for, session, send_file
from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = 'secret_key_for_session'

# In-memory storage for user notes
user_notes = {}

# HTML Templates
login_page = '''
<!doctype html>
<title>Login</title>
<h2>Enter Username and Company</h2>
<form method="POST">
  Username: <input type="text" name="username" required><br>
  Company: <input type="text" name="company" required><br>
  <input type="submit" value="Enter">
</form>
'''

notes_template = '''
<!doctype html>
<title>Notes</title>
<h2>Welcome {{ username }} from {{ company }}</h2>
<div style="display: flex; flex-wrap: wrap; gap: 10px;">
  {% for user, info in notes.items() %}
    <div style="flex: 1 0 calc(50% - 10px); border: 1px solid black; padding: 10px;">
      <h3>{{ user }} ({{ info['company'] }})</h3>
      {% if user == current_user %}
        <form method="POST">
          <textarea name="note" rows="10" style="width: 100%;">{{ info['note'] }}</textarea><br>
          <input type="submit" value="Save">
        </form>
        <form method="GET" action="{{ url_for('download_note', username=user) }}">
          <button type="submit">Download Note</button>
        </form>
      {% else %}
        <textarea rows="10" style="width: 100%;" disabled>{{ info['note'] }}</textarea>
      {% endif %}
    </div>
  {% endfor %}
</div>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        company = request.form['company']
        session['username'] = username
        session['company'] = company
        if username not in user_notes:
            user_notes[username] = {'company': company, 'note': ''}
        return redirect(url_for('notes'))
    return render_template_string(login_page)

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_notes[username]['note'] = request.form['note']
    return render_template_string(notes_template, notes=user_notes, current_user=username, username=username, company=session.get('company'))

@app.route('/download/<username>')
def download_note(username):
    if username in user_notes and session.get('username') == username:
        note_content = user_notes[username]['note']
        file_stream = BytesIO()
        file_stream.write(note_content.encode('utf-8'))
        file_stream.seek(0)
        return send_file(file_stream, as_attachment=True, download_name=f"{username}_note.txt", mimetype='text/plain')
    return "Unauthorized", 403

if __name__ == '__main__':
    app.run(debug=True)
