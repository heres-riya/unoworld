from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from google.auth.transport.requests import Request
from google.oauth2 import id_token

import os
from dotenv import load_dotenv
import csv
from datetime import datetime
import requests

load_dotenv()

app = Flask(__name__)
MODEL_DIR = os.path.abspath(os.path.dirname(__file__))
# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'postgresql://postgres:postgres@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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

class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    google_id = db.Column(db.String(256), unique=True, nullable=True)
    courses = db.relationship('Course', secondary=enrollments, backref='students')

    @property
    def is_admin(self):
        return self.id == 2  # Assuming student with ID 2 is the admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))

@app.route('/')
def index():
    student_id = session.get('student_id')
    if student_id:
        student = Student.query.get(student_id)
        if (student):
            return redirect(url_for('student_dashboard'))    
    students = None # Student.query.all()
    courses = None # Course.query.all()

    return render_template('index.html', students=students, courses=courses)



@app.route('/admin')


def admin():
    # Admin view
    student_id = session.get('student_id')
    if not student_id:
        return "Access Denied", 403

    student = Student.query.get(student_id)
    if (not student) or not (student.is_admin):
        return "Access Denied", 403
    
    if not student.is_admin:
        return "Access Denied", 403
        
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('admin.html', students=students, courses=courses)

# --- AUTH ROUTES ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if Student.query.filter_by(email=email).first():
            flash('Email already registered!')
            return redirect(url_for('register'))

        new_student = Student(name=name, email=email)
        new_student.set_password(password)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Login route accessed")
    if request.method == 'POST':
        print("POST request received")
        email = request.form.get('email')
        password = request.form.get('password')
        student = Student.query.filter_by(email=email).first()

        if student and student.check_password(password):
            session['student_id'] = student.id
            session['user_name'] = student.name
            return redirect(url_for('student_dashboard'))
        flash('Invalid credentials')
    print("About to render login.html")
    google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    return render_template('login.html', google_client_id=google_client_id)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/auth/google', methods=['POST'])
def auth_google():
    """Handle Google OAuth token and create/login user"""
    try:
        token = request.json.get('credential')
        
        if not token:
            return {'error': 'No token provided'}, 400
        
        # Get Google's public keys and verify the token
        GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
        
        idinfo = id_token.verify_oauth2_token(token, Request(), GOOGLE_CLIENT_ID)
        
        # Get user info from token
        email = idinfo['email']
        name = idinfo.get('name', email)
        google_id = idinfo['sub']
        
        # Check if user exists
        user = Student.query.filter_by(email=email).first()
        
        if not user:
            # Create new user with Google OAuth
            user = Student(
                name=name,
                email=email,
                google_id=google_id
            )
            db.session.add(user)
            db.session.commit()
        elif not user.google_id:
            # Link Google account to existing user
            user.google_id = google_id
            db.session.commit()
        
        # Log the user in
        session['student_id'] = user.id
        session['user_name'] = user.name
        login_user(user)
        
        return {'success': True, 'redirect': url_for('student_dashboard')}
    
    except ValueError as e:
        # Invalid token
        return {'error': 'Invalid token'}, 401
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    register()
    return redirect(url_for('register'))
    
# --- STUDENT PORTAL ROUTES --- MAIN STUDENT PAGE
@app.route('/dashboard')
def student_dashboard():
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('login'))

    student = Student.query.get(student_id)
    # Get courses the student is NOT already in
    available_courses = Course.query.filter(~Course.students.contains(student)).all()
    courses = Course.query.all()
    return render_template('portal.html', courses=courses, student=student, available_courses=available_courses)

@app.route('/enroll/<int:course_id>')
def enroll_student(course_id):
    student_id = session.get('student_id')
    if not student_id: return redirect(url_for('login'))

    student = Student.query.get(student_id)
    course = Course.query.get(course_id)
    if course not in student.courses:
        student.courses.append(course)
        db.session.commit()
    return redirect(url_for('student_dashboard'))

# --- ADMIN ACTIONS ---
@app.route('/add_course', methods=['POST'])
def add_course():
    name = request.form.get('course_name')
    instructor = request.form.get('instructor')
    db.session.add(Course(course_name=name, instructor=instructor))
    db.session.commit()
    return redirect(url_for('index'))




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
