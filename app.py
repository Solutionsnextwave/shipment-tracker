
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash
print(generate_password_hash('admin123'))
import pymysql
import os

app = Flask(__name__)
app.secret_key = 'secret123'

def get_db():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        db=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.before_request
def require_login():
    if request.endpoint not in ('login', 'static') and 'user' not in session:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
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
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

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

@app.route('/users', methods=['GET', 'POST'])
def manage_users():
    if not session['user'].get('is_admin'):
        return "Access denied"
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = generate_password_hash(request.form['password'])
        view = 'can_view' in request.form
        edit = 'can_edit' in request.form
        delete = 'can_delete' in request.form
        cursor.execute("""
            INSERT INTO users (email, name, password_hash, can_view, can_edit, can_delete)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (email, name, password, view, edit, delete))
        conn.commit()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('users.html', users=users)

@app.route('/delete-user/<int:id>')
def delete_user(id):
    if not session['user'].get('is_admin'):
        return "Access denied"
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/users')
