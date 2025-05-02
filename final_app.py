
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
    cursor.execute(
        "SELECT s.*, pt.name AS product_type, u.name AS uom, w.label AS weight_label "
        "FROM shipment_status s "
        "LEFT JOIN product_types pt ON s.product_type_id = pt.id "
        "LEFT JOIN uom u ON s.uom_id = u.id "
        "LEFT JOIN weights w ON s.weight_id = w.id"
    )
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
        fields = [
            'po_number', 'tracking_number', 'po_date', 'po_expiry_date',
            'expected_delivery_date', 'appointment_date', 'company',
            'location', 'pincode', 'product_type_id', 'uom_id', 'weight_id',
            'quantity', 'driver_name', 'vehicle_number', 'weight',
            'mode_of_shipment', 'batch_number', 'asn', 'grn', 'status'
        ]
        values = [request.form.get(f) for f in fields]
        placeholders = ', '.join(['%s'] * len(fields))
        cursor.execute(
            f"INSERT INTO shipment_status ({', '.join(fields)}) VALUES ({placeholders})",
            values
        )
        conn.commit()
        return redirect('/status')
    cursor.execute("SELECT * FROM companies")
    companies = cursor.fetchall()
    cursor.execute("SELECT * FROM product_types")
    product_types = cursor.fetchall()
    cursor.execute("SELECT * FROM uom")
    uoms = cursor.fetchall()
    cursor.execute("SELECT * FROM weights")
    weights = cursor.fetchall()
    conn.close()
    return render_template('add_po.html', companies=companies, product_types=product_types, uoms=uoms, weights=weights)

@app.route('/companies', methods=['GET', 'POST'])
def manage_companies():
    if not session['user'].get('is_admin'):
        return "Access denied"
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        gstn = request.form['gstn']
        contact_person = request.form['contact_person']
        email = request.form['email']
        mobile = request.form['mobile']
        cursor.execute(
            "INSERT INTO companies (name, address, gstn, contact_person, email, mobile) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (name, address, gstn, contact_person, email, mobile)
        )
        conn.commit()
    cursor.execute("SELECT * FROM companies")
    companies = cursor.fetchall()
    conn.close()
    return render_template('companies.html', companies=companies)

@app.route('/product-types', methods=['GET', 'POST'])
def product_types():
    if not session['user'].get('is_admin'):
        return "Access denied"
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        cursor.execute("INSERT INTO product_types (name) VALUES (%s)", (request.form['name'],))
        conn.commit()
    cursor.execute("SELECT * FROM product_types")
    items = cursor.fetchall()
    conn.close()
    return render_template('product_types.html', items=items)

@app.route('/uom', methods=['GET', 'POST'])
def uom():
    if not session['user'].get('is_admin'):
        return "Access denied"
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        cursor.execute("INSERT INTO uom (name) VALUES (%s)", (request.form['name'],))
        conn.commit()
    cursor.execute("SELECT * FROM uom")
    items = cursor.fetchall()
    conn.close()
    return render_template('uom.html', items=items)

@app.route('/weights', methods=['GET', 'POST'])
def weights():
    if not session['user'].get('is_admin'):
        return "Access denied"
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        label = request.form['label']
        value = request.form['value']
        cursor.execute("INSERT INTO weights (label, value) VALUES (%s, %s)", (label, value))
        conn.commit()
    cursor.execute("SELECT * FROM weights")
    items = cursor.fetchall()
    conn.close()
    return render_template('weights.html', items=items)
