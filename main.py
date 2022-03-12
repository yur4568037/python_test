import asyncio
import aiohttp
from operator import itemgetter
import os.path
import json
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
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

data1_F = False
data2_F = False
data3_F = False

data1 = []
data2 = []
data3 = []


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), nullable=False)
    access = db.Column(db.Integer, nullable=False)         # 1 - admin, 2 - user
    description = db.Column(db.String(200))
    userpass = db.Column(db.String(20), nullable=False)

    # Format output
    def __repr__(self):
        return '<Users %r>' % self.username


class MyData(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50))

    # Format output
    def __repr__(self):
        return '<MyData %r>' % self.username





# first create users database
if os.path.isfile("users.db") == False:
    db.create_all()
    newuser = Users(id = 0, username = "admin", access = 1, userpass = "admin")
    newdata = MyData(id = 0, name = "No data")

    try:
        db.session.add(newuser)
        db.session.add(newdata)
        db.session.commit()
        print("Tables created")
    except:
        print("Error tables created")

    print("Database created")
else:
    # set last id_global and increment
    sql_users = Users.query.order_by(Users.id).all()
    try:
        id_global = sql_users[-1].id
        id_global += 1
    except:
        id_global = 0
    
    print("Database exist")


# Data point handlers=================================================
@app.route('/database/point1', methods=['GET'])
def data_point1():

    try:
        with open('data_source1.json') as f1:
            data1 = json.load(f1)    
    except:
        return('error')
        
    data1_new = []

    for el in data1:
        if 'id' and 'name' in el:            # check dict
            if type(el.get('id')) == int:    # check id type
                data1_new.append(el)    

    return json.dumps(data1_new)


@app.route('/database/point2', methods=['GET'])
def data_point2():
    
    try:
        with open('data_source2.json') as f2:
            data2 = json.load(f2)    
    except:
        return('error')
        
    data2_new = []

    for el in data2:
        if 'id' and 'name' in el:            # check dict
            if type(el.get('id')) == int:    # check id type
                data2_new.append(el)    

    return json.dumps(data2_new)


@app.route('/database/point3', methods=['GET'])
def data_point3():
    
    try:
        with open('data_source3.json') as f3:
            data3 = json.load(f3)    
    except:
        return('error')
        
    data3_new = []

    for el in data3:
        if 'id' and 'name' in el:            # check dict
            if type(el.get('id')) == int:    # check id type
                data3_new.append(el)    

    return json.dumps(data3_new)


# function for async requests======================================
async def fetch_point(url, id):
    async with aiohttp.ClientSession() as session:
        # debug
        if id == 1:
            await asyncio.sleep(0)
        if id == 2:
            await asyncio.sleep(0)
        if id == 3:
            await asyncio.sleep(0)
        #debug
        
        global data1_F
        global data2_F
        global data3_F
        global data1
        global data2
        global data3

        try:
            async with session.get(url) as response:
                data = await response.read()
                if id == 1 and data != 'error':
                    data1_F = True
                    data1 = json.loads(data)
                if id == 2:
                    data2_F = True
                    data2 = json.loads(data)
                if id == 3:
                    data3_F = True
                    data3 = json.loads(data)
        except:
            if id == 1:
                data1_F = False
            if id == 2:
                data2_F = False
            if id == 3:
                data3_F = False
            print('error http request')


async def fetch_process():
    futures = [asyncio.create_task(fetch_point('http://127.0.0.1:5000/database/point1', 1)), asyncio.create_task(fetch_point('http://127.0.0.1:5000/database/point2', 2)),
    asyncio.create_task(fetch_point('http://127.0.0.1:5000/database/point3', 3))]

    done, pending = await asyncio.wait(futures, timeout=2)

    for future in pending:
        future.cancel()
        print('pending ' + future.get_name())
    
    for future in done:
        print('done ' + future.get_name())


# HTTP handlers==========================================
@app.route('/database', methods=['POST', 'GET'])
def page_database():
    if request.method == "POST":
        
        # start async request JSON (non-async in the beginning)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(fetch_process())
        loop.close()
        
        global data1_F
        global data2_F
        global data3_F
        global data1
        global data2
        global data3

        data_all = []

        if data1_F == True:
            data1_F = False
            data_all += data1
        if data2_F == True:
            data2_F = False
            data_all += data2
        if data3_F == True:
            data3_F = False
            data_all += data3

        sorted_data = sorted(data_all, key=itemgetter('id'))

        sql_database = MyData.query.order_by(MyData.id).all()

        for el in sql_database:
            db.session.delete(el)
        db.session.commit()
        
        for el in sorted_data:
            newdata = MyData(id = el.get('id'), name = el.get('name'))
            try:
                db.session.add(newdata)
                db.session.commit()
            except:
                print("Error db commit")
        
        return redirect('/database')

    else:
        sql_database = MyData.query.order_by(MyData.id).all()
        return render_template("database.html", sql_database=sql_database)


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
