
from flask import Flask, render_template, request, redirect
import pymysql
import config

app = Flask(__name__)

def get_db():
    return pymysql.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        db=config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM po_details")
        po_data = cursor.fetchall()
    conn.close()
    return render_template('index.html', po_data=po_data)

@app.route('/add', methods=['GET', 'POST'])
def add_po():
    if request.method == 'POST':
        data = (
            request.form['po_number'],
            request.form['revised_po'],
            request.form['location'],
            request.form['pin_code'],
            request.form['product_1l'],
            request.form['product_900ml'],
            request.form['product_500ml'],
            request.form['product_450ml'],
            request.form['po_date'],
            request.form['asn'],
            request.form['grn'],
            request.form['payment_status']
        )
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO po_details (
                    po_number, revised_po, location, pin_code,
                    product_1l, product_900ml, product_500ml, product_450ml,
                    po_date, asn, grn, payment_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, data)
            conn.commit()
        conn.close()
        return redirect('/')
    return render_template('add_po.html')

@app.route('/status')
def view_status():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT pd.po_number, pd.location, ap.confirm_date, ap.delivery_location, ap.total_po_qty
            FROM po_details pd
            LEFT JOIN appointment_status ap ON pd.po_number = ap.po_number
        """)
        status_data = cursor.fetchall()
    conn.close()
    return render_template('view_status.html', status_data=status_data)
import json

@app.route('/insert-sample')
def insert_sample_data():
    try:
        with open("insert_sample_data.json") as f:
            data = json.load(f)

        conn = get_db()
        cursor = conn.cursor()

        for row in data['po_details']:
            cursor.execute("""
                INSERT INTO po_details (
                    po_number, revised_po, location, pin_code,
                    product_1l, product_900ml, product_500ml, product_450ml,
                    po_date, asn, grn, payment_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['po_number'], row['revised_po'], row['location'], row['pin_code'],
                row['product_1l'], row['product_900ml'], row['product_500ml'], row['product_450ml'],
                row['po_date'], row['asn'], row['grn'], row['payment_status']
            ))

        for row in data['appointment_status']:
            cursor.execute("""
                INSERT INTO appointment_status (
                    confirm_date, delivery_location, vendor_name,
                    brand, category, sku_count, total_po_qty, po_number
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['confirm_date'], row['delivery_location'], row['vendor_name'],
                row['brand'], row['category'], row['sku_count'], row['total_po_qty'], row['po_number']
            ))

        conn.commit()
        conn.close()
        return "✅ Sample data inserted successfully"
    except Exception as e:
        return f"❌ Error: {e}"

@app.route('/debug-status')
def debug_status():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        cursor.execute("SELECT * FROM po_details LIMIT 1;")
        po_sample = cursor.fetchall()
        cursor.execute("SELECT * FROM appointment_status LIMIT 1;")
        ap_sample = cursor.fetchall()
    conn.close()
    return {
        "tables": tables,
        "sample_po_details": po_sample,
        "sample_appointment_status": ap_sample
    }


if __name__ == '__main__':
    app.run(debug=True)
