# ============================================================
# Smart Complaint Management System
# app.py - Main Flask Application (SQLite version)
#
# NOTE: This version uses Python's built-in SQLite database.
#       A MySQL version is available — see database.sql.
#       To switch to MySQL, install Flask-MySQLdb and update
#       the db_query() helper to use flask_mysqldb.
# ============================================================

from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, g)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename   # Sanitize uploaded filenames
import os
import secrets
import string
import sqlite3
from functools import wraps
from datetime import datetime                # For converting SQLite timestamp strings
from flask_mail import Mail, Message

# ============================================================
# App Configuration
# ============================================================
app = Flask(__name__)

# ---- Mail Configuration ----
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER', 'your_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS', 'your_app_password')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'your_email@gmail.com')

mail = Mail(app)
# Secret key for session management
app.secret_key = 'smart_complaint_secret_key_2024'

# ---- Database path (SQLite file) ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'complaint.db')

# ---- File Upload Configuration ----
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
@app.template_filter('strftime')
def strftime_filter(date_str, format='%Y-%m-%d %H:%M:%S'):
    if not date_str:
        return ""
    if isinstance(date_str, datetime):
        return date_str.strftime(format)
    # SQLite returns dates as strings
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime(format)
    except (ValueError, TypeError):
        return date_str


# ============================================================
# SQLite Database Helpers
# ============================================================

def get_db():
    """Open a database connection (one per request, stored in g)."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row   # Rows behave like dicts
        g.db.execute("PRAGMA foreign_keys = ON")  # Enable FK constraints
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def query_db(sql, args=(), one=False, commit=False):
    """
    Run a SQL statement.
    - one=True  → return a single row (or None)
    - commit=True → commit the transaction (INSERT/UPDATE/DELETE)
    Returns all rows by default.
    """
    db = get_db()
    cur = db.execute(sql, args)
    if commit:
        db.commit()
        return cur.lastrowid       # Useful after INSERT
    rows = cur.fetchall()
    return (rows[0] if rows else None) if one else rows


def init_db():
    """Create all tables and seed data on first run."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")

    db.executescript("""
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT NOT NULL,
            email        TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            phone        TEXT,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Admins table
        CREATE TABLE IF NOT EXISTS admins (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );

        -- Departments table
        CREATE TABLE IF NOT EXISTS departments (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );

        -- Complaints table
        CREATE TABLE IF NOT EXISTS complaints (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id  TEXT UNIQUE NOT NULL,
            user_id       INTEGER NOT NULL,
            title         TEXT NOT NULL,
            description   TEXT NOT NULL,
            category      TEXT NOT NULL,
            photo         TEXT,
            location      TEXT,
            status        TEXT DEFAULT 'Pending',
            department_id INTEGER,
            admin_notes   TEXT,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
        );
    """)

    # Seed departments (only if table is empty)
    count = db.execute("SELECT COUNT(*) FROM departments").fetchone()[0]
    if count == 0:
        departments = [
            'Road & Infrastructure', 'Water Supply', 'Electricity',
            'Sanitation & Waste', 'Education / College',
            'Health & Medical', 'Public Safety', 'General Administration'
        ]
        for dept in departments:
            db.execute("INSERT INTO departments (name) VALUES (?)", (dept,))

    # Seed default admin (only if table is empty)
    admin_count = db.execute("SELECT COUNT(*) FROM admins").fetchone()[0]
    if admin_count == 0:
        hashed = generate_password_hash('admin123')
        db.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
            ('admin', hashed)
        )

    db.commit()
    db.close()
    print("✅ Database initialized successfully.")


# ============================================================
# Helper Functions
# ============================================================

def allowed_file(filename):
    """Check file extension is in the allowed list."""
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)


def generate_complaint_id():
    """Generate a unique complaint ID like CMP-AB3X7."""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(secrets.choice(chars) for _ in range(5))
    return f"CMP-{suffix}"


# ============================================================
# Access Control Decorators
# ============================================================

def login_required(f):
    """Redirect to login page if user is not in session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Redirect to admin login if admin is not in session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


# ============================================================
# PUBLIC ROUTES
# ============================================================

@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


# ============================================================
# USER AUTHENTICATION ROUTES
# ============================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        phone    = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('Name, email and password are required.', 'danger')
            return redirect(url_for('register'))

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register'))

        # Check for duplicate email
        existing = query_db("SELECT id FROM users WHERE email = ?", (email,), one=True)
        if existing:
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('login'))

        hashed_pw = generate_password_hash(password)
        query_db(
            "INSERT INTO users (name, email, phone, password_hash) VALUES (?, ?, ?, ?)",
            (name, email, phone, hashed_pw), commit=True
        )
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter email and password.', 'danger')
            return redirect(url_for('login'))

        user = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Log out user."""
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ============================================================
# USER DASHBOARD & COMPLAINT ROUTES
# ============================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with summary stats."""
    uid = session['user_id']
    total      = query_db("SELECT COUNT(*) AS c FROM complaints WHERE user_id=?", (uid,), one=True)['c']
    pending    = query_db("SELECT COUNT(*) AS c FROM complaints WHERE user_id=? AND status='Pending'", (uid,), one=True)['c']
    in_progress= query_db("SELECT COUNT(*) AS c FROM complaints WHERE user_id=? AND status='In Progress'", (uid,), one=True)['c']
    resolved   = query_db("SELECT COUNT(*) AS c FROM complaints WHERE user_id=? AND status='Resolved'", (uid,), one=True)['c']
    recent     = query_db("""
        SELECT complaint_id, title, category, status, created_at
        FROM complaints WHERE user_id=? ORDER BY created_at DESC LIMIT 5
    """, (uid,))
    return render_template('dashboard.html',
                           total=total, pending=pending,
                           in_progress=in_progress, resolved=resolved,
                           recent=recent)


@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_complaint():
    """Submit a new complaint."""
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category    = request.form.get('category', '').strip()
        location    = request.form.get('location', '').strip()
        uid         = session['user_id']

        if not title or not description or not category:
            flash('Title, description and category are required.', 'danger')
            return redirect(url_for('submit_complaint'))

        # Handle optional photo upload
        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                photo_filename = f"{secrets.token_hex(8)}_{secure_filename(file.filename)}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            elif file and file.filename != '' and not allowed_file(file.filename):
                flash('Invalid file type. Allowed: png, jpg, jpeg, gif, pdf', 'danger')
                return redirect(url_for('submit_complaint'))

        # Generate unique complaint ID (retry if collision)
        complaint_id = generate_complaint_id()
        while query_db("SELECT id FROM complaints WHERE complaint_id=?", (complaint_id,), one=True):
            complaint_id = generate_complaint_id()

        query_db("""
            INSERT INTO complaints (complaint_id, user_id, title, description, category, photo, location)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (complaint_id, uid, title, description, category, photo_filename, location), commit=True)

        # --------------------------------------------------------
        # Send Email Notification to Admin
        # --------------------------------------------------------
        admin_email = app.config['MAIL_USERNAME']
        user_name = session.get('user_name', 'Unknown User')
        
        msg = Message("New Complaint Submitted", recipients=[admin_email])
        msg.body = f"""Hello Admin,

A new complaint has been submitted.

Complaint ID: {complaint_id}
Submitted By: {user_name}
Category/Department: {category}
Issue/Title: {title}
Description: {description}

Please log in to the admin panel to review and update the status.

Thank you,
Smart Complaint System
"""
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending admin email: {e}")
        # --------------------------------------------------------

        flash(f'Complaint submitted! Your ID: {complaint_id}', 'success')
        return redirect(url_for('my_complaints'))

    return render_template('submit_complaint.html')


@app.route('/my_complaints')
@login_required
def my_complaints():
    """List user's own complaints with optional status filter."""
    uid    = session['user_id']
    status = request.args.get('status', 'all')

    if status != 'all':
        complaints = query_db(
            "SELECT * FROM complaints WHERE user_id=? AND status=? ORDER BY created_at DESC",
            (uid, status)
        )
    else:
        complaints = query_db(
            "SELECT * FROM complaints WHERE user_id=? ORDER BY created_at DESC", (uid,)
        )
    return render_template('my_complaints.html', complaints=complaints, status_filter=status)


@app.route('/complaint/<complaint_id>')
@login_required
def complaint_detail(complaint_id):
    """Full detail of a single complaint."""
    uid = session['user_id']
    complaint = query_db("""
        SELECT c.*, d.name AS department_name
        FROM complaints c
        LEFT JOIN departments d ON c.department_id = d.id
        WHERE c.complaint_id=? AND c.user_id=?
    """, (complaint_id, uid), one=True)

    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('my_complaints'))

    return render_template('complaint_detail.html', complaint=complaint)


# ============================================================
# ADMIN ROUTES
# ============================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = query_db("SELECT * FROM admins WHERE username=?", (username,), one=True)
        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_id']   = admin['id']
            session['admin_name'] = admin['username']
            flash(f"Welcome, Admin {admin['username']}!", 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    """Admin logout."""
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    flash('Admin logged out.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with stats."""
    total       = query_db("SELECT COUNT(*) AS c FROM complaints", one=True)['c']
    pending     = query_db("SELECT COUNT(*) AS c FROM complaints WHERE status='Pending'", one=True)['c']
    in_progress = query_db("SELECT COUNT(*) AS c FROM complaints WHERE status='In Progress'", one=True)['c']
    resolved    = query_db("SELECT COUNT(*) AS c FROM complaints WHERE status='Resolved'", one=True)['c']
    total_users = query_db("SELECT COUNT(*) AS c FROM users", one=True)['c']
    recent      = query_db("""
        SELECT c.id, c.complaint_id, c.title, c.category, c.status, c.created_at, u.name AS user_name
        FROM complaints c JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC LIMIT 7
    """)
    return render_template('admin_dashboard.html',
                           total=total, pending=pending,
                           in_progress=in_progress, resolved=resolved,
                           total_users=total_users, recent=recent)


@app.route('/admin/complaints')
@admin_required
def admin_complaints():
    """All complaints with search and filter."""
    search = request.args.get('search', '').strip()
    status = request.args.get('status', 'all')

    sql = """
        SELECT c.*, u.name AS user_name, d.name AS department_name
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        LEFT JOIN departments d ON c.department_id = d.id
        WHERE 1=1
    """
    params = []

    if status != 'all':
        sql += " AND c.status = ?"
        params.append(status)

    if search:
        sql += " AND (c.complaint_id LIKE ? OR c.title LIKE ? OR u.name LIKE ? OR c.category LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like, like, like])

    sql += " ORDER BY c.created_at DESC"
    complaints = query_db(sql, params)
    return render_template('admin_complaints.html',
                           complaints=complaints, search=search, status_filter=status)


@app.route('/admin/update/<int:complaint_id>', methods=['GET', 'POST'])
@admin_required
def admin_update(complaint_id):
    """Admin: Update complaint status / department / notes."""
    if request.method == 'POST':
        new_status  = request.form.get('status')
        dept_id     = request.form.get('department_id') or None
        admin_notes = request.form.get('admin_notes', '').strip()

        # Fetch old complaint to check if status changed, and to get user email
        old_complaint = query_db("""
            SELECT c.*, u.email, u.name as user_name
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = ?
        """, (complaint_id,), one=True)

        query_db("""
            UPDATE complaints
            SET status=?, department_id=?, admin_notes=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (new_status, dept_id, admin_notes, complaint_id), commit=True)
        
        # Send Email Notification
        if old_complaint and old_complaint['status'] != new_status:
            admin_email = app.config['MAIL_USERNAME']
            user_name = old_complaint['user_name']
            c_id = old_complaint['complaint_id']
            title = old_complaint['title']
            
            msg = Message("Complaint Status Updated", recipients=[admin_email])
            msg.body = f"""Hello Admin,

The complaint regarding "{title}" from user {user_name} has been updated.

Complaint ID: {c_id}
New Status: {new_status}

Thank you,
Smart Complaint System
"""
            try:
                mail.send(msg)
            except Exception as e:
                print(f"Error sending email: {e}")

        flash('Complaint updated successfully.', 'success')
        return redirect(url_for('admin_complaints'))

    complaint   = query_db("""
        SELECT c.*, u.name AS user_name FROM complaints c
        JOIN users u ON c.user_id=u.id WHERE c.id=?
    """, (complaint_id,), one=True)
    departments = query_db("SELECT * FROM departments ORDER BY name")

    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('admin_complaints'))

    return render_template('admin_update.html',
                           complaint=complaint, departments=departments)


@app.route('/admin/delete/<int:complaint_id>', methods=['POST'])
@admin_required
def admin_delete(complaint_id):
    """Admin: Delete a complaint."""
    row = query_db("SELECT photo FROM complaints WHERE id=?", (complaint_id,), one=True)
    if row and row['photo']:
        path = os.path.join(app.config['UPLOAD_FOLDER'], row['photo'])
        if os.path.exists(path):
            os.remove(path)

    query_db("DELETE FROM complaints WHERE id=?", (complaint_id,), commit=True)
    flash('Complaint deleted.', 'success')
    return redirect(url_for('admin_complaints'))


@app.route('/admin/report')
@admin_required
def admin_report():
    """Report page."""
    by_category = query_db("""
        SELECT category,
               COUNT(*) AS total,
               SUM(CASE WHEN status='Pending' THEN 1 ELSE 0 END) AS pending,
               SUM(CASE WHEN status='In Progress' THEN 1 ELSE 0 END) AS in_progress,
               SUM(CASE WHEN status='Resolved' THEN 1 ELSE 0 END) AS resolved
        FROM complaints GROUP BY category ORDER BY total DESC
    """)
    by_department = query_db("""
        SELECT COALESCE(d.name, 'Unassigned') AS dept_name,
               COUNT(*) AS total,
               SUM(CASE WHEN c.status='Resolved' THEN 1 ELSE 0 END) AS resolved
        FROM complaints c
        LEFT JOIN departments d ON c.department_id = d.id
        GROUP BY c.department_id ORDER BY total DESC
    """)
    grand_total    = query_db("SELECT COUNT(*) AS c FROM complaints", one=True)['c']
    grand_resolved = query_db("SELECT COUNT(*) AS c FROM complaints WHERE status='Resolved'", one=True)['c']

    return render_template('report.html',
                           by_category=by_category, by_department=by_department,
                           grand_total=grand_total, grand_resolved=grand_resolved)


# ============================================================
# Run the Application
# ============================================================
if __name__ == '__main__':
    # Initialize the database (creates tables + seeds data on first run)
    with app.app_context():
        init_db()

    # Start the Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)
