from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, make_response
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from wtforms import Form ,StringField, TextAreaField, PasswordField, validators
from wtforms.fields import TextField
from wtforms_components import Email
from passlib.hash import sha256_crypt
from functools import wraps
import datetime, time
import os


mysql = MySQL(cursorclass=DictCursor)
app = Flask(__name__)
app.secret_key= os.urandom(24)

#config MySQL
app.config['MYSQL_DATABASE_HOST']= 'localhost'
app.config['MYSQL_DATABASE_USER']= 'root'
app.config['MYSQL_DATABASE_PASSWORD']= ''
app.config['MYSQL_DATABASE_DB']= 'school'


#init MySQL
mysql.init_app(app)


#### Algemene routes ####
@app.route('/')
def index():
    resp = make_response(render_template('home.html'))
    expire_date = datetime.datetime.now()
    expire_date = expire_date + datetime.timedelta(days=30)
    resp.set_cookie('welcome', 'Welkom terug', expires=expire_date)		
    return resp

@app.route('/about')
def about():
    return render_template('about.html')

#### Richtingen ####

@app.route('/richtingen')
def richtingen():
    #create cursor
    cur = mysql.get_db().cursor()

    #get richtingen
    result = cur.execute("SELECT * FROM richtingen")

    richtingen = cur.fetchall()

    if result > 0:
        return render_template('richtingen.html', richtingen=richtingen)
    else:
        msg = "No subjects found"
        return render_template('richtingen.html', msg=msg)

    cur.close()

@app.route('/richting/<string:id>/')
def richting(id):
    #create cursor
    cur = mysql.get_db().cursor()

    #get richtingen
    result = cur.execute("SELECT * FROM richtingen WHERE id = %s",[id])

    richting = cur.fetchone()

    return render_template('richting.html', richting=richting)

#### leraren ####

@app.route('/leraren')
def leraren():
    #create cursor
    cur = mysql.get_db().cursor()

    #get leraren
    result = cur.execute("SELECT * FROM leraren")

    leraren = cur.fetchall()

    if result > 0:
        return render_template('leraren.html', leraren=leraren)
    else:
        msg = "No subjects found"
        return render_template('leraren.html', msg=msg)
    
    cur.close()

@app.route('/leraar/<string:id>/')
def leraar(id):
    #create cursor
    cur = mysql.get_db().cursor()

    #get leraren
    result = cur.execute("SELECT * FROM leraren WHERE id = %s",[id])

    leraar = cur.fetchone()

    return render_template('leraar.html', leraar=leraar)


#### klassen ####
@app.route('/klassen')
def klassen():
    #create cursor
    cur = mysql.get_db().cursor()

    #get klassen
    result = cur.execute("SELECT * FROM klassen")

    klassen = cur.fetchall()

    if result > 0:
        return render_template('klassen.html', klassen=klassen)
    else:
        msg = "No subjects found"
        return render_template('klassen.html', msg=msg)
    
    cur.close()

@app.route('/klas/<string:id>/')
def klas(id):
    #create cursor
    cur = mysql.get_db().cursor()

    #get klas
    result = cur.execute("SELECT * FROM klassen WHERE id = %s",[id])

    klas = cur.fetchone()

    return render_template('klas.html', klas=klas)


#### register ####

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4,max=25)])
    email = StringField('Email', [validators.Length(min=6,max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #create cursor
        cur = mysql.get_db().cursor()

        #Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",(name,email,username,password))

        #commit to db
        mysql.get_db().commit()

        #close connection
        cur.close()

        flash('You are now registered and can log in', 'success')
        
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#### login ####
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        
        # get form fields
        username = request.form['username']
        password_canidate = request.form['password']

        #create cursor
        cur = mysql.get_db().cursor()

        #get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        
        #check result
        if result > 0:
            #get stored hash
            data = cur.fetchone()
            password = data['password']
            

            #compare passwords
            if sha256_crypt.verify(password_canidate, password):
                #when all is correct
                session['logged_in'] = True
                session['username'] = username

                flash('You are now loggend in','success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid password'
                return render_template('login.html', error=error)
            
            #close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

#check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

#### logout ####
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

#### dashboard ####

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

@app.route('/dashboardRichtingen')
@is_logged_in
def dashboardRichtingen():
    #create cursor
    cur = mysql.get_db().cursor()

    #get richtingen
    result = cur.execute("SELECT * FROM richtingen")

    richtingen = cur.fetchall()

    if result > 0:
        return render_template('dashboardRichtingen.html', richtingen=richtingen)
    else:
        msg = "No subjects found"
        return render_template('dashboardRichtingen.html', msg=msg)

    cur.close()

#### richtingen ####

class RichtingForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=100)])
    body = TextAreaField('Body', [validators.Length(min=30)])

@app.route('/add_richting', methods=['GET','POST'])
@is_logged_in
def add_richting():
    form = RichtingForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        #create cursor
        cur = mysql.get_db().cursor()

        #execute
        cur.execute("INSERT INTO richtingen(title,body,author) VALUES(%s,%s,%s)",(title,body,session['username']))

        #commit to db
        mysql.get_db().commit()

        cur.close()

        flash('Subject Created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_richting.html', form=form)

#### edit richting ####
@app.route('/edit_richting/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_richting(id):

    cur = mysql.get_db().cursor()

    #get user by id
    result = cur.execute("SELECT * FROM richtingen WHERE id =%s", [id])

    richting = cur. fetchone()

    form = RichtingForm(request.form)

    #populate fields
    form.title.data = richting['title']
    form.body.data = richting['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        #create cursor
        cur = mysql.get_db().cursor()

        #execute
        cur.execute("UPDATE richtingen SET title=%s, body=%s WHERE id=%s", (title,body,id))

        #commit to db
        mysql.get_db().commit()

        cur.close()

        flash('subject successfully Updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_richting.html', form=form)

#### delete richting ####
@app.route('/delete_richting/<string:id>', methods=['POST'])
@is_logged_in
def delete_richting(id):

    cur = mysql.get_db().cursor()

    cur.execute("DELETE FROM richtingen WHERE id=%s", [id])

    mysql.get_db().commit()

    cur.close()
    flash('Subject Deleted', 'success')

    return redirect(url_for('dashboard'))


####leraren####

@app.route('/dashboardLeraren')
@is_logged_in
def dashboardLeraren():
    #create cursor
    cur = mysql.get_db().cursor()

    #get leraren
    result = cur.execute("SELECT * FROM leraren")

    leraren = cur.fetchall()

    if result > 0:
        return render_template('dashboardLeraren.html', leraren=leraren)
    else:
        msg = "No subjects found"
        return render_template('dashboardLeraren.html', msg=msg)

    cur.close()

class LeraarForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=100)])
    prename = StringField('Prename', [validators.Length(min=1, max=150)])
    foto = TextAreaField('Foto', [validators.Length(min=30)])
    email = TextField(validators=[Email()])

@app.route('/add_leraar', methods=['GET','POST'])
@is_logged_in
def add_leraar():
    form = LeraarForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        prename = form.prename.data
        foto = form.foto.data
        email = form.email.data
        
        #create cursor
        cur = mysql.get_db().cursor()

        #execute
        cur.execute("INSERT INTO leraren(name,prename,foto,email) VALUES(%s,%s,%s,%s)",(name,prename,foto,email))

        #commit to db
        mysql.get_db().commit()

        cur.close()

        flash('Leraar Created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_leraar.html', form=form)

#### edit leraar ####
@app.route('/edit_leraar/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_leraar(id):

    cur = mysql.get_db().cursor()

    #get leraar by id
    result = cur.execute("SELECT * FROM leraren WHERE id =%s", [id])

    leraar = cur. fetchone()

    form = LeraarForm(request.form)

    #populate fields
    form.name.data = leraar['name']
    form.prename.data = leraar['prename']
    form.foto.data = leraar['foto']
    form.email.data = leraar['email']
    

    if request.method == 'POST' and form.validate():
        name = request.form['name']
        prename = request.form['prename']
        foto = request.form['foto']
        email = request.form['email']

        #create cursor
        cur = mysql.get_db().cursor()

        #execute
        cur.execute("UPDATE leraren SET name=%s, prename=%s, foto=%s, email=%s WHERE id=%s", (name,prename,foto,email,id))

        #commit to db
        mysql.get_db().commit()

        cur.close()

        flash('Leraar successfully Updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_leraar.html', form=form)

#### delete leraar ####
@app.route('/delete_leraar/<string:id>', methods=['POST'])
@is_logged_in
def delete_leraar(id):

    cur = mysql.get_db().cursor()

    cur.execute("DELETE FROM leraren WHERE id=%s", [id])

    mysql.get_db().commit()

    cur.close()
    flash('Leraar Deleted', 'success')

    return redirect(url_for('dashboard'))

#### klassen dashboard 

@app.route('/dashboardKlassen')
@is_logged_in
def dashboardKlassen():
    #create cursor
    cur = mysql.get_db().cursor()

    #get klassen
    result = cur.execute("SELECT * FROM klassen")

    klassen = cur.fetchall()

    if result > 0:
        return render_template('dashboardKlassen.html', klassen=klassen)
    else:
        msg = "No subjects found"
        return render_template('dashboardKlassen.html', msg=msg)

    cur.close()

class KlasForm(Form):
    name = StringField('Name', [validators.Length(min=3, max=100)])
    richting = StringField('richting', [validators.Length(min=3, max=100)])
    leraar = StringField('leraar', [validators.Length(min=3, max=100)])
    numerieke_code = StringField('numerieke_code', [validators.Length(max=100)])
    

@app.route('/add_klas', methods=['GET','POST'])
@is_logged_in
def add_klas():
    form = KlasForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        richting = form.richting.data
        leraar = form.leraar.data
        numerieke_code = form.numerieke_code.data
        
        #create cursor
        cur = mysql.get_db().cursor()

        #execute
        cur.execute("INSERT INTO klassen(name,richting,leraar,numerieke_code) VALUES(%s,%s,%s,%s)",(name,richting,leraar,numerieke_code))

        #commit to db
        mysql.get_db().commit()

        cur.close()

        flash('Klas Created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_klas.html', form=form)

#### edit klas ####
@app.route('/edit_klas/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_klas(id):

    cur = mysql.get_db().cursor()

    #get klas by id
    result = cur.execute("SELECT * FROM klassen WHERE id =%s", [id])

    klas = cur. fetchone()

    form = KlasForm(request.form)

    #populate fields
    form.name.data = klas['name']
    form.richting.data = klas['richting']
    form.leraar.data = klas['leraar']
    form.numerieke_code.data = klas['numerieke_code']


    

    if request.method == 'POST' and form.validate():
        name = request.form['name']
        richting = request.form['richting']
        leraar = request.form['leraar']
        numerieke_code = request.form['numerieke_code']
     

        #create cursor
        cur = mysql.get_db().cursor()

        #execute
        cur.execute("UPDATE klassen SET name=%s, richting=%s, leraar=%s, numerieke_code=%s WHERE id=%s", (name,richting,leraar,numerieke_code,id))

        #commit to db
        mysql.get_db().commit()

        cur.close()

        flash('Klas successfully Updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_klas.html', form=form)

#### delete klas ####
@app.route('/delete_klas/<string:id>', methods=['POST'])
@is_logged_in
def delete_klas(id):

    cur = mysql.get_db().cursor()

    cur.execute("DELETE FROM klassen WHERE id=%s", [id])

    mysql.get_db().commit()

    cur.close()
    flash('Klas Deleted', 'success')

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)