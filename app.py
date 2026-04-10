import os
import sqlite3
import csv
import io
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, Response, flash, session, jsonify

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'students.db'))


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                roll_number TEXT UNIQUE,
                course TEXT,
                enrollment_date TEXT,
                address TEXT
            )
            """
        )
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")


init_db()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please login first')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped_view


@app.route('/')
def login():
    session.clear()
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = username
            return redirect(url_for('dashboard'))

        flash('Invalid username or password')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,)
        ).fetchone()

        if existing_user:
            message = 'Username already exists'
        else:
            conn.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            conn.commit()
            conn.close()
            flash('Registration successful. Please login.')
            return redirect(url_for('login'))

        conn.close()

    return render_template('register.html', message=message)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('dashboard.html', students=students)


@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        roll_number = request.form['roll_number']
        course = request.form['course']
        enrollment_date = request.form['enrollment_date']
        address = request.form['address']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO students (name, email, phone, roll_number, course, enrollment_date, address)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (name, email, phone, roll_number, course, enrollment_date, address)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    return render_template('add_student.html')


@app.route('/update_student/<int:id>', methods=['GET', 'POST'])
@login_required
def update_student(id):
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        roll_number = request.form['roll_number']
        course = request.form['course']
        enrollment_date = request.form['enrollment_date']
        address = request.form['address']

        conn.execute(
            '''UPDATE students SET name=?, email=?, phone=?, roll_number=?, course=?, enrollment_date=?, address=?
               WHERE id=?''',
            (name, email, phone, roll_number, course, enrollment_date, address, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('update_student.html', student=student)


@app.route('/delete_student/<int:id>')
@login_required
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search_student():
    students = []
    if request.method == 'POST':
        search_term = request.form['search_term']
        conn = get_db_connection()
        students = conn.execute(
            "SELECT * FROM students WHERE name LIKE ? OR roll_number LIKE ? OR email LIKE ?",
            (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%')
        ).fetchall()
        conn.close()

    return render_template('search.html', students=students)


@app.route('/analytics')
@login_required
def analytics():
    conn = get_db_connection()
    total_students = conn.execute('SELECT COUNT(*) as total FROM students').fetchone()['total']
    course_data = conn.execute('SELECT course, COUNT(*) as count FROM students GROUP BY course').fetchall()
    enrollment_trends = conn.execute(
        """
        SELECT strftime('%Y-%m', enrollment_date) as month, COUNT(*) as count
        FROM students
        WHERE enrollment_date IS NOT NULL AND enrollment_date != ''
        GROUP BY strftime('%Y-%m', enrollment_date)
        ORDER BY month
        """
    ).fetchall()
    conn.close()

    return render_template(
        'analytics.html',
        total_students=total_students,
        course_data=course_data,
        enrollment_trends=enrollment_trends
    )


@app.route('/export_csv')
@login_required
def export_csv():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students ORDER BY id').fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    if students:
        writer.writerow(students[0].keys())
        for student in students:
            writer.writerow(student)

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=students.csv'}
    )


@app.route('/bulk_import', methods=['GET', 'POST'])
@login_required
def bulk_import():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        if file and file.filename.endswith('.csv'):
            try:
                stream = io.StringIO(file.stream.read().decode('UTF8'), newline=None)
                csv_reader = csv.DictReader(stream)

                conn = get_db_connection()
                cursor = conn.cursor()
                imported_count = 0

                for row in csv_reader:
                    if not any(row.values()):
                        continue
                    cursor.execute(
                        '''INSERT INTO students (name, email, phone, roll_number, course, enrollment_date, address)
                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (
                            row.get('name', ''),
                            row.get('email', ''),
                            row.get('phone', ''),
                            row.get('roll_number', ''),
                            row.get('course', ''),
                            row.get('enrollment_date', ''),
                            row.get('address', '')
                        )
                    )
                    imported_count += 1

                conn.commit()
                conn.close()
                flash(f'Successfully imported {imported_count} students!')
                return redirect(url_for('dashboard'))

            except Exception as e:
                flash(f'Error importing file: {str(e)}')
                return redirect(request.url)

    return render_template('bulk_import.html')


@app.route('/download_sample_csv')
def download_sample_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['name', 'email', 'phone', 'roll_number', 'course', 'enrollment_date', 'address'])
    writer.writerow(['John Doe', 'john@example.com', '9876543210', 'STU001', 'Computer Science', '2024-01-15', '123 Main St'])
    writer.writerow(['Jane Smith', 'jane@example.com', '9876543211', 'STU002', 'Information Technology', '2024-01-16', '456 Oak Ave'])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=sample_students.csv'}
    )


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


# This allows gunicorn to import the app object
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


