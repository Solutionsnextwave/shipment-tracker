
from flask import Flask, render_template, request, redirect, url_for
import pymysql
import os

app = Flask(__name__)

def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    return redirect(url_for('status'))

@app.route('/status')
def status():
    return render_template('status.html')

@app.route('/add-po', methods=['GET', 'POST'])
def add_po():
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = (
            request.form['po_number'], request.form['location'], request.form['po_date'],
            request.form['product_1l'], request.form['product_900ml'],
            request.form['product_500ml'], request.form['product_450ml'],
            request.form['company_id']
        )
        cursor.execute("""
            INSERT INTO po_details (po_number, location, po_date, product_1l, product_900ml, product_500ml, product_450ml, company_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, data)
        conn.commit()
        return redirect('/status')
    cursor.execute("SELECT id, name FROM companies")
    companies = cursor.fetchall()
    conn.close()
    return render_template('add_po.html', companies=companies)

@app.route('/companies', methods=['GET', 'POST'])
def companies():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute("""
            INSERT INTO companies (name, code, contact_person, phone, email)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.form['name'],
            request.form['code'],
            request.form['contact_person'],
            request.form['phone'],
            request.form['email']
        ))
        conn.commit()
        return redirect('/companies')

    cursor.execute("SELECT * FROM companies")
    companies = cursor.fetchall()
    conn.close()
    return render_template('companies.html', companies=companies)

@app.route('/delete-company/<int:id>')
def delete_company(id):
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM companies WHERE id=%s", (id,))
        conn.commit()
    conn.close()
    return redirect('/companies')

if __name__ == "__main__":
    app.run(debug=True)
