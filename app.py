
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql, os

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
    allowed = ('login', 'static')
    if request.endpoint not in allowed and 'user' not in session:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user'] = user
            return redirect('/')
        error = "Invalid credentials"
    return render_template('login.html', error=error)

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
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shipment_status")
    shipments = cursor.fetchall()
    conn.close()
    return render_template('status.html', shipments=shipments)

@app.route('/add-po', methods=['GET', 'POST'])
def add_po():
    if not session['user'].get('can_edit'):
        return "Access denied"
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        po_number = request.form['po_number']
        date = request.form['date']
        company = request.form['company']
        status = request.form['status']
        cursor.execute("INSERT INTO shipment_status (po_number, date, company, status) VALUES (%s, %s, %s, %s)",
                       (po_number, date, company, status))
        conn.commit()
        return redirect('/status')
    cursor.execute("SELECT * FROM companies")
    companies = cursor.fetchall()
    conn.close()
    return render_template('add_po.html', companies=companies)

@app.route('/companies', methods=['GET', 'POST'])
def companies():
    if not session['user'].get('is_admin'):
        return "Access denied"
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        cursor.execute("INSERT INTO companies (name) VALUES (%s)", (name,))
        conn.commit()
    cursor.execute("SELECT * FROM companies")
    companies = cursor.fetchall()
    conn.close()
    return render_template('companies.html', companies=companies)

@app.route('/users', methods=['GET', 'POST'])
def users():
    if not session['user'].get('is_admin'):
        return "Access denied"
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        can_view = 'can_view' in request.form
        can_edit = 'can_edit' in request.form
        can_delete = 'can_delete' in request.form
        cursor.execute("INSERT INTO users (name, email, password_hash, can_view, can_edit, can_delete, is_admin) VALUES (%s, %s, %s, %s, %s, %s, FALSE)",
                       (name, email, password, can_view, can_edit, can_delete))
        conn.commit()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('users.html', users=users)
