import os.path
import json
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import true
from forms import SignInForm, NewUserForm, EditUserForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "12345"

db = SQLAlchemy(app)

# global variables
id_global = 0
access_to_site = False
user_permission = 2

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), nullable=False)
    access = db.Column(db.Integer, nullable=False)         # 1 - admin, 2 - user
    description = db.Column(db.String(200))
    userpass = db.Column(db.String(20), nullable=False)

    # Format output
    def __repr__(self):
        return '<Users %r>' % self.username


# first create database
if os.path.isfile("users.db") == False:
    db.create_all()
    newuser = Users(id = 0, username = "admin", access = 1, userpass = "admin")

    try:
        db.session.add(newuser)
        db.session.commit()
        print("Admin created")
    except:
        print("Error admin created")

    print("Database created")
else:
    # set last id_global and increment
    sql_users = Users.query.order_by(Users.id).all()
    id_global = sql_users[-1].id
    id_global += 1
    print("Database exist")



@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')

    
@app.route('/')
@app.route('/index')
def index():
    global access_to_site
    if access_to_site == False:
        return redirect('/signin')

    return render_template("index.html")


@app.route('/user', methods=['GET'])    # POST request via AJAX
def user():
    global access_to_site
    if access_to_site == False:
        return redirect('/signin')
    
    sql_users = Users.query.order_by(Users.id).all()
    formnewuser = NewUserForm()
    return render_template("user.html", sql_users=sql_users, user_permission=user_permission, formnewuser=formnewuser)


@app.route('/user/<int:id>/delete')
def user_delete(id):
    if access_to_site == False:
        return redirect('/signin')

    #permission control
    if user_permission != 1:
        return redirect('/user')

    user = Users.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        return redirect('/user')
    except:
        return "Error detele user"


# update user via form
@app.route('/user/<int:id>/update', methods=['POST', 'GET'])
def user_update(id):
    if access_to_site == False:
        return redirect('/signin')

    #permission control
    if user_permission != 1:
        return redirect('/user')

    user = Users.query.get_or_404(id)

    # empty password protect
    if(len(request.form['password'])  > 0):
        user.userpass = request.form['password']

    if id == 0:      # admin password update 
        user.username = "admin"    
        user.access = 1
    else:
        user.username = request.form['username']    
        user.access = request.form['access']
        user.description = request.form['description']

    try:
        db.session.commit()
        return redirect('/user')
    except:
        return "Error update user"


@app.route('/signin', methods=['GET'])
def signin():
    # two SignInForm() for SignIn and Registration
    form1 = SignInForm()
    form2 = SignInForm()

    return render_template("signin.html", form1 = form1, form2 = form2)


@app.route('/signout', methods=['GET'])
def signout():
    global access_to_site
    access_to_site = False

    global user_permission
    user_permission = 2
    return redirect('/signin')


# user registration via AJAX; redirect via JS
@app.route('/send_registration', methods=['POST'])
def send_registration():
    form = SignInForm()
    if request.method == "POST":
        if form.validate_on_submit():

            read_username = request.form['username']
            read_password = request.form['password']

            sql_users = Users.query.order_by(Users.id).all()

            for element in sql_users:
                if read_username == element.username:
                    return json.dumps({'success': 'false', 'msg': 'User with this name exists'})    
            else:
                global id_global
                new_id = id_global
                id_global += 1

                # access level for new user always 2
                newuser = Users(id = new_id, username = read_username, access = 2, userpass = read_password)

                global access_to_site
                access_to_site = True

                try:
                    db.session.add(newuser)
                    db.session.commit()
                    # return redirect('/index')
                    return json.dumps({'success': 'true', 'msg': ' '})
                except:
                    return json.dumps({'success': 'false', 'msg': 'Server error'})

        else:
            #  error handler
            return json.dumps({'success': 'false', 'msg': 'Server error'})


# admin create new user via AJAX
@app.route('/send_newuser', methods=['POST'])
def send_newuser():
    global access_to_site, user_permission

    if access_to_site == False:
        return json.dumps({'success': 'false', 'msg': 'access error'})

    # permission control
    if user_permission != 1:
        return json.dumps({'success': 'false', 'msg': 'permission error'})

    form = NewUserForm()
    if request.method == "POST":
        if form.validate_on_submit():

            read_username = request.form['username']
            read_password = request.form['password']
            read_access = int(request.form['access'])
            read_description = request.form['description']

            if read_access > 2 or read_access < 1:     # read access protect
                read_access = 2

            for element in sql_users:
                if read_username == element.username:
                    return json.dumps({'success': 'false', 'msg': 'User with this name exists'})    
            else:
                global id_global
                new_id = id_global
                id_global += 1

                newuser = Users(id = new_id, username = read_username, access = read_access, description = read_description, userpass = read_password)

                try:
                    db.session.add(newuser)
                    db.session.commit()
                    #return redirect('/index')
                    return json.dumps({'success': 'true', 'msg': ' '})
                except:
                    return json.dumps({'success': 'false', 'msg': 'Server error'})

        else:
            #  error handler
            print (form.errors)
            return json.dumps({'success': 'false', 'msg': 'Validation error'})


# user sign in via AJAX; redirect via JS
@app.route('/send_signin', methods=['POST'])
def send_signin():
    form = SignInForm()
    if request.method == "POST":
        if form.validate_on_submit():
            read_username = request.form['username']
            read_password = request.form['password']      

            sql_users = Users.query.order_by(Users.id).all()

            for element in sql_users:
                if (read_username == element.username 
                and read_password == element.userpass):
                    global access_to_site
                    access_to_site = True

                    # set permission
                    global user_permission
                    if element.access == 1:
                        user_permission = 1
                    else:
                        user_permission = 2
                    
                    #break
                    return json.dumps({'success': 'true', 'msg': ' '})
            else:
                return json.dumps({'success': 'false', 'msg': 'Data is incorrect'})

        else:
            #  error handler
            return json.dumps({'success': 'false', 'msg': 'Server error'})
    


if __name__ == "__main__":
    app.run(debug=True)
