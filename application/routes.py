from application import app, db, api
from flask import render_template, request, json, Response, redirect, url_for, flash, session, jsonify
from application.models import User, Course, Enrollment
from application.forms import LoginForm, RegisterForm
from flask_restplus import Resource


##########################################################
@api.route('/api', 'api/', methods=['GET'])
class GetAndPost(Resource):
    def get(self):
        return jsonify(User.objects.all())


@api.route('/api/<idx>', methods=['GET'])
class GetUpdateDelete(Resource):
    def get(self, idx):
        return jsonify(User.objects.get(user_id=idx))


##########################################################

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template('index.html', index=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('username'):
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.objects(email=email).first()
        if user and user.get_password(password):
            flash(f'{user.first_name}, You logged in successfully.', 'success')
            session['user_id'] = user.user_id
            session['username'] = user.first_name
            return redirect(url_for('index'))
        else:
            flash("Something went wrong!", "danger")
    return render_template('login.html', title='Login', form=form, login=True)


@app.route('/logout')
def logout():
    session['user_id'] = False
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('username'):
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user_id = User.objects.count() + 1
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User(user_id=user_id, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        flash(f'{user.first_name}, You registered successfully.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', register=True, title='Register', form=form)


@app.route('/courses/')
@app.route('/courses/<term>')
def courses(term=None):
    if term is None:
        term = 'Spring 2019'
    classes = Course.objects.order_by('+courseID')
    return render_template('courses.html', courseData=classes, courses=True, term=term)


@app.route('/enrollment', methods=["GET", "POST"])
def enrollment():
    if not session.get('username'):
        return redirect(url_for('login'))

    courseID = request.form.get('courseID')
    courseTitle = request.form.get('title')
    user_id = session.get('user_id')

    if courseID:
        if Enrollment.objects(user_id=user_id, courseID=courseID):
            flash(f'You are already enrolled in {courseTitle}', 'danger')
            redirect(url_for('courses'))
        else:
            Enrollment(user_id=user_id, courseID=courseID).save()
            flash(f'You are now enrolled in {courseTitle}', 'success')
            redirect(url_for('courses'))

    classes = list(User.objects.aggregate(*[
        {
            '$lookup': {
                'from': 'enrollment',
                'localField': 'user_id',
                'foreignField': 'user_id',
                'as': 'r1'
            }
        }, {
            '$unwind': {
                'path': '$r1',
                'includeArrayIndex': 'r1_id',
                'preserveNullAndEmptyArrays': False
            }
        }, {
            '$lookup': {
                'from': 'course',
                'localField': 'r1.courseID',
                'foreignField': 'courseID',
                'as': 'r2'
            }
        }, {
            '$unwind': {
                'path': '$r2',
                'preserveNullAndEmptyArrays': False
            }
        }, {
            '$match': {
                'user_id': user_id
            }
        }, {
            '$sort': {
                'courseID': 1
            }
        }
    ]))

    term = request.form.get('term')
    return render_template('enrollment.html', enrollment=True, title='Enrollment', classes=classes)


@app.route('/api/')
@app.route('/api/<idx>')
def api(idx=None):
    if idx == None:
        jdata = courseData
    else:
        jdata = courseData[int(idx)]
    return Response(json.dumps(jdata), mimetype='application/json')


@app.route("/user")
def user():
    users = User.objects.all()
    return render_template('user.html', users=users)
