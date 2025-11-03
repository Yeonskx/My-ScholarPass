from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__, static_folder='.', template_folder='.')

# --- Database connection ---
def get_db_connection():
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Ensure users table exists ---
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'student'
    )''')
    conn.commit()
    conn.close()

# --- Routes for your HTML files ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin')
def signin():
    return render_template('accountsignin.html')

@app.route('/students')
def students():
    return render_template('students.html')

@app.route('/providers')
def providers():
    return render_template('providers.html')

# --- Signup route ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, 'student')",
            (name, email, password)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('signin'))

    # If user visits /signup directly in browser
    return redirect(url_for('signin'))

# --- Login route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()
        conn.close()

        if user:
            return redirect(url_for('index'))  # ✅ Redirect to homepage
        else:
            return redirect(url_for('signin'))  # Invalid login → back to signin
    # If someone visits /login directly in browser
    return redirect(url_for('signin'))

# --- Allow serving CSS and JS directly ---
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    init_db()  # ✅ Make sure table exists
    app.run(debug=True)
