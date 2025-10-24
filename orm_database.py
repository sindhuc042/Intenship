from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# --- 1. Flask App Initialization ---
# This part is the same as before.
app = Flask(__name__)

# --- 2. Database Configuration ---
# Configure the database URI for PostgreSQL.
# Replace 'your_password', 'your_user', 'your_host', and 'your_db' accordingly.
# Example: 'postgresql://postgres:mysecretpassword@localhost/roster_db'
# your_password = "Ashwin@1999"
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:sindhu@123@localhost/roster_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Optional: Reduces overhead

# --- 3. Database Initialization ---
# Create the SQLAlchemy database object.
db = SQLAlchemy(app)


# --- 4. Define the Model ---
# This class represents the 'students' table in our database.
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    # The __repr__ method gives a developer-friendly representation of the object.
    def __repr__(self):
        return f'<Student {self.first_name}>'


# --- 5. THE FIX: Use app.app_context() ---
# This block is the solution to the "Working outside of application context" error.
# We manually create the context so that Flask-SQLAlchemy knows which app to use.
def initialize_database():
    """
    Creates all database tables and adds an initial student.
    This function should be run once to set up the database.
    """
    with app.app_context():
        print("Application context pushed.")
        
        # This command creates the 'student' table based on the model definition above.
        # It will not re-create tables that already exist.
        print("Creating database tables...")
        db.create_all()
        print("Tables created.")

        # Let's add a new student to demonstrate the session.
        # We check if a student already exists to avoid errors on subsequent runs.
        if not Student.query.filter_by(email='charlie@example.com').first():
            print("Adding a new student...")
            new_student = Student(first_name='Charlie', email='charlie@example.com')
            
            # The 'session' is like a staging area for your database changes.
            db.session.add(new_student)
            
            # The 'commit' command saves all changes in the session to the database.
            db.session.commit()
            print("New student 'Charlie' added.")
        else:
            print("Student 'Charlie' already exists.")
            
        # Let's query and print all students to verify.
        all_students = Student.query.all()
        print("\nCurrent students in database:")
        for student in all_students:
            print(f"- ID: {student.id}, Name: {student.first_name}, Email: {student.email}")
        
        print("\nDatabase initialization complete.")

# --- Running the script ---
if __name__ == '__main__':
    # When you run this Python file directly, the following function will execute.
    initialize_database()

# You can still define routes for a web application below this.
# The context is automatically handled inside routes.
@app.route('/')
def index():
    # No need for `with app.app_context():` here!
    students = Student.query.all()
    student_list = "".join([f"<li>{s.first_name}</li>" for s in students])
    return f"<h1>Student List</h1><ul>{student_list}</ul>"
