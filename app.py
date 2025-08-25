import os
import sqlite3

DB_PATH = 'library.db'
SCHEMA_PATH = 'full_schema.sql'

def init_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            with open(SCHEMA_PATH, 'r') as f:
                conn.executescript(f.read())

init_db()
# --- Helper for user-friendly action descriptions ---
def get_action_description(log):
    action = log['action']
    details = log['details'] or ''
    desc = ''
    if action == 'add_wishlist':
        # Try to get book title
        book_id = details.split('=')[1] if '=' in details else ''
        db = get_db()
        book = db.execute('SELECT title FROM book_db WHERE book_id = ?', (book_id,)).fetchone()
        desc = f"Added to wishlist: <a href='/admin/book/{book_id}' class='log-link'>{book['title'] if book else book_id}</a>"
    elif action == 'remove_wishlist':
        book_id = details.split('=')[1] if '=' in details else ''
        db = get_db()
        book = db.execute('SELECT title FROM book_db WHERE book_id = ?', (book_id,)).fetchone()
        desc = f"Removed from wishlist: <a href='/admin/book/{book_id}' class='log-link'>{book['title'] if book else book_id}</a>"
    elif action == 'reserve_book':
        book_id = details.split('=')[1] if '=' in details else ''
        db = get_db()
        book = db.execute('SELECT title FROM book_db WHERE book_id = ?', (book_id,)).fetchone()
        desc = f"Reserved book: <a href='/admin/book/{book_id}' class='log-link'>{book['title'] if book else book_id}</a>"
    elif action == 'return_book':
        book_id = details.split('=')[1] if '=' in details else ''
        db = get_db()
        book = db.execute('SELECT title FROM book_db WHERE book_id = ?', (book_id,)).fetchone()
        desc = f"Returned book: <a href='/admin/book/{book_id}' class='log-link'>{book['title'] if book else book_id}</a>"
    else:
        desc = action.replace('_', ' ').capitalize() + (f": {details}" if details else '')
    return desc

# Correct import for secure_filename
from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
import sqlite3

import os
from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify
import bcrypt
from datetime import date, timedelta

# --- Flask App Configuration ---
app = Flask(__name__)
# Load secrets from environment variables, with a fallback for local testing
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL')
# For local development, fallback to SQLite
app.config['LOCAL_DATABASE'] = 'library.db'

# --- Notifications API ---
@app.route('/notifications')
def notifications():
    if 'mob_no' not in session:
        return jsonify({'notifications': []})
    db = get_db()
    user = db.execute('SELECT * FROM member_db WHERE mob_no = ?', (session['mob_no'],)).fetchone()
    notifs = db.execute('SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 20', (user['member_id'],)).fetchall()
    unread_count = db.execute('SELECT COUNT(*) as cnt FROM notifications WHERE user_id = ? AND is_read = 0', (user['member_id'],)).fetchone()['cnt']
    return jsonify({'notifications': [dict(n) for n in notifs], 'unread_count': unread_count})

# --- Notification Helper ---
def create_notification(user_id, message):
    db = get_db()
    db.execute('INSERT INTO notifications (user_id, message) VALUES (?, ?)', (user_id, message))
    db.commit()

    # --- User Activity Logging Helper ---
def log_user_activity(user_id, action, details=None):
    db = get_db()
    db.execute('INSERT INTO user_activity (user_id, action, details) VALUES (?, ?, ?)', (user_id, action, details))
    db.commit()

# --- Profile Management ---


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'mob_no' not in session:
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM member_db WHERE mob_no = ?', (session['mob_no'],)).fetchone()
    # Handle missing profile_pic gracefully
    profile_pic = user['profile_pic'] if 'profile_pic' in user.keys() else None
    error = None
    success = None
    if request.method == 'POST':
        first_name = request.form.get('first_name', user['first_name'])
        last_name = request.form.get('last_name', user['last_name'])
        address = request.form.get('address', user['address'])
        email_id = request.form.get('email_id', user['email_id'])
        mob_no = request.form.get('mob_no', user['mob_no'])
        # Password change
        new_password = request.form.get('new_password')
        if new_password:
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        else:
            hashed = user['password']
        # Handle file upload
        file = request.files.get('profile_pic')
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{user['mob_no']}_" + file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_pic = filename
        db.execute('UPDATE member_db SET first_name=?, last_name=?, address=?, email_id=?, mob_no=?, password=?, profile_pic=? WHERE member_id=?',
                   (first_name, last_name, address, email_id, mob_no, hashed, profile_pic, user['member_id']))
        db.commit()
        session['mob_no'] = mob_no
        success = 'Profile updated successfully.'
        # Refresh user data
        user = db.execute('SELECT * FROM member_db WHERE mob_no = ?', (mob_no,)).fetchone()
    return render_template('profile.html', user=user, error=error, success=success)

# Profile picture upload config (must be after app is defined)
UPLOAD_FOLDER = 'static/profile_pics'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Database Functions ---
def get_db():
    """
    Connects to the database and returns a connection object.
    It stores the connection in the 'g' object to reuse it for the same request.
    This function now supports both PostgreSQL (for production) and SQLite (for local dev).
    """
    db = getattr(g, '_database', None)
    if db is not None:
        return db

    # Always use SQLite for this application
    db = getattr(g, '_database', None)
    if db is not None:
        return db
    db = g._database = sqlite3.connect(app.config['LOCAL_DATABASE'])
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Closes the database connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Authentication Routes ---
@app.before_request
def check_auth():
    """
    Runs before every request to check for user authentication.
    Redirects to the login page if the user is not authenticated,
    unless the request is for the login/register page or static files.
    """
    allowed_routes = ['login', 'register', 'static', 'get_chatbot_response', 'forgot_password', 'reset_password']
    if request.endpoint in allowed_routes:
        return
    
    if 'mob_no' not in session:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login and redirects to the appropriate dashboard."""
    error = None
    if request.method == 'POST':
        mob_no = request.form['mob_no']
        password = request.form['password'].encode('utf-8')
        
        db = get_db()
        user = db.execute('SELECT * FROM member_db WHERE mob_no = ?', (mob_no,)).fetchone()
        
        if user and bcrypt.checkpw(password, user['password']):
            session['mob_no'] = user['mob_no']
            session['name'] = f"{user['first_name']} {user['last_name']}"
            if user['role'] == 'admin':
                return redirect(url_for('admin_page'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            error = 'Incorrect mobile number or password.'
    
    return render_template('login_register.html', error=error)

@app.route('/register', methods=['POST'])
def register():
    """Handles user registration and creates a new member record."""
    error = None
    if request.method == 'POST':
        db = get_db()
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        mob_no = request.form['mob_no']
        email_id = request.form['email_id']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        role = request.form['role']
        
        check_mob = db.execute('SELECT mob_no FROM member_db WHERE mob_no = ?', (mob_no,)).fetchone()
        
        if check_mob:
            error = 'Mobile number is already registered'
        else:
            db.execute('INSERT INTO member_db (first_name, last_name, address, mob_no, email_id, password, role) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (first_name, last_name, address, mob_no, email_id, password, role))
            db.commit()
            return redirect(url_for('login'))
            
    return render_template('login_register.html', error=error)

@app.route('/logout')
def logout():
    """Clears the session and logs the user out."""
    session.clear()
    return redirect(url_for('login'))

# --- Admin Pages ---
def get_user_role():
    """Helper function to get the current user's role."""
    if 'mob_no' in session:
        db = get_db()
        user = db.execute('SELECT role FROM member_db WHERE mob_no = ?', (session['mob_no'],)).fetchone()
        if user:
            return user['role']
    return None

@app.route('/admin_page')
def admin_page():
    """Admin dashboard route, showing key statistics."""
    if get_user_role() != 'admin':
        return redirect(url_for('user_dashboard'))

    db = get_db()
    total_books = db.execute("SELECT COUNT(*) AS cnt FROM book_db").fetchone()['cnt']
    total_users = db.execute("SELECT COUNT(*) AS cnt FROM member_db WHERE role='user'").fetchone()['cnt']
    pending_issues = db.execute("SELECT COUNT(*) AS cnt FROM issued_books WHERE return_date IS NULL").fetchone()['cnt']
    due_today = db.execute("SELECT COUNT(*) AS cnt FROM issued_books WHERE due_date = ? AND return_date IS NULL", (date.today(),)).fetchone()['cnt']
    
    recent_issues = db.execute("SELECT ib.issue_id, m.first_name || ' ' || m.last_name AS member_name, b.title AS book_title, ib.issue_date, ib.due_date FROM issued_books ib JOIN member_db m ON ib.member_id = m.member_id JOIN book_db b ON ib.book_id = b.book_id ORDER BY ib.issue_date DESC LIMIT 5").fetchall()

    # Get count of pending reservations (status = 'pending')
    pending_count = db.execute("SELECT COUNT(*) AS cnt FROM reservations WHERE status = 'pending'").fetchone()['cnt']
    # User Activity Log (last 20 actions)
    activity_log = db.execute('''
        SELECT ua.*, m.first_name, m.last_name
        FROM user_activity ua
        JOIN member_db m ON ua.user_id = m.member_id
        ORDER BY ua.created_at DESC
        LIMIT 20
    ''').fetchall()
    # Add user profile links and friendly descriptions
    log_rows = []
    for log in activity_log:
        log = dict(log)
        log['user_link'] = f"<a href='/admin/user/{log['user_id']}' class='log-link'>{log['first_name']} {log['last_name']}</a>"
        log['desc'] = get_action_description(log)
        log_rows.append(log)
    if request.args.get('ajax') == '1':
        # Return JSON for AJAX live update
        return jsonify([
            {
                'created_at': log['created_at'],
                'user_link': log['user_link'],
                'desc': log['desc'],
                'action': log['action']
            } for log in log_rows
        ])
    return render_template('admin_page.html',
        total_books=total_books, total_users=total_users, pending_issues=pending_issues, due_today=due_today,
        recent_issues=recent_issues, pending_count=pending_count, activity_log=log_rows)

# --- Export user activity log as CSV ---
import csv
from io import StringIO
@app.route('/admin/export_activity_log')
def export_activity_log():
    db = get_db()
    logs = db.execute('''
        SELECT ua.created_at, m.first_name, m.last_name, ua.action, ua.details
        FROM user_activity ua
        JOIN member_db m ON ua.user_id = m.member_id
        ORDER BY ua.created_at DESC
        LIMIT 1000
    ''').fetchall()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Timestamp', 'User', 'Action', 'Details'])
    for log in logs:
        cw.writerow([
            log['created_at'],
            f"{log['first_name']} {log['last_name']}",
            log['action'],
            log['details']
        ])
    output = si.getvalue()
    return app.response_class(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=user_activity_log.csv'}
    )
    return render_template('admin_page.html', total_books=total_books, total_users=total_users, pending_issues=pending_issues, due_today=due_today, recent_issues=recent_issues, pending_count=pending_count, activity_log=activity_log)

@app.route('/manage_member', methods=['GET', 'POST'])
def manage_member():
    """Manages member CRUD operations."""
    if get_user_role() != 'admin':
        return redirect(url_for('user_dashboard'))

    db = get_db()
    edit_data = None
    
    if request.method == 'POST':
        if 'add_member' in request.form:
            fname = request.form['first_name']
            lname = request.form['last_name']
            address = request.form['address']
            mob_no = request.form['mob_no']
            email = request.form['email_id']
            password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            role = request.form['role']
            db.execute("INSERT INTO member_db (first_name, last_name, address, mob_no, email_id, password, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (fname, lname, address, mob_no, email, password, role))
        elif 'edit_member' in request.form:
            id = request.form['member_id']
            fname = request.form['first_name']
            lname = request.form['last_name']
            address = request.form['address']
            mob_no = request.form['mob_no']
            email = request.form['email_id']
            role = request.form['role']
            db.execute("UPDATE member_db SET first_name=?, last_name=?, address=?, mob_no=?, email_id=?, role=? WHERE member_id=?",
                         (fname, lname, address, mob_no, email, role, id))
        db.commit()
        return redirect(url_for('manage_member'))
    
    if 'edit' in request.args:
        edit_id = request.args['edit']
        edit_data = db.execute("SELECT * FROM member_db WHERE member_id = ?", (edit_id,)).fetchone()
    
    if 'delete' in request.args:
        delete_id = request.args['delete']
        db.execute("DELETE FROM member_db WHERE member_id = ?", (delete_id,))
        db.commit()
        return redirect(url_for('manage_member'))
    
    members = db.execute("SELECT member_id, first_name, last_name, address, mob_no, email_id, role FROM member_db").fetchall()
    
    return render_template('manage_member.html', members=members, edit_data=edit_data)

@app.route('/manage_book', methods=['GET', 'POST'])
def manage_book():
    """Manages book CRUD operations."""
    if get_user_role() != 'admin':
        return redirect(url_for('user_dashboard'))
    
    db = get_db()
    edit_data = None

    if request.method == 'POST':
        if 'add_book' in request.form:
            title = request.form['title']
            category = request.form['category']
            publisher = request.form['publisher']
            year = request.form['year']
            edition = request.form['edition']
            stock = request.form['total_stock']
            author = request.form['author_name']
            db.execute("INSERT INTO book_db (title, category, publisher, year, edition, total_stock, author_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (title, category, publisher, year, edition, stock, author))
        elif 'edit_book' in request.form:
            id = request.form['book_id']
            title = request.form['title']
            category = request.form['category']
            publisher = request.form['publisher']
            year = request.form['year']
            edition = request.form['edition']
            stock = request.form['total_stock']
            author = request.form['author_name']
            db.execute("UPDATE book_db SET title=?, category=?, publisher=?, year=?, edition=?, total_stock=?, author_name=? WHERE book_id=?",
                         (title, category, publisher, year, edition, stock, author, id))
        db.commit()
        return redirect(url_for('manage_book'))

    if 'edit' in request.args:
        edit_id = request.args['edit']
        edit_data = db.execute("SELECT * FROM book_db WHERE book_id = ?", (edit_id,)).fetchone()
    
    if 'delete' in request.args:
        delete_id = request.args['delete']
        db.execute("DELETE FROM book_db WHERE book_id = ?", (delete_id,))
        db.commit()
        return redirect(url_for('manage_book'))

    books = db.execute("SELECT book_id, title, category, publisher, year, edition, total_stock, author_name FROM book_db").fetchall()
    
    return render_template('manage_book.html', books=books, edit_data=edit_data)

@app.route('/manage_issue')
def manage_issue():
    """Displays all issued books."""
    if get_user_role() != 'admin':
        return redirect(url_for('user_dashboard'))

    db = get_db()
    issued_records = db.execute("SELECT ib.issue_id, m.first_name || ' ' || m.last_name AS member_name, b.title AS book_title, ib.issue_date, ib.due_date, ib.return_date FROM issued_books ib JOIN member_db m ON ib.member_id = m.member_id JOIN book_db b ON ib.book_id = b.book_id ORDER BY ib.issue_date DESC").fetchall()
    return render_template('manage_issue.html', issued_records=issued_records)

@app.route('/manage_fine', methods=['GET', 'POST'])
def manage_fine():
    """Manages fines, including filtering and marking as paid."""
    if get_user_role() != 'admin':
        return redirect(url_for('user_dashboard'))
    
    db = get_db()
    
    if request.method == 'POST':
        if 'pay_fine' in request.form:
            fine_id = request.form['fine_id']
            db.execute("UPDATE fines SET status = 'Paid', payment_date = ? WHERE fine_id = ?", (date.today(), fine_id))
            db.commit()
            # Notify user and admin
            fine = db.execute("SELECT f.*, ib.member_id, b.title FROM fines f JOIN issued_books ib ON f.issue_id = ib.issue_id JOIN book_db b ON ib.book_id = b.book_id WHERE f.fine_id = ?", (fine_id,)).fetchone()
            if fine:
                admins = db.execute('SELECT member_id FROM member_db WHERE role = "admin"').fetchall()
                for admin in admins:
                    create_notification(admin['member_id'], f"Fine paid for '{fine['title']}' by member ID {fine['member_id']}")
                create_notification(fine['member_id'], f"Your fine for '{fine['title']}' has been paid.")
            return redirect(url_for('manage_fine'))
    
    if 'delete' in request.args:
        fine_id = request.args['delete']
        db.execute("DELETE FROM fines WHERE fine_id = ?", (fine_id,))
        db.commit()
        return redirect(url_for('manage_fine'))
    
    status_filter = request.args.get('status', 'all')
    member_filter = request.args.get('member', '')

    query = """
        SELECT f.fine_id, f.issue_id, f.fine_amount, f.days_late, f.status, f.fine_date, f.payment_date,
               m.member_id, m.first_name, m.last_name, m.mob_no, m.email_id,
               b.book_id, b.title, b.author_name,
               ib.issue_date, ib.due_date, ib.return_date
        FROM fines f
        JOIN issued_books ib ON f.issue_id = ib.issue_id
        JOIN member_db m ON ib.member_id = m.member_id
        JOIN book_db b ON ib.book_id = b.book_id
        WHERE 1=1
    """
    
    params = []
    if status_filter != 'all':
        query += " AND f.status = ?"
        params.append(status_filter)
    if member_filter:
        query += " AND (m.first_name LIKE ? OR m.last_name LIKE ? OR m.first_name || ' ' || m.last_name LIKE ?)"
        params.extend([f"%{member_filter}%"] * 3)

    query += " ORDER BY f.fine_date DESC"

    fines = db.execute(query, params).fetchall()

    total_fines = db.execute("SELECT COUNT(*) AS count FROM fines").fetchone()['count']
    pending_fines = db.execute("SELECT COUNT(*) AS count FROM fines WHERE status = 'Pending'").fetchone()['count']
    paid_fines = db.execute("SELECT COUNT(*) AS count FROM fines WHERE status = 'Paid'").fetchone()['count']
    total_amount = db.execute("SELECT COALESCE(SUM(fine_amount), 0) AS total FROM fines WHERE status = 'Pending'").fetchone()['total']

    return render_template('manage_fine.html', fines=fines, total_fines=total_fines, pending_fines=pending_fines, paid_fines=paid_fines, total_amount=total_amount, status_filter=status_filter, member_filter=member_filter)

@app.route('/manage_return', methods=['GET', 'POST'])
def manage_return():
    """Manages book returns, calculates fines, and tracks overdue items."""
    if get_user_role() != 'admin':
        return redirect(url_for('user_dashboard'))

    db = get_db()
    
    if request.method == 'POST' and 'process_return' in request.form:
        issue_id = request.form['issue_id']
        return_date = date.today().isoformat()
        issue = db.execute("SELECT ib.*, m.first_name, m.last_name, m.member_id, b.title FROM issued_books ib JOIN member_db m ON ib.member_id = m.member_id JOIN book_db b ON ib.book_id = b.book_id WHERE ib.issue_id = ?", (issue_id,)).fetchone()
        if issue:
            due_date = date.fromisoformat(issue['due_date'])
            days_late = max(0, (date.today() - due_date).days)
            fine = days_late * 5
            db.execute("UPDATE issued_books SET return_date = ? WHERE issue_id = ?", (return_date, issue_id))
            if fine > 0:
                db.execute("INSERT INTO fines (issue_id, fine_amount, days_late, status, fine_date) VALUES (?, ?, ?, 'Pending', ?)",
                            (issue_id, fine, days_late, date.today()))
            db.commit()
            # Notify user and admin
            admins = db.execute('SELECT member_id FROM member_db WHERE role = "admin"').fetchall()
            for admin in admins:
                create_notification(admin['member_id'], f"Book '{issue['title']}' returned by {issue['first_name']} {issue['last_name']}")
            create_notification(issue['member_id'], f"You have returned '{issue['title']}'.")
            
    if 'delete' in request.args:
        issue_id = request.args['delete']
        db.execute("DELETE FROM fines WHERE issue_id = ?", (issue_id,))
        db.execute("DELETE FROM issued_books WHERE issue_id = ?", (issue_id,))
        db.commit()
        return redirect(url_for('manage_return'))

    status_filter = request.args.get('status', 'all')
    member_filter = request.args.get('member', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    query = """
        SELECT ib.issue_id, ib.issue_date, ib.due_date, ib.return_date,
               m.member_id, m.first_name, m.last_name, m.mob_no, m.email_id,
               b.book_id, b.title, b.author_name, b.category,
               (CASE WHEN ib.return_date IS NULL AND ib.due_date < CURRENT_DATE THEN CAST((JULIANDAY(CURRENT_DATE) - JULIANDAY(ib.due_date)) AS INTEGER)
                     WHEN ib.return_date IS NOT NULL AND ib.return_date > ib.due_date THEN CAST((JULIANDAY(ib.return_date) - JULIANDAY(ib.due_date)) AS INTEGER)
                     ELSE 0 END) AS days_overdue,
               (CASE WHEN f.fine_amount IS NOT NULL THEN f.fine_amount ELSE 0 END) AS fine_amount,
               f.status AS fine_status
        FROM issued_books ib
        JOIN member_db m ON ib.member_id = m.member_id
        JOIN book_db b ON ib.book_id = b.book_id
        LEFT JOIN fines f ON ib.issue_id = f.issue_id
        WHERE 1=1
    """

    params = []
    if status_filter == 'pending':
        query += " AND ib.return_date IS NULL"
    elif status_filter == 'returned':
        query += " AND ib.return_date IS NOT NULL"
    
    if member_filter:
        query += " AND (m.first_name LIKE ? OR m.last_name LIKE ? OR m.first_name || ' ' || m.last_name LIKE ?)"
        params.extend([f"%{member_filter}%"] * 3)
    
    if date_from:
        query += " AND ib.issue_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND ib.issue_date <= ?"
        params.append(date_to)

    query += " ORDER BY ib.issue_date DESC"
    returns = db.execute(query, params).fetchall()

    total_issues = db.execute("SELECT COUNT(*) AS count FROM issued_books").fetchone()['count']
    pending_returns = db.execute("SELECT COUNT(*) AS count FROM issued_books WHERE return_date IS NULL").fetchone()['count']
    completed_returns = db.execute("SELECT COUNT(*) AS count FROM issued_books WHERE return_date IS NOT NULL").fetchone()['count']
    overdue_books = db.execute("SELECT COUNT(*) AS count FROM issued_books WHERE return_date IS NULL AND due_date < CURRENT_DATE").fetchone()['count']

    return render_template('manage_return.html', returns=returns, total_issues=total_issues, pending_returns=pending_returns, completed_returns=completed_returns, overdue_books=overdue_books, status_filter=status_filter, member_filter=member_filter, date_from=date_from, date_to=date_to)

@app.route('/report_page')
def report_page():
    """Generates various reports and statistics."""
    if get_user_role() != 'admin':
        return redirect(url_for('user_dashboard'))

    db = get_db()
    
    timeframe = request.args.get('tf', 'daily')
    if timeframe == 'weekly':
        start_date = (date.today() - timedelta(days=7)).isoformat()
    elif timeframe == 'monthly':
        start_date = (date.today() - timedelta(days=30)).isoformat()
    else:
        start_date = date.today().isoformat()
    
    borrow_summary = db.execute("SELECT COUNT(*) AS cnt FROM issued_books WHERE issue_date >= ?", (start_date,)).fetchone()['cnt']
    fine_summary = db.execute("SELECT COALESCE(SUM(fine_amount), 0) AS total FROM fines WHERE status='Paid' AND payment_date >= ?", (start_date,)).fetchone()['total']

    # Report Queries
    all_issued = db.execute("SELECT ib.issue_id, b.title, m.first_name || ' ' || m.last_name AS member_name, ib.issue_date, ib.due_date, ib.return_date FROM issued_books ib JOIN book_db b ON ib.book_id = b.book_id JOIN member_db m ON ib.member_id = m.member_id ORDER BY ib.issue_date DESC").fetchall()
    top_books = db.execute("SELECT b.book_id, b.title, b.author_name, COUNT(*) AS borrow_count FROM issued_books ib JOIN book_db b ON ib.book_id = b.book_id GROUP BY b.book_id ORDER BY borrow_count DESC LIMIT 10").fetchall()
    active_members = db.execute("SELECT m.member_id, m.first_name || ' ' || m.last_name AS member_name, COUNT(*) AS borrow_count FROM issued_books ib JOIN member_db m ON ib.member_id = m.member_id GROUP BY m.member_id ORDER BY borrow_count DESC LIMIT 10").fetchall()
    overdue = db.execute("SELECT ib.issue_id, b.title, m.first_name || ' ' || m.last_name AS member_name, ib.due_date FROM issued_books ib JOIN book_db b ON ib.book_id = b.book_id JOIN member_db m ON ib.member_id = m.member_id WHERE ib.due_date < CURRENT_DATE AND ib.return_date IS NULL ORDER BY ib.due_date ASC").fetchall()
    low_stock = db.execute("SELECT book_id, title, total_stock FROM book_db WHERE total_stock < 3 ORDER BY total_stock ASC").fetchall()
    
    # New Reports
    monthly_borrow = db.execute("SELECT SUBSTR(issue_date, 1, 7) AS month, COUNT(*) AS borrow_count FROM issued_books GROUP BY month ORDER BY month DESC LIMIT 12").fetchall()
    category_popularity = db.execute("SELECT b.category, COUNT(*) AS borrow_count FROM issued_books ib JOIN book_db b ON ib.book_id = b.book_id GROUP BY b.category ORDER BY borrow_count DESC").fetchall()
    fine_collection = db.execute("SELECT SUBSTR(payment_date, 1, 7) AS month, SUM(fine_amount) AS total_collected FROM fines WHERE status='Paid' GROUP BY month ORDER BY month DESC LIMIT 12").fetchall()
    top_authors = db.execute("SELECT b.author_name, COUNT(*) AS borrow_count FROM issued_books ib JOIN book_db b ON ib.book_id = b.book_id GROUP BY b.author_name ORDER BY borrow_count DESC LIMIT 10").fetchall()

    return render_template('report_page.html', timeframe=timeframe, borrow_summary=borrow_summary, fine_summary=fine_summary, all_issued=all_issued, top_books=top_books, active_members=active_members, overdue=overdue, low_stock=low_stock, monthly_borrow=monthly_borrow, category_popularity=category_popularity, fine_collection=fine_collection, top_authors=top_authors)

@app.route('/wishlist_data', methods=['GET', 'POST'])
def wishlist_data():
    """Manages books in the admin wishlist and handles issuing from there."""
    if get_user_role() != 'admin':
        return redirect(url_for('user_dashboard'))

    db = get_db()
    if request.method == 'POST' and 'issue_book' in request.form:
        member_id = request.form['member_id']
        book_id = request.form['book_id']
        issue_date = date.today().isoformat()
        due_date = (date.today() + timedelta(days=14)).isoformat()
        
        stock_check = db.execute("SELECT total_stock FROM book_db WHERE book_id = ?", (book_id,)).fetchone()['total_stock']
        issued_count = db.execute("SELECT COUNT(*) FROM issued_books WHERE book_id = ? AND return_date IS NULL", (book_id,)).fetchone()[0]

        if issued_count < stock_check:
            db.execute("INSERT INTO issued_books (member_id, book_id, issue_date, due_date) VALUES (?, ?, ?, ?)", (member_id, book_id, issue_date, due_date))
            db.execute("DELETE FROM wishlist WHERE member_id = ? AND book_id = ?", (member_id, book_id))
            db.commit()
            session['message'] = 'Book issued successfully!'
        else:
            session['message'] = 'No stock available for this book.'
            
        return redirect(url_for('wishlist_data'))

    wishlist_records = db.execute("SELECT ib.wishlist_id, ib.member_id, ib.book_id, m.first_name || ' ' || m.last_name AS member_name, b.title AS book_title FROM wishlist ib JOIN member_db m ON ib.member_id = m.member_id JOIN book_db b ON ib.book_id = b.book_id ORDER BY ib.added_date DESC").fetchall()
    message = session.pop('message', None)
    return render_template('wishlist_data.html', wishlist_records=wishlist_records, message=message)

# --- User Dashboard ---
@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    """User dashboard, displaying books, history, and fines."""
    if get_user_role() == 'admin':
        return redirect(url_for('admin_page'))

    db = get_db()
    user_data = db.execute("SELECT * FROM member_db WHERE mob_no = ?", (session['mob_no'],)).fetchone()
    member_id = user_data['member_id']

    if request.method == 'POST' and 'toggle_wishlist' in request.form:
        book_id = request.form['book_id']
        wishlist_check = db.execute("SELECT * FROM wishlist WHERE member_id = ? AND book_id = ?", (member_id, book_id)).fetchone()
        if wishlist_check:
            db.execute("DELETE FROM wishlist WHERE member_id = ? AND book_id = ?", (member_id, book_id))
            session['message'] = "Book removed from wishlist!"
            log_user_activity(member_id, 'remove_wishlist', f'book_id={book_id}')
        else:
            db.execute("INSERT INTO wishlist (member_id, book_id) VALUES (?, ?)", (member_id, book_id))
            session['message'] = "Book added to wishlist!"
            log_user_activity(member_id, 'add_wishlist', f'book_id={book_id}')
        db.commit()
        return redirect(url_for('user_dashboard'))

    # Statistics
    total_issued = db.execute("SELECT COUNT(*) AS count FROM issued_books WHERE member_id = ?", (member_id,)).fetchone()['count']
    currently_issued = db.execute("SELECT COUNT(*) AS count FROM issued_books WHERE member_id = ? AND return_date IS NULL", (member_id,)).fetchone()['count']
    overdue_books = db.execute("SELECT COUNT(*) AS count FROM issued_books WHERE member_id = ? AND return_date IS NULL AND due_date < CURRENT_DATE", (member_id,)).fetchone()['count']
    pending_fines = db.execute("SELECT COALESCE(SUM(f.fine_amount), 0) AS total FROM fines f JOIN issued_books ib ON f.issue_id = ib.issue_id WHERE ib.member_id = ? AND f.status = 'Pending'", (member_id,)).fetchone()['total']

    # Search & Books
    search_query = request.args.get('search', '')
    search_filter = request.args.get('filter', 'all')
    params = [member_id]
    where_clause = ""
    
    if search_query:
        if search_filter == 'all':
            where_clause = "WHERE b.title LIKE ? OR b.author_name LIKE ? OR b.category LIKE ?"
            params.extend([f"%{search_query}%"] * 3)
        elif search_filter == 'title':
            where_clause = "WHERE b.title LIKE ?"
            params.append(f"%{search_query}%")
        elif search_filter == 'author':
            where_clause = "WHERE b.author_name LIKE ?"
            params.append(f"%{search_query}%")
        elif search_filter == 'category':
            where_clause = "WHERE b.category LIKE ?"
            params.append(f"%{search_query}%")

    books_query = f"""
        SELECT b.book_id, b.title, b.author_name, b.category, b.year, b.total_stock,
               (SELECT COUNT(*) FROM issued_books ib WHERE ib.book_id = b.book_id AND ib.return_date IS NULL) AS issued_count,
               EXISTS(SELECT 1 FROM wishlist w WHERE w.book_id = b.book_id AND w.member_id = ?) AS in_wishlist,
               EXISTS(SELECT 1 FROM reservations r WHERE r.book_id = b.book_id AND r.member_id = ? AND r.status = 'active') AS has_reserved
        FROM book_db b
        {where_clause}
        ORDER BY b.title
    """
    params = [member_id, member_id] + params[1:]
    books = db.execute(books_query, tuple(params)).fetchall()

    # Issued Books
    issued_books_query = """
        SELECT ib.issue_id, ib.issue_date, ib.due_date, ib.return_date,
               b.title, b.author_name, b.category,
               (CASE WHEN ib.return_date IS NULL AND ib.due_date < CURRENT_DATE THEN CAST((JULIANDAY(CURRENT_DATE) - JULIANDAY(ib.due_date)) AS INTEGER) ELSE 0 END) AS days_overdue,
               f.fine_amount, f.status AS fine_status
        FROM issued_books ib
        JOIN book_db b ON ib.book_id = b.book_id
        LEFT JOIN fines f ON ib.issue_id = f.issue_id
        WHERE ib.member_id = ?
        ORDER BY ib.issue_date DESC
    """
    issued_records = db.execute(issued_books_query, (member_id,)).fetchall()

    # Wishlist
    wishlist_query = """
        SELECT w.wishlist_id, w.added_date,
               b.book_id, b.title, b.author_name, b.category, b.total_stock,
               (SELECT COUNT(*) FROM issued_books ib WHERE ib.book_id = b.book_id AND ib.return_date IS NULL) AS issued_count
        FROM wishlist w
        JOIN book_db b ON w.book_id = b.book_id
        WHERE w.member_id = ?
        ORDER BY w.added_date DESC
    """
    wishlist_records = db.execute(wishlist_query, (member_id,)).fetchall()

    # Recommendations
    recommended_books = []
    # Get categories the user borrowed most
    cat_row = db.execute("SELECT b.category, COUNT(*) as cnt FROM issued_books ib JOIN book_db b ON ib.book_id = b.book_id WHERE ib.member_id = ? GROUP BY b.category ORDER BY cnt DESC LIMIT 1", (member_id,)).fetchone()
    if cat_row:
        # Recommend books from top category not already issued
        recommended_books = db.execute("SELECT * FROM book_db WHERE category = ? AND book_id NOT IN (SELECT book_id FROM issued_books WHERE member_id = ?) GROUP BY book_id LIMIT 5", (cat_row['category'], member_id)).fetchall()
    if not recommended_books:
        # Fallback: most popular books
        recommended_books = db.execute("SELECT b.*, COUNT(ib.issue_id) as cnt FROM book_db b LEFT JOIN issued_books ib ON b.book_id = ib.book_id GROUP BY b.book_id ORDER BY cnt DESC LIMIT 5").fetchall()

    message = session.pop('message', None)

    return render_template('user_dashboard.html', user_data=user_data, total_issued_count=total_issued, currently_issued_count=currently_issued, overdue_count=overdue_books, pending_fines_amount=pending_fines, search_query=search_query, search_filter=search_filter, books=books, issued_records=issued_records, wishlist_records=wishlist_records, message=message, recommended_books=recommended_books)

@app.route('/reserve_book', methods=['POST'])
def reserve_book():
    if 'mob_no' not in session:
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM member_db WHERE mob_no = ?', (session['mob_no'],)).fetchone()
    member_id = user['member_id']
    book_id = request.form.get('book_id')
    # Check if already reserved
    existing = db.execute('SELECT * FROM reservations WHERE member_id = ? AND book_id = ? AND status = "active"', (member_id, book_id)).fetchone()
    if not existing:
        db.execute('INSERT INTO reservations (member_id, book_id) VALUES (?, ?)', (member_id, book_id))
        db.commit()
        # Notify admin(s)
        admins = db.execute('SELECT member_id FROM member_db WHERE role = "admin"').fetchall()
        book = db.execute('SELECT title FROM book_db WHERE book_id = ?', (book_id,)).fetchone()
        for admin in admins:
            create_notification(admin['member_id'], f"New reservation request for '{book['title']}' by {user['first_name']} {user['last_name']}")
        # Notify user
        create_notification(member_id, f"You have reserved '{book['title']}'.")
    log_user_activity(member_id, 'reserve_book', f'book_id={book_id}')
    return redirect(url_for('user_dashboard'))

@app.route('/my_reservations')
def my_reservations():
    if 'mob_no' not in session:
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM member_db WHERE mob_no = ?', (session['mob_no'],)).fetchone()
    member_id = user['member_id']
    reservations = db.execute('SELECT r.*, b.title, b.author_name FROM reservations r JOIN book_db b ON r.book_id = b.book_id WHERE r.member_id = ? ORDER BY r.reserved_date DESC', (member_id,)).fetchall()
    return render_template('my_reservations.html', reservations=reservations)

# --- Chatbot API Route ---
@app.route('/get_chatbot_response', methods=['POST'])
def get_chatbot_response():
    """
    Handles a user's chatbot query and returns a response.
    Now supports book search and more flexible answers.
    """
    user_message = request.json.get('message', '').lower()
    db = get_db()

    # Book search intent
    if any(word in user_message for word in ['find book', 'search book', 'book by', 'author', 'category', 'title']):
        # Try to extract a keyword
        import re
        match = re.search(r'(?:book|author|category|title)[:\s]+([\w\s]+)', user_message)
        keyword = match.group(1).strip() if match else user_message
        books = db.execute("SELECT title, author_name, category FROM book_db WHERE title LIKE ? OR author_name LIKE ? OR category LIKE ? LIMIT 5", (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")).fetchall()
        if books:
            book_lines = [f"{b['title']} by {b['author_name']} ({b['category']})" for b in books]
            response = "Here are some books I found:\n" + "\n".join(book_lines)
        else:
            response = "Sorry, I couldn't find any books matching your query."
        return jsonify({'response': response})

    # Try to find a direct keyword match (improved)
    response_data = db.execute("SELECT response FROM chatbot_responses WHERE ? LIKE '%' || keyword || '%' OR keyword LIKE '%' || ? || '%'", (user_message, user_message)).fetchone()
    if response_data:
        response = response_data['response']
    else:
        # Fallback response for unhandled questions
        response = "I'm sorry, I don't have information on that. Please ask about library hours, fines, renewals, book search, or borrowing limits."
    return jsonify({'response': response})

@app.route('/')
def home():
    db = get_db()
    chatbot_responses = db.execute('SELECT * FROM chatbot_responses').fetchall()
    db.close()
    return render_template('index.html', chatbot_responses=chatbot_responses)

@app.route('/api/search_books')
def api_search_books():
    """API endpoint for dynamic book search (AJAX)."""
    if get_user_role() == 'admin':
        return jsonify([])

    db = get_db()
    member_id = db.execute("SELECT member_id FROM member_db WHERE mob_no = ?", (session['mob_no'],)).fetchone()['member_id']
    search_query = request.args.get('q', '')
    search_filter = request.args.get('filter', 'all')
    params = [member_id]
    where_clause = ""
    if search_query:
        if search_filter == 'all':
            where_clause = "WHERE b.title LIKE ? OR b.author_name LIKE ? OR b.category LIKE ?"
            params.extend([f"%{search_query}%"] * 3)
        elif search_filter == 'title':
            where_clause = "WHERE b.title LIKE ?"
            params.append(f"%{search_query}%")
        elif search_filter == 'author':
            where_clause = "WHERE b.author_name LIKE ?"
            params.append(f"%{search_query}%")
        elif search_filter == 'category':
            where_clause = "WHERE b.category LIKE ?"
            params.append(f"%{search_query}%")
    books_query = f'''
        SELECT b.book_id, b.title, b.author_name, b.category, b.year, b.total_stock,
               (SELECT COUNT(*) FROM issued_books ib WHERE ib.book_id = b.book_id AND ib.return_date IS NULL) AS issued_count,
               (SELECT COUNT(*) FROM wishlist w WHERE w.book_id = b.book_id AND w.member_id = ?) AS in_wishlist
        FROM book_db b
        {where_clause}
        ORDER BY b.title
    '''
    params = [member_id] + params[1:]  # member_id for wishlist check
    books = db.execute(books_query, tuple(params)).fetchall()
    result = [
        {
            'book_id': book['book_id'],
            'title': book['title'],
            'author_name': book['author_name'],
            'category': book['category'],
            'year': book['year'],
            'total_stock': book['total_stock'],
            'issued_count': book['issued_count'],
            'in_wishlist': bool(book['in_wishlist'])
        }
        for book in books
    ]
    return jsonify(result)

@app.route('/api/toggle_wishlist', methods=['POST'])
def api_toggle_wishlist():
    if 'mob_no' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    db = get_db()
    user_data = db.execute("SELECT * FROM member_db WHERE mob_no = ?", (session['mob_no'],)).fetchone()
    member_id = user_data['member_id']
    book_id = request.form.get('book_id')
    if not book_id:
        return jsonify({'success': False, 'error': 'No book_id provided'}), 400
    wishlist_check = db.execute("SELECT * FROM wishlist WHERE member_id = ? AND book_id = ?", (member_id, book_id)).fetchone()
    if wishlist_check:
        db.execute("DELETE FROM wishlist WHERE member_id = ? AND book_id = ?", (member_id, book_id))
        db.commit()
        return jsonify({'success': True, 'in_wishlist': False})
    else:
        db.execute("INSERT INTO wishlist (member_id, book_id) VALUES (?, ?)", (member_id, book_id))
        db.commit()
        return jsonify({'success': True, 'in_wishlist': True})

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    error = None
    success = None
    if request.method == 'POST':
        mob_no = request.form['mob_no']
        email_id = request.form['email_id']
        db = get_db()
        user = db.execute('SELECT * FROM member_db WHERE mob_no = ? AND email_id = ?', (mob_no, email_id)).fetchone()
        if user:
            return render_template('reset_password.html', mob_no=mob_no, email_id=email_id)
        else:
            error = 'No user found with that mobile number and email.'
    return render_template('forgot_password.html', error=error, success=success)

@app.route('/reset_password', methods=['POST'])
def reset_password():
    mob_no = request.form['mob_no']
    email_id = request.form['email_id']
    new_password = request.form['new_password']
    db = get_db()
    user = db.execute('SELECT * FROM member_db WHERE mob_no = ? AND email_id = ?', (mob_no, email_id)).fetchone()
    if user:
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        db.execute('UPDATE member_db SET password = ? WHERE mob_no = ? AND email_id = ?', (hashed, mob_no, email_id))
        db.commit()
        return render_template('login_register.html', error=None, success='Password reset successful. Please log in.')
    else:
        return render_template('reset_password.html', mob_no=mob_no, email_id=email_id, error='User not found or info incorrect.')

@app.route('/api/search_suggestions')
def search_suggestions():
    q = request.args.get('q', '').strip()
    db = get_db()
    suggestions = set()
    if q:
        # Titles
        for row in db.execute("SELECT title FROM book_db WHERE title LIKE ? LIMIT 5", (f"%{q}%",)):
            suggestions.add(row['title'])
        # Authors
        for row in db.execute("SELECT author_name FROM book_db WHERE author_name LIKE ? LIMIT 5", (f"%{q}%",)):
            suggestions.add(row['author_name'])
        # Categories
        for row in db.execute("SELECT category FROM book_db WHERE category LIKE ? LIMIT 5", (f"%{q}%",)):
            suggestions.add(row['category'])
    return jsonify(list(suggestions))

@app.route('/admin/book_reservations/<int:book_id>')
def admin_book_reservations(book_id):
    if get_user_role() != 'admin':
        return redirect(url_for('user_dashboard'))
    db = get_db()
    reservations = db.execute('''
        SELECT r.*, m.first_name, m.last_name, m.mob_no, m.email_id
        FROM reservations r
        JOIN member_db m ON r.member_id = m.member_id
        WHERE r.book_id = ? AND r.status = 'active'
        ORDER BY r.reserved_date ASC
    ''', (book_id,)).fetchall()
    book = db.execute('SELECT * FROM book_db WHERE book_id = ?', (book_id,)).fetchone()
    return render_template('admin_book_reservations.html', reservations=reservations, book=book)

@app.route('/admin/reservations')
def admin_all_reservations():
    if get_user_role() != 'admin':
        return redirect(url_for('user_dashboard'))
    db = get_db()
    reservations = db.execute('''
        SELECT r.*, b.title, b.author_name, m.first_name, m.last_name, m.mob_no, m.email_id
        FROM reservations r
        JOIN book_db b ON r.book_id = b.book_id
        JOIN member_db m ON r.member_id = m.member_id
        WHERE r.status = 'active'
        ORDER BY r.reserved_date ASC
    ''').fetchall()
    return render_template('admin_all_reservations.html', reservations=reservations)

def get_pending_reservation_count():
    db = get_db()
    row = db.execute("SELECT COUNT(*) as cnt FROM reservations WHERE status = 'active'").fetchone()
    return row['cnt'] if row else 0

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

