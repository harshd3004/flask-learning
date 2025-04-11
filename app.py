from flask import Flask,render_template,request,redirect,url_for,flash
from datetime import datetime

app = Flask(__name__)

# This makes 'now' available in all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html', now=datetime.now())

@app.route('/user/<uname>')
def greetUser(uname):
    return render_template('greet_user.html',username=uname, now=datetime.now())

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        passwd = request.form['password']

        #store the user in database (to be done later)

        print(f"New User: {username}, Email: {email}")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    return ""

@app.route('/contactform',methods=['GET','POST'])
def contactForm():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        #Validation to be added
        
        print(f'Contact form submitted by {name}')

    return render_template('contact_form.html')

if __name__ == '__main__':
    app.run(debug=True)