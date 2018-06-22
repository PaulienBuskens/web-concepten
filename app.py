from flask import Flask, render_template
from data import Classes

app = Flask(__name__)

Classes = Classes()

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

if __name__ == '__main__':
    app.run(debug=True)