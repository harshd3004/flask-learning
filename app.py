from flask import Flask,render_template,request,redirect,url_for,flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/flaskdb"  
mongo = PyMongo(app)

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

        errors = []

        # Basic validation
        if not username:
            errors.append("Username is required.")
        if not email or '@' not in email:
            errors.append("Valid email is required.")
        if len(passwd) < 6:
            errors.append("Password must be at least 6 characters.")

        
        if mongo.db.users.find_one({'email':email}):
            errors.append("Email already registered.")
        
        if errors:
            return render_template('register.html', errors=errors)

        #store the user in database
        mongo.db.users.insert_one({
            'username': username,
            'email': email,
            'password': generate_password_hash(passwd),  
            'created_at': datetime.now()
        })
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        passwd = request.form['password']
        user = mongo.db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], passwd):
            return redirect(url_for('home'))
        else:
            error = "Invalid credentials!"
            return render_template('login.html',error = "Invalid credentials!")
    return render_template('login.html')

@app.route('/contactform',methods=['GET','POST'])
def contactForm():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        #Validation to be added
        
        #writing to db
        mongo.db.contact_message.insert_one({
            'name':name,
            'email':email,
            'message' : message
        })

    return render_template('contact_form.html')

if __name__ == '__main__':
    app.run(debug=True)