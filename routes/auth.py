# routes/auth.py
from flask import Blueprint, render_template, request, redirect, session, url_for

# Define the auth_blueprint
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        session['role'] = role
        if role == 'shop':
            return redirect(url_for('shop.dashboard'))
        elif role == 'warehouse':
            return redirect(url_for('warehouse.dashboard'))
    return render_template('login.html')

@auth_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
