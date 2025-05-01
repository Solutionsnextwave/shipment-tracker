
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os

app = Flask(__name__)
app.secret_key = 'secret123'

def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.before_request
def require_login():
    if request.endpoint not in ('login', 'static', 'create_admin') and 'user' not in session:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()
        if user:
            if check_password_hash(user['password_hash'], password):
                session['user'] = {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email'],
                    'is_admin': user['is_admin'],
                    'can_view': user['can_view'],
                    'can_edit': user['can_edit'],
                    'can_delete': user['can_delete']
                }
                return redirect('/')
            else:
                error = "❌ Password does not match"
        else:
            error = "❌ Email not found"
    return render_template('login.html', error=error)
print("HASH FROM DB:", user['password_hash'])
print("PASSWORD TYPED:", password)
print("MATCHES:", check_password_hash(user['password_hash'], password))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/')
def home():
    return redirect('/status')

@app.route('/status')
def status():
    if not session['user'].get('can_view'):
        return "Access denied"
    return render_template('status.html')

@app.route('/create-admin')
def create_admin():
    conn = get_db()
    cursor = conn.cursor()
    password_hash = generate_password_hash("admin123")
    try:
        cursor.execute("""
            INSERT INTO users (email, name, password_hash, can_view, can_edit, can_delete, is_admin)
            VALUES (%s, %s, %s, TRUE, TRUE, TRUE, TRUE)
        """, ('kumaran@moojic.com', 'Admin', password_hash))
        conn.commit()
        return "✅ Admin created successfully"
    except pymysql.err.IntegrityError:
        return "⚠️ Admin already exists"
