import os
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, url_for, redirect, flash

# --- Database Connection Function ---
# It's a good practice to wrap the connection logic in a function.
# This makes it reusable and easier to manage.
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="roster_db",
            # Replace with your own username and password if needed
            user=os.environ.get('DB_USERNAME', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'sindhu@123')
        )
        return conn
    except psycopg2.OperationalError as e:
        # This error is common if the database isn't running or credentials are wrong.
        print(f"Error connecting to database: {e}")
        return None

# --- Flask App Initialization ---
app = Flask(__name__)
# A secret key is needed for flashing messages
app.config['SECRET_KEY'] = 'your_secret_key_for_production'


# --- READ (List all students) ---
@app.route('/')
def index():
    """Displays all students from the database."""
    conn = get_db_connection()
    if conn is None:
        flash('Database connection could not be established.', 'danger')
        return render_template('index.html', students=[])

    # A cursor allows Python code to execute PostgreSQL command in a database session.
    # The `with` statement ensures the cursor is automatically closed.
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute('SELECT * FROM students ORDER BY id;')
        students = cur.fetchall() # Fetch all rows from the query result

    conn.close()
    return render_template('index.html', students=students)


# --- CREATE (Add a new student) ---
@app.route('/create/', methods=('GET', 'POST'))
def create():
    """Handles the creation of a new student."""
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']

        if not firstname or not lastname or not email:
            flash('All fields are required!', 'danger')
        else:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # !!! IMPORTANT: Use parameterized queries to prevent SQL injection.
                # NEVER use f-strings or string concatenation to build queries.
                cur.execute('INSERT INTO students (firstname, lastname, email) VALUES (%s, %s, %s)',
                            (firstname, lastname, email))
                conn.commit() # Commit the transaction to save changes
            conn.close()
            flash('Student created successfully!', 'success')
            return redirect(url_for('index'))

    return render_template('create.html')


# --- UPDATE (Edit a student's details) ---
@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
def edit(id):
    """Handles editing an existing student."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        # Fetch the student to pre-populate the form
        cur.execute('SELECT * FROM students WHERE id = %s', (id,))
        student = cur.fetchone()

    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']

        if not firstname or not lastname or not email:
            flash('All fields are required!', 'danger')
        else:
            with conn.cursor() as cur:
                # Use a parameterized query for the UPDATE statement
                cur.execute('UPDATE students SET firstname = %s, lastname = %s, email = %s WHERE id = %s',
                            (firstname, lastname, email, id))
                conn.commit()
            conn.close()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('index'))

    # Close connection if it's a GET request
    if request.method == 'GET':
        conn.close()

    return render_template('edit.html', student=student)


# --- DELETE (Remove a student) ---
@app.route('/<int:id>/delete/', methods=('POST',))
def delete(id):
    """Handles the deletion of a student."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        # First, fetch the student's name for the flash message
        cur.execute('SELECT firstname, lastname FROM students WHERE id = %s', (id,))
        student = cur.fetchone()
        
        # Now, delete the student
        cur.execute('DELETE FROM students WHERE id = %s', (id,))
        conn.commit()
    conn.close()
    
    student_name = f"{student['firstname']} {student['lastname']}"
    flash(f'"{student_name}" was successfully deleted!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
