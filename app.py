
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

@app.route('/add-po')
def add_po():
    return render_template('add_po.html')

@app.route('/add-status')
def add_status():
    return render_template('add_status.html')

@app.route('/companies')
def companies():
    return render_template('companies.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True)
