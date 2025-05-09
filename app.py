from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import models  # Import our data models
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use SQLite file
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

with app.app_context():
    db.create_all()  # Create the database tables

# Manually add warehouse user if not already in the database
with app.app_context():
    warehouse_username = 'warehouse'
    warehouse_password_hash = generate_password_hash('warehouse_password')
    if not User.query.filter_by(username=warehouse_username).first():
        new_user = User(username=warehouse_username, password=warehouse_password_hash)
        db.session.add(new_user)
    db.session.commit()

def get_user_role(username):
    user = User.query.filter_by(username=username).first()
    if user and username == 'warehouse':
        return 'warehouse'
    elif user:
        return 'shop'
    return None

app.jinja_env.globals.update(get_user_role=get_user_role)

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                return redirect(url_for('login'))
            user_role = get_user_role(session['username'])
            if role and user_role != role:
                return "Unauthorized access.", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            return "Username already taken. Please choose another."

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect(url_for('shop_dashboard'))

    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            role = get_user_role(username)
            if role == 'warehouse':
                return redirect(url_for('warehouse_dashboard'))
            elif role == 'shop':
                return redirect(url_for('shop_dashboard'))
        else:
            return "Invalid credentials."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/users')
def view_users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/warehouse')
@login_required(role='warehouse')
def warehouse_dashboard():
    warehouse_stock = models.load_warehouse_stock()
    return render_template('warehouse_dashboard.html', stock=warehouse_stock)

@app.route('/warehouse/add_product', methods=['POST'])
@login_required(role='warehouse')
def add_product():
    product_name = request.form['product_name']
    initial_quantity = int(request.form.get('initial_quantity', 0))

    warehouse_stock = models.load_warehouse_stock()
    for item in warehouse_stock:
        if item.lower() == product_name.lower():
            return f"Product '{item}' already exists (case-insensitive)."

    models.add_warehouse_product(product_name, initial_quantity)
    return redirect(url_for('warehouse_dashboard'))

@app.route('/warehouse/delete_product', methods=['POST'])
@login_required(role='warehouse')
def delete_product():
    product_name = request.form['product_name']

    warehouse_stock = models.load_warehouse_stock()
    found_product = None
    for item in warehouse_stock:
        if item.lower() == product_name.lower():
            found_product = item
            break

    if found_product:
        models.delete_warehouse_product(found_product)
        return redirect(url_for('warehouse_dashboard'))
    else:
        return f"Product '{product_name}' not found in warehouse."

@app.route('/shop')
@login_required(role='shop')
def shop_dashboard():
    username = session['username']
    shop_id = username
    shop_stock = models.get_shop_stock(shop_id)
    low_stock_items = {
        product: qty for product, qty in shop_stock.items() if qty < models.LOW_STOCK_THRESHOLD
    }
    return render_template('shop_dashboard.html', stock=shop_stock, low_stock=low_stock_items)

@app.route('/shop/request_stock', methods=['POST'])
@login_required(role='shop')
def request_stock():
    username = session['username']
    shop_id = username
    product = request.form['product']
    quantity = int(request.form['quantity'])

    warehouse_stock = models.load_warehouse_stock()
    found_product = None
    for item in warehouse_stock:
        if item.lower() == product.lower():
            found_product = item
            break

    if found_product:
        if warehouse_stock[found_product] >= quantity:
            models.update_warehouse_stock(found_product, -quantity)
            current_shop_stock = models.get_shop_stock(shop_id).get(product, 0)
            models.update_shop_stock(shop_id, product, current_shop_stock + quantity)
            return redirect(url_for('shop_dashboard'))
        else:
            return "Warehouse has insufficient stock."
    else:
        return f"Product '{product}' not found in warehouse."

@app.route('/shop/return_stock', methods=['POST'])
@login_required(role='shop')
def return_stock():
    username = session['username']
    shop_id = username
    product = request.form['product']
    quantity = int(request.form['quantity'])

    current_shop_stock = models.get_shop_stock(shop_id).get(product, 0)
    if current_shop_stock >= quantity:
        models.update_shop_stock(shop_id, product, current_shop_stock - quantity)
        models.update_warehouse_stock(product, quantity)
        return redirect(url_for('shop_dashboard'))
    else:
        return "Insufficient stock to return."

if __name__ == '__main__':
    app.run(debug=True)