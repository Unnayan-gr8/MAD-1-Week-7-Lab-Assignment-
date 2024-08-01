from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

#------------------------------------DATABASE MANAGEMENT---------------------------------------------------------------------

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///week7_database.sqlite3"

db = SQLAlchemy(app)

app.app_context().push()

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    roll_number = db.Column(db.String(), unique = True, nullable = False)
    first_name = db.Column(db.String(), nullable = False)
    last_name = db.Column(db.String())
    courses = db.relationship("Course", backref = "studiesby", secondary = "enrollments")

class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    course_code = db.Column(db.String(), unique = True, nullable = False)
    course_name = db.Column(db.String(), nullable = False)
    course_description = db.Column(db.String())

class Enrollments(db.Model):
    enrollment_id = db.Column(db.Integer, primary_key = True, autoincrement= True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable = False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable = False)

#-----------------------------------Routes-------------------------------------------------------------------------------------

@app.route('/')
def home():
    students = Student.query.all()
    return render_template("index.html", students = students)

@app.route('/student/create', methods = ['GET', 'POST'])
def studentcreate():
    if request.method == "POST":
        roll = request.form.get("roll")
        A = db.session.query(Student).filter(Student.roll_number == roll).first()
        if(A):
            return render_template("exist.html")
        else:
            f_name = request.form.get("f_name")
            l_name = request.form.get("l_name")
            new_student = Student(roll_number = roll, first_name = f_name, last_name = l_name)
            db.session.add(new_student)
            db.session.commit()
            return redirect('/')
    return render_template("create.html")

@app.route('/student/<int:student_id>/update', methods = ["GET", "POST"])
def update(student_id):
    stud = Student.query.get(student_id)
    cou = Course.query.all()
    if request.method == "POST":
        fname = request.form.get("f_name")
        lname = request.form.get("l_name")
        course = request.form.get("course")
        stud.first_name = fname
        stud.last_name= lname
        db.session.commit()
        enroll = Enrollments(estudent_id = stud.student_id, ecourse_id = course)
        db.session.add(enroll)
        db.session.commit()
        return redirect('/')
    return render_template("update.html", stud = stud, cou = cou)

@app.route('/student/<int:student_id>/delete')
def delete(student_id):
    stud = db.session.query(Student).filter(Student.student_id == student_id).first()
    db.session.delete(stud)
    db.session.commit()
    enroll = db.session.query(Enrollments).filter(Enrollments.estudent_id == student_id).first()
    while(enroll):
        db.session.delete(enroll)
        db.session.commit()
        enroll = db.session.query(Enrollments).filter(Enrollments.estudent_id == student_id).first()
    return redirect('/')

@app.route('/student/<int:student_id>')
def student(student_id):
    student = db.session.query(Student).filter(Student.student_id == student_id).first()
    courses = student.courses
    return render_template("enroll.html", student = student, courses = courses)

@app.route('/student/<int:student_id>/withdraw/<int:course_id>')
def withdraw(student_id, course_id):
    stud = Student.query.get(student_id)
    cou = Course.query.get(course_id)
    enroll = db.session.query(Enrollments).filter(Enrollments.estudent_id == stud.student_id, Enrollments.ecourse_id == cou.course_id).first()
    db.session.delete(enroll)
    db.session.commit()
    return redirect('/')

@app.route('/courses')
def courses():
    courses = Course.query.all()
    return render_template("courses.html", courses = courses)

@app.route('/course/create', methods = ["GET", "POST"])
def ccreate():
    if request.method == "POST":
        code = request.form.get("code")
        A = db.session.query(Course).filter(Course.course_code == code).first()
        if(A):
            return render_template("cexist.html")
        else:
            name = request.form.get("c_name")
            desc = request.form.get("desc")
            new_course = Course(course_code = code, course_name = name, course_description = desc)
            db.session.add(new_course)
            db.session.commit()
            return redirect('/courses')
    return render_template("ccreate.html")

@app.route('/course/<int:course_id>/update', methods = ["GET", "POST"])
def cupdate(course_id):
    cou = Course.query.get(course_id)
    if request.method == "POST":
        name = request.form.get("c_name")
        desc = request.form.get("desc")
        cou.course_name = name
        cou.course_description = desc
        db.session.commit()
        return redirect('/courses')
    return render_template("cupdate.html", cou = cou)

@app.route('/course/<int:course_id>/delete')
def cdelete(course_id):
    cou = Course.query.get(course_id)
    db.session.delete(cou)
    db.session.commit()
    enroll = db.session.query(Enrollments).filter(Enrollments.ecourse_id == course_id).first()
    while(enroll):
        db.session.delete(enroll)
        db.session.commit()
        enroll = db.session.query(Enrollments).filter(Enrollments.ecourse_id == id).first()
    return redirect('/')

@app.route('/course/<int:course_id>')
def course(course_id):
    cou = Course.query.get(course_id)
    students = cou.studiesby
    return render_template("cenroll.html", students = students, cou = cou)

if __name__ == "__main__":
    app.run(debug = True)
