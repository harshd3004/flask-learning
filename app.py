from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return 'This is the about page'

@app.route('/user/<username>')
def greetUser(username):
    return f'Hello {username}'

if __name__ == '__main__':
    app.run(debug=True)