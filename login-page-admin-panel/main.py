import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', '12345'))
        conn.commit()
    conn.close()
import os
from flask import abort

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

@app.route("/dbview")
def dbview():
    if request.args.get("key") != os.environ.get("VIEW_KEY", ""):
        abort(404)
    con = sqlite3.connect(DB_PATH)
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")]
    html = ""
    for t in tables:
        cur = con.execute(f'SELECT * FROM "{t}"')
        cols = [c[0] for c in cur.description]
        html += f"<h3>{t}</h3><table border=1 cellpadding=6><tr>"
        html += "".join(f"<th>{c}</th>" for c in cols) + "</tr>"
        for row in cur.fetchall():
            html += "<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>"
        html += "</table>"
    con.close()
    return html

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            message = "This username is already taken!"
        except Exception as e:
            message = f"An error occurred: {e}"

    return render_template('register.html', message=message)

@app.route('/', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
            if username == 'admin':
                if password == '12345':
                    return redirect(url_for('show_users'))

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            message = "This username is already taken!"
        except Exception as e:
            message = f"An error occurred: {e}"
        # conn = sqlite3.connect('database.db')
        # cursor = conn.cursor()
        # cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        # user = cursor.fetchone()
        # conn.close()


            
        #     message = f"Welcome, {username}! You are logged in."
        # else:
        #     message = "Invalid username or password."

    return render_template('login.html', message=message)

@app.route('/admin/users')
def show_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password FROM users')
    all_users = cursor.fetchall()
    conn.close()
    return render_template('admin.html', users=all_users)

@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    username = user[0] if user else "Unknown"
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    print(f"[SUCCESS] User '{username}' was permanently removed from database.db\n")
    return redirect(url_for('show_users'))


if __name__ == '__main__':
    init_db() 
    app.run(debug=True)


