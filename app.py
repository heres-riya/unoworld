from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import csv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
MODEL_DIR = os.path.abspath(os.path.dirname(__file__))
# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'postgresql://postgres:postgres@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Association Table for Many-to-Many relationship
enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    instructor = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=False)


# ... (rest of your imports)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    courses = db.relationship('Course', secondary=enrollments, backref='students')

    @property
    def is_admin(self):
        return self.id == 2  # Assuming student with ID 2 is the admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.route('/')
def index():

    student_id = session.get('student_id')
    if student_id:
        student = Student.query.get(student_id)
        if (student):
            return redirect(url_for('main.student_dashboard'))    
    students = None # Student.query.all()
    courses = None # Course.query.all()

    return render_template('index.html', students=students, courses=courses)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
