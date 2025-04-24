
#============================
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, Flask!'


app = Flask(__name__)

# In-memory database for demonstration (replace with a database in a real-world application)
users = {}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username in users and check_password_hash(users[username]['password'], password):
        # Successful login, redirect to home page
        return redirect(url_for('home'))
    else:
        # Failed login
        return 'Invalid username or password. Please try again.'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if username in users:
            return 'Username already exists. Please choose a different one.'

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Store user data in the database
        users[username] = {'password': hashed_password, 'email': email}

        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/home')
def home():
    return redirect(url_for('static', filename='html/index.html'))

if __name__ == '__main__':
    app.run(debug=True)
