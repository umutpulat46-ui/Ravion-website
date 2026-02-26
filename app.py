from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory, flash, g
import sqlite3
import os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from functools import wraps

load_dotenv()

# Configure Flask
app = Flask(__name__, template_folder='.')
app.secret_key = os.environ.get("SECRET_KEY", "fallback_secret_key")
DATABASE = 'agency.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- STATIC FILE HANDLING (Fixes 403) ---
@app.route('/<path:filename>')
def serve_static(filename):
    if filename.lower().endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf')):
        return send_from_directory('.', filename)
    return "Not Found", 404

# --- AUTH DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


# --- PUBLIC ROUTES ---
@app.route('/')
def index():
    # Log valid visit (simple IP logging)
    client_ip = request.remote_addr
    
    try:
        db = get_db()
        # Ensure table updated (run python3 init_db.py)
        db.execute('INSERT INTO visits (ip_address) VALUES (?)', (client_ip,))
        db.commit()
    except Exception as e:
        print(f"Error logging visit: {e}")

    return render_template('index.html')

@app.route('/tr')
def index_tr():
    return render_template('index_tr.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    company = request.form.get('company')
    budget = request.form.get('budget')
    message = request.form.get('message')
    
    # Insert into DB
    db = get_db()
    db.execute('INSERT INTO messages (name, email, phone, company, budget, message) VALUES (?, ?, ?, ?, ?, ?)',
               (name, email, phone, company, budget, message))
    db.commit()
    
    # Print to terminal as requested
    print(f"\n--- NEW MESSAGE SAVED ---")
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Phone: {phone}")
    print(f"Company: {company}")
    print(f"Budget: {budget}")
    print(f"Message: {message}")
    print(f"-------------------------\n")
    
    flash('Message Sent Successfully!')
    return redirect('/')

# --- LOGIN & ADMIN ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        db = get_db()
        cursor = db.execute('SELECT * FROM admins WHERE username = ?', (username,))
        admin_row = cursor.fetchone()

        if admin_row and check_password_hash(admin_row['password_hash'], password):
            session['logged_in'] = True
            session['admin_id'] = admin_row['id']
            session['admin_username'] = admin_row['username']
            return redirect('/admin') 
        else:
            error = "Access Denied. Unauthorized entry attempt."

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/delete_message/<int:id>')
@login_required
def delete_message(id):
    
    db = get_db()
    db.execute('DELETE FROM messages WHERE id = ?', (id,))
    db.commit()
    
    flash('Message Deleted.')
    return redirect('/messages')

@app.route('/admin')
@login_required
def admin():
    
    db = get_db()
    
    # Count real messages
    cursor = db.execute('SELECT COUNT(*) FROM messages')
    message_count = cursor.fetchone()[0]

    # Count real visits
    cursor = db.execute('SELECT COUNT(*) FROM visits')
    visit_count = cursor.fetchone()[0]

    # Count real projects
    cursor = db.execute('SELECT COUNT(*) FROM projects')
    project_count = cursor.fetchone()[0]
    
    # Get latest 5 messages
    cursor = db.execute('SELECT * FROM messages ORDER BY id DESC LIMIT 5')
    latest_messages = cursor.fetchall()

    # Get all projects
    cursor = db.execute('SELECT * FROM projects')
    projects = cursor.fetchall()
    
    # We pass dummy data for others to avoid errors since we're in "nuclear fix" mode
    return render_template('admin.html', 
                           message_count=message_count, 
                           visit_count=visit_count,
                           project_count=project_count,
                           latest_messages=latest_messages,
                           projects=projects)

# Compatibility for existing links
@app.route('/admin.html')
def admin_html():
    return redirect('/admin')

@app.route('/clients')
@login_required
def clients():
    
    db = get_db()
    cursor = db.execute('SELECT * FROM clients ORDER BY id DESC')
    clients = cursor.fetchall()
            
    return render_template('clients.html', clients=clients)

@app.route('/add_client', methods=['POST'])
@login_required
def add_client():
    
    name = request.form.get('name')
    company = request.form.get('company')
    email = request.form.get('email')
    phone = request.form.get('phone')
    
    db = get_db()
    db.execute('INSERT INTO clients (name, company, email, phone, status) VALUES (?, ?, ?, ?, ?)', 
               (name, company, email, phone, 'Active'))
    db.commit()
    
    return redirect('/clients')

@app.route('/delete_client/<int:id>')
@login_required
def delete_client(id):
    
    db = get_db()
    db.execute('DELETE FROM clients WHERE id = ?', (id,))
    db.commit()
    
    return redirect('/clients')

@app.route('/team')
@login_required
def team():
    
    db = get_db()
    cursor = db.execute('SELECT * FROM employees ORDER BY id DESC')
    team = cursor.fetchall()
            
    return render_template('team.html', team=team)

@app.route('/add_employee', methods=['POST'])
@login_required
def add_employee():
    
    name = request.form.get('name')
    role = request.form.get('role')
    salary = request.form.get('salary')
    
    db = get_db()
    db.execute('INSERT INTO employees (name, role, salary, status) VALUES (?, ?, ?, ?)', 
               (name, role, salary, 'Active'))
    db.commit()
    
    return redirect('/team')

@app.route('/delete_employee/<int:id>')
@login_required
def delete_employee(id):
    
    db = get_db()
    db.execute('DELETE FROM employees WHERE id = ?', (id,))
    db.commit()
    
    return redirect('/team')

@app.route('/messages')
@login_required
def messages_route():
    
    db = get_db()
    cursor = db.execute('SELECT * FROM messages ORDER BY id DESC')
    messages = cursor.fetchall()
    
    return render_template('messages.html', messages=messages)

@app.route('/messages.html')
def messages_html():
    return redirect('/messages')

@app.route('/projects')
@login_required
def projects():
    
    db = get_db()
    cursor = db.execute('SELECT * FROM projects ORDER BY id DESC')
    projects = cursor.fetchall()
            
    return render_template('projects.html', projects=projects)

@app.route('/add_project', methods=['POST'])
@login_required
def add_project():
    
    name = request.form.get('name')
    value = request.form.get('value')
    status = request.form.get('status')
    
    db = get_db()
    db.execute('INSERT INTO projects (name, status, value) VALUES (?, ?, ?)', 
               (name, status, value))
    db.commit()
    
    return redirect('/projects')

@app.route('/delete_project/<int:id>')
@login_required
def delete_project(id):
    
    db = get_db()
    db.execute('DELETE FROM projects WHERE id = ?', (id,))
    db.commit()
    
    return redirect('/projects')

@app.route('/complete_project/<int:id>')
@login_required
def complete_project(id):
    
    db = get_db()
    db.execute("UPDATE projects SET status = 'Completed' WHERE id = ?", (id,))
    db.commit()
    
    return redirect('/projects')

@app.route('/projects.html')
def projects_html():
    return redirect('/projects')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
    print("Starting server on PORT 5001...")
    # Initialize DB check
    if not os.path.exists(DATABASE):
        print("Database not found. Initializing...")
        with app.app_context():
            db = get_db()
            db.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    company TEXT,
                    budget TEXT,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            db.commit()
            print("Database initialized.")
            
app.run(debug=True, port=5001, host='0.0.0.0')