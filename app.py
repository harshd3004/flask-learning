from flask import Flask,render_template
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', now=datetime.now())

@app.route('/about')
def about():
    return render_template('about.html', now=datetime.now())

@app.route('/user/<uname>')
def greetUser(uname):
    return render_template('greet_user.html',username=uname, now=datetime.now())

if __name__ == '__main__':
    app.run(debug=True)