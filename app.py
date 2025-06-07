from flask import Flask,render_template,request,redirect,url_for,flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail,Message
from dotenv import load_dotenv,dotenv_values
from itsdangerous import URLSafeTimedSerializer
from flask_limiter import Limiter

app = Flask(__name__)

load_dotenv() 
env = dotenv_values()

app.secret_key = env.get('SECRET_KEY')

app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = env.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = env.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@gmail.com'

mail = Mail(app)

app.config['SECURITY_PASSWORD_SALT'] = env.get('EMAIL_PASSWORD_SALT')
def generate_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration  # Check expiration
        )
        return email
    except:
        return False

def sendVerificationMail(email):
    token = generate_token(email)
    verification_url = url_for("verify_email", token=token, _external=True)
    msg = Message(
        "Verify Your Email - My Flask app",
        recipients=[email],
        html=render_template(
            "email/verification.html",
            verification_url=verification_url,
            year=datetime.now().year
        )
    )

    msg.body = f"""
                    Please verify your email for Flask app:
                    {verification_url}

                    If you didn't request this, ignore this email.
                """
    
    mail.send(msg)

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
            'is_verified': False,
            'verification_token': 'random_token_here',
            'created_at': datetime.now()
        })
        flash('User Registered Succesfully, PLease verify your email !')
        sendVerificationMail(email)
        flash('Verification email sent! Check your inbox.', 'info')

        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        passwd = request.form['password']
        user = mongo.db.users.find_one({'email': email})

        if not user['is_verified']:
            flash('Account not verified. Check your email.', 'warning')
            return render_template('login.html',email=email)

        if user and check_password_hash(user['password'], passwd):
            return redirect(url_for('home'))
        else:
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

@app.route('/verify/<token>')
def verify_email(token):
    email = confirm_token(token)
    if not email:
        flash('Invalid or expired link', 'danger')
        return redirect(url_for('register'))
     
    user = mongo.db.users.find_one({'email': email})
    if user['is_verified']:
        flash('Account already verified', 'info')
    else:
        mongo.db.users.update_one(
            {'email': email},
            {'$set': {'is_verified': True}}
        )
        flash('Email verified! You can now login.', 'success')
    
    return redirect(url_for('login'))

limiter = Limiter(app)
@app.route('/resend-verification', methods=['POST'])
@limiter.limit("3/hour")
def resend_verification():
    email = request.form.get('email')
    user = mongo.db.users.find_one({'email': email})
    
    if user and not user['is_verified']:
        sendVerificationMail(email)
        flash('New verification email sent', 'success')
    else:
        flash('Email already verified or not found', 'danger')
    
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)