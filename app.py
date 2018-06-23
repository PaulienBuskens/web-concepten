from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Classes
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from wtforms import Form ,StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


mysql = MySQL(cursorclass=DictCursor)
app = Flask(__name__)

#config MySQL
app.config['MYSQL_DATABASE_HOST']= 'localhost'
app.config['MYSQL_DATABASE_USER']= 'root'
app.config['MYSQL_DATABASE_PASSWORD']= ''
app.config['MYSQL_DATABASE_DB']= 'school'


#init MySQL
mysql.init_app(app)

Classes = Classes()

#### Algemene routes ####
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/classes')
def classes():
    return render_template('classes.html', classes = Classes)

@app.route('/class/<string:id>/')
def clas(id):
    return render_template('class.html', id=id)

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
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

#### dashboard ####

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)