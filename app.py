import os
import re
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session  # Import Flask-Session
from scripts import functions

# Initialize Flask application
app = Flask(__name__, template_folder='template', static_folder='static')

# Global variables
IDLENGTH = 32
DBPATH = 'database/accounts.json'
LOGFILEPATH = 'logs/application.log'

# Configure logging
os.makedirs(os.path.dirname(LOGFILEPATH), exist_ok=True)

logging.basicConfig(
    filename=LOGFILEPATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


app.secret_key = functions.generate_id(IDLENGTH)

# Configure server-side sessions
app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True  

Session(app)  

def check_authorization():
    """
    Check if the current session has a valid MasterPassword.
    """
    if 'MasterPassword' in session:
        return functions.password_check(DBPATH, str(session['MasterPassword']))
    return False

def database_exists(path):
    """
    Check if the database file exists.
    """
    return os.path.exists(path) 

@app.route('/')
def index():
    """
    Render the index page or redirect to login based on authorization status.
    """
    if check_authorization():
        return render_template('vault.html')
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login. If the method is POST, validate the provided password.
    """
    if request.method == 'GET':
        return redirect(url_for('index'))

    password = request.form.get('MasterPassword')
    if functions.password_check(DBPATH, password):
        session['MasterPassword'] = password
        return redirect(url_for('vault'))
    
    return render_template('login.html', error="* Invalid credentials or setup error. Please try again.")

@app.route('/initialize', methods=['GET', 'POST'])
def initialize():
    """
    Initialize the database with a new password. Validate the password strength and match.
    """
    if request.method == 'GET':
        return render_template('initialize.html')

    new_password = request.form.get('newPassword')
    confirm_password = request.form.get('confirmPassword')

    if new_password != confirm_password:
        return render_template('initialize.html', error="Passwords do not match.")

    if len(new_password) < 16:
        return render_template('initialize.html', error="Password must be at least 16 characters long.")

    if (not re.search(r'[A-Z]', new_password) or
        not re.search(r'[a-z]', new_password) or
        not re.search(r'\d', new_password) or
        not re.search(r'[@#$%^&+=!]', new_password)):
        return render_template('initialize.html', error="Password must include at least one uppercase letter, one lowercase letter, one digit, and one special character.")

    if database_exists(DBPATH):
        return render_template('initialize.html', error="Database already exists at the specified location.")
    
    try:
        functions.initialize_db(DBPATH, new_password)
        session['MasterPassword'] = new_password
        return redirect(url_for('vault'))
    except Exception:
        logging.error("Failed to initialize the database during initialization route.")
        return render_template('initialize.html', error="Failed to initialize the database. Please try again.")

@app.route('/vault', methods=['GET', 'POST'])
def vault():
    """
    Render the vault page if the user is authorized.
    """
    if check_authorization():
        return render_template('vault.html')
    return render_template('login.html', error="* Authorization required to access the vault")

@app.route('/data', methods=['POST'])
def get_data():
    """
    Retrieve data from the database if the user is authorized.
    """
    if not check_authorization():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = functions.load_db(DBPATH, session['MasterPassword'])
        return jsonify(data)
    except Exception:
        logging.error("Failed to retrieve data during get_data route.")
        return jsonify({'error': 'Failed to retrieve data. Please try again later.'}), 500

@app.route('/accounts', methods=['POST', 'PUT', 'DELETE'])
def manage_account():
    """
    Manage user accounts with different HTTP methods.
    - POST: Add a new account
    - PUT: Edit an existing account
    - DELETE: Remove an account
    """
    if not check_authorization():
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Invalid JSON'}),

    try:
        if request.method == 'POST':
            account_data = {
                'name': data['name'],
                'url': data['url'], 
                'password': data['password']
            }
            functions.add_account(DBPATH, IDLENGTH, session['MasterPassword'], account_data)
            return jsonify({"status": "success", "action": "added"})

        elif request.method == 'PUT':
            account_id = data['id']
            account_data = {
                'name': data['name'],
                'url': data['url'],  
                'password': data['password']
            }
            functions.edit_account(DBPATH, account_id, account_data, session['MasterPassword'])
            return jsonify({"status": "success", "action": "edited"})

        elif request.method == 'DELETE':
            account_id = data['id']
            functions.delete_account(DBPATH, account_id)
            return jsonify({"status": "success", "action": "deleted"})

        else:
            return jsonify({"error": "Method not allowed"}), 405
    except KeyError:
        return jsonify({"error": "Missing required data."}), 400
    except Exception:
        logging.error("An error occurred during account management.")
        return jsonify({"error": "An error occurred. Please try again later."}), 500

@app.route('/logout', methods=['GET'])
def logout():
    """
    Log out the user by clearing the session and regenerating the secret key.
    """
    if 'MasterPassword' not in session:
        return redirect(url_for('index'))

    del session['MasterPassword']
    app.secret_key = functions.generate_id(IDLENGTH) 
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
