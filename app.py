from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Get database path from environment variable or use default
DATABASE_PATH = os.getenv('DATABASE_PATH', 'reservations.db')

# Ensure the database directory exists
db_dir = os.path.dirname(DATABASE_PATH)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir)
    print(f"Created database directory: {db_dir}")

def get_db():
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db

def get_cost_matrix():
    return [[100, 75, 50, 100] for row in range(12)]

def generate_reservation_code():
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def init_db():
    print(f"Initializing database at {DATABASE_PATH}...")
    # Read and execute the schema.sql file
    with open('schema.sql', 'r') as f:
        schema = f.read()
    
    # Execute the schema
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.executescript(schema)
        print("Schema executed successfully")
        
    # Create default admin if not exists
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = 'admin'")
        admin = cursor.fetchone()
        if not admin:
            print("Creating default admin user...")
            cursor.execute(
                "INSERT INTO admins (username, password) VALUES (?, ?)",
                ('admin', 'admin123')
            )
            conn.commit()
            print("Default admin user created!")
            print("Username: admin")
            print("Password: admin123")
        else:
            print("Admin user already exists!")
            print(f"Username: {admin[0]}")
            print(f"Password: {admin[1]}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Login attempt - Username: {username}, Password: {password}")
        
        db = get_db()
        cursor = db.cursor()
        
        # Debug: Check if admin exists
        cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
        admin = cursor.fetchone()
        if admin:
            print(f"Admin found: {admin['username']}")
            print(f"Stored password: {admin['password']}")
            print(f"Provided password: {password}")
            
            if admin['password'] == password:
                print("Password match! Login successful")
                session['admin'] = True
                db.close()
                return redirect(url_for('admin_dashboard'))
            else:
                print("Password mismatch!")
        else:
            print(f"No admin found with username: {username}")
            
        db.close()
        flash('Invalid credentials')
                
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM reservations")
    reservations = cursor.fetchall()
    db.close()
        
    total_sales = sum(get_cost_matrix()[r['seatRow']][r['seatColumn']] for r in reservations)
    return render_template('admin_dashboard.html', 
                        reservations=reservations,
                        total_sales=total_sales,
                        cost_matrix=get_cost_matrix())

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        try:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            row = int(request.form.get('row')) - 1  # Convert to 0-based index
            column = int(request.form.get('column')) - 1  # Convert to 0-based index
            
            print(f"Reservation attempt - Name: {first_name} {last_name}, Row: {row}, Column: {column}")
            
            passenger_name = f"{first_name} {last_name}"
            e_ticket = generate_reservation_code()
            
            db = get_db()
            cursor = db.cursor()
            
            # Check if seat is already reserved
            cursor.execute("SELECT * FROM reservations WHERE seatRow = ? AND seatColumn = ?",
                        (row, column))
            if cursor.fetchone():
                db.close()
                flash('Seat already reserved')
                return redirect(url_for('reserve'))
            
            # Create new reservation
            cursor.execute(
                "INSERT INTO reservations (passengerName, seatRow, seatColumn, eTicketNumber) VALUES (?, ?, ?, ?)",
                (passenger_name, row, column, e_ticket)
            )
            db.commit()
            db.close()
            
            print(f"Reservation successful - Ticket: {e_ticket}")
            flash(f'Reservation successful! Your reservation code is: {e_ticket}')
            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error during reservation: {str(e)}")
            flash('An error occurred during reservation. Please try again.')
            return redirect(url_for('reserve'))
    
    # Get current reservations for the seating chart
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM reservations")
        reservations = cursor.fetchall()
        db.close()
        
        return render_template('reserve.html', 
                            cost_matrix=get_cost_matrix(),
                            reservations=reservations)
    except Exception as e:
        print(f"Error loading reservations: {str(e)}")
        flash('Error loading seating chart. Please try again.')
        return redirect(url_for('index'))

@app.route('/admin/delete_reservation/<int:id>')
def delete_reservation(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM reservations WHERE id = ?", (id,))
    db.commit()
    db.close()
    
    flash('Reservation deleted successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Delete the database file to start fresh
    if os.path.exists(DATABASE_PATH):
        print(f"Deleting existing database at {DATABASE_PATH}...")
        os.remove(DATABASE_PATH)
    
    init_db()  # Initialize database with schema and default admin
    app.run(host='0.0.0.0', debug=True) 