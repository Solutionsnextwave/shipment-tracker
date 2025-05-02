
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
    if request.endpoint not in ('login', 'static') and 'user' not in session:
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
        po_date = request.form['po_date']
        location = request.form['location']
        pincode = request.form['pincode']
        company = request.form['company']
        asn = request.form['asn']
        grn = request.form['grn']
        batch_number = request.form['batch_number']
        status = request.form['status']
        cursor.execute("""
            INSERT INTO shipment_status
            (po_number, po_date, location, pincode, company, asn, grn, batch_number, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (po_number, po_date, location, pincode, company, asn, grn, batch_number, status))
        conn.commit()
        return redirect('/status')
    cursor.execute("SELECT * FROM companies")
    companies = cursor.fetchall()
    conn.close()
    return render_template('add_po.html', companies=companies)
