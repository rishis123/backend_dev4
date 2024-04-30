from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()


# your classes here
"""
Association table between the instructors and courses, connected via id primary_key
"""
instructor_association_table = db.Table(
    "instructor_association", 
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),  # user_id column references id in User table
    db.Column("course_id", db.Integer, db.ForeignKey("course.id"), primary_key=True)  # course_id column references id in Course table
)
"""
Association table between the students and courses, connected via id primary_key
"""
student_association_table = db.Table(
    "student_association", 
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("course.id"), primary_key=True)
)


"""
User class, making the table for all user values in the database
"""

class User(db.Model):    
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    instructed_courses = db.relationship('Course', secondary=instructor_association_table, back_populates='instructors')
    #Contains all the courses that this user teaches. 
    enrolled_courses = db.relationship('Course', secondary=student_association_table, back_populates='students')
    #backpopulate to connect the students list in Course and courses in User

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "courses": [course.serialize_without_rec() for course in self.instructed_courses] + \
          [course.serialize_without_rec() for course in self.enrolled_courses]
# Note: we only want to yield one single courses field in serialization, so we combine both courses' lists
        }
    
    """
    Yields students/instructors' information without enrolled courses, to avoid mutually recursive definition 
    """
    def serialize_without_courses(self):
            return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid
        }

   
    
"""
Course class, making the table for all course values in the database
"""
class Course(db.Model):
    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True)    
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    instructors = db.relationship('User',secondary=instructor_association_table, back_populates = 'instructed_courses')
    students = db.relationship('User', secondary=student_association_table, back_populates = 'enrolled_courses')


    assignments = db.relationship('Assignment', cascade="delete")
    #Many-to-one relationship -- association table with Assignment class

    """
    Standard serialization function, includes instructors, students, and assignments
    """
    def serialize(self):
            return {
                "id": self.id,
                "code": self.code,
                "name": self.name,     
                "instructors": [user.serialize_without_courses() for user in self.instructors],
                "students": [user.serialize_without_courses() for user in self.students],
                "assignments": [assignment.serialize_without_courses() for assignment in self.assignments]
                }
    
    """
    Yields enrolled course information without assignments, instructors, or students, to avoid mutually recursive definition 
    """
    def serialize_without_rec(self):
            return {
            "id": self.id,
            "code": self.code,
            "name": self.name
        }

"""
Assignment class, making the table for all Assignment values in the database
"""
class Assignment(db.Model):
    __tablename__ = "assignment"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

    """
    Yields standard serialization of assignments, including courses
    """
    def serialize(self):
        course_val = Course.query.get(self.course_id)
        return {
                "id": self.id,
                "title": self.title,
                "due_date": self.due_date,     
                "course": [course_val.serialize_without_rec()]
                }

    """
    Yields assignment information without courses', to avoid repetition
    """
    def serialize_without_courses(self):
            return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date
        }