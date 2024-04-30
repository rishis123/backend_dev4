import json
from flask import Flask, request
from db import db, Course, User, Assignment 
from flask_sqlalchemy import SQLAlchemy
# association tables not needed, abstracted away


app = Flask(__name__)
db_filename = "backup.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


# your routes here
# generalized response formats
"""
Modified success and failure responses per previous hw assignments
"""
def success_response(body, code=200):
    return json.dumps(body), code

def failure_response(message, code=404):
    return json.dumps({'error': message}), code


"""
Route to create the course. Returns error code 400 if no code or name provided in 
request body, otherwise makes the new Course, commits it to the database, and
returns a 201 success code along with the serialization.
"""
@app.route("/api/courses/", methods=["POST"])
def create_course():
    body = json.loads(request.data)
    code = body['code']
    if code is None:
        return failure_response("No code provided", 400)
    name = body['name']
    if name is None:
        return failure_response("No name provided", 400)
    
    new_course = Course(code=code, name=name) #create new Course object with given code and name
    db.session.add(new_course) #add object to sqlAlchemy session and commit to database. This is effectively one row in courses table
    db.session.commit()
    return success_response(new_course.serialize(), 201)

"""
Route to create a user. Returns error code 400 if no netid or name provided in 
request body, otherwise makes the new User, commits it to the database, and
returns a 201 success code along with the serialization.
"""
@app.route("/api/users/", methods=["POST"])
def create_user():
    body = json.loads(request.data)
    name = body['name']
    if name is None:
        return failure_response("No name provided", 400)
    netid = body['netid']
    if netid is None:
        return failure_response("No netid provided", 400)
    
    new_user = User(name=name, netid=netid) #create new User object with given name and neitd
    db.session.add(new_user) #add object to sqlAlchemy session and commit to database. This is effectively one row in Users table
    db.session.commit()
    return success_response(new_user.serialize(), 201)


"""
Returns a serialization of every course in the Course table
"""
@app.route("/api/courses/")
def get_courses():
    courses = [c.serialize() for c in Course.query.all()] 
    return success_response(courses)

"""
Returns a serialization of the course with id [course_id] if it exists, otherwise returns 404 Course not found error
"""
@app.route("/api/courses/<int:course_id>/")
def get_specific_course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!", 400)
    return success_response(course.serialize())

"""
Removes course from the existing database session (i.e., current instance), and yields the serialized version of the course.
 If course is not found, then yields 404 Course not found error
"""
@app.route("/api/courses/<int:course_id>/", methods=["DELETE"])
def delete_course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")
    serialized_course = course.serialize()
    db.session.delete(course)  #deletes course from existing session
    db.session.commit() #permanently changes database from session
    return success_response(serialized_course)

"""
Adds assignments to a specific course with id [course_id] (404 Not Found error if not in Course table), and returns the serialized
assignment with its course field reflecting [course_id] and 201 Success response.
"""
@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def create_assignment(course_id):
    course = Course.query.filter_by(id=course_id).first() #don't want whole collection of values, just first course to have that value
    if course is None:
        return failure_response("Course not found!")

    body = json.loads(request.data) #should contain title of Assignment and due date
    title = body["title"]
    if title is None:
        return failure_response("Title not found", 400)
    due_date = body["due_date"]
    if due_date is None:
        return failure_response("Due date not found", 400)
    
    new_assignment = Assignment(title=title, due_date = due_date, course_id = course_id) #course field initialized with the course_id

    db.session.add(new_assignment)

    db.session.commit()

    return success_response(new_assignment.serialize(), 201)


"""
Yields the serialization of the user in User table with id [user_id], otherwise a 
404 failure response if the user doesn't exist.
"""
@app.route("/api/users/<int:user_id>/", methods=["GET"])
def get_specific_user(user_id):
    # Query the database to get the user by their ID
    user = User.query.get(user_id)

    # If the user does not exist, return a 404 error response
    if not user:
        return failure_response("User not found")

    # Serialize the user data
    serialized_user = user.serialize()

    # Return the serialized user data with the associated courses
    return success_response(serialized_user)


"""
Adds user with id [user_id] provided in request body to the course [course_id].
400 error if invalid or nonexistent [type_val] (must either be "student" or "instructor") or [user_id].
Accordingly updating the course's instructors/assignemnts, the output is a 200 status code along with the updated, serialized course.
"""
@app.route("/api/courses/<int:course_id>/add/", methods = ["POST"])
def add_user_to_course(course_id):
    body = json.loads(request.data)

    course = Course.query.get(course_id)#don't want whole collection of values, just first course to have that value
    if course is None:
        return failure_response("Course not found!")

    type_val = body["type"]
    user_id = body["user_id"]
    if type_val is None:
        return failure_response("No type!", 400)
    elif type_val != "student" and type_val != "instructor":
        return failure_response("Invalid user type!", 400)  
    elif user_id is None:
        return failure_response("No user id provided!", 400) 
    
    #check if the respective values exist
    user = User.query.get(user_id)

    if user is None:
        return failure_response("No such user exists", 400) 
        

    if type_val == "student":
        course.students.append(user) # if user is student, appends to Courses' students list
    else: #type_val is instructor
        course.instructors.append(user) 

    #Note: These changes are bidirectional -- changing the course lists will change this user's course list.
    db.session.commit()

    updated_course = course.serialize() #return in json form

    return success_response(updated_course) #returns updated course 

"""
Resets tables to empty value for graders' postman evaluation.
"""
@app.route("/api/reset/", methods=["POST"])
def reset_tables():
    db.drop_all()  # Drops all existing tables
    db.create_all()  # Recreates tables based on your defined models
    return "Tables reset successfully", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
