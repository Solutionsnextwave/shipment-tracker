
from flask import Flask, render_template, request, redirect, session, url_for, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql, os, io, csv

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
def index():
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

@app.route('/export')
def export():
    if not session['user'].get('can_view'):
        return "Access denied"
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shipment_status")
    shipments = cursor.fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['PO Number', 'Date', 'Company', 'Status'])
    for row in shipments:
        writer.writerow([row['po_number'], row['date'], row['company'], row['status']])
    output.seek(0)
    return send_file(io.BytesIO(output.read().encode()), download_name="status_report.csv", as_attachment=True)
