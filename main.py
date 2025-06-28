from flask import Flask, render_template, redirect, request, url_for, flash, session
import sqlite3
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-123' 

#Made By Anmol Choudhury


# ======================= DATABASE FUNCTIONS =======================
def init_db():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            date_till TEXT,
            room_number TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            room_number TEXT PRIMARY KEY,
            status TEXT NOT NULL
        )
    ''')
    room_numbers = ['101', '102', '103', '104', '105', '106']
    for rn in room_numbers:
        cursor.execute('''
            INSERT OR IGNORE INTO rooms (room_number, status)
            VALUES (?, 'available')
        ''', (rn,))
    conn.commit()
    conn.close()

def get_customer_by_username(username):
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customers WHERE username = ?', (username,))
    customer = cursor.fetchone()
    conn.close()
    return customer

def get_customer_by_id(customer_id):
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
    customer = cursor.fetchone()
    conn.close()
    return customer

def get_customer_booking(customer_id):
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT room_number, date_till FROM customers WHERE id = ? AND room_number IS NOT NULL', (customer_id,))
    booking = cursor.fetchone()
    conn.close()
    return booking

def count_available_rooms():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM rooms WHERE status = 'available'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_all_bookings():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, room_number, phone, date_till FROM customers WHERE room_number IS NOT NULL')
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def get_available_room():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT room_number FROM rooms WHERE status = "available" ORDER BY room_number LIMIT 1')
    room = cursor.fetchone()
    conn.close()
    return room[0] if room else None

def book_room_for_customer(customer_id, date_till):
    room_number = get_available_room()
    if not room_number:
        return None
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE customers SET room_number = ?, date_till = ? WHERE id = ?', (room_number, date_till, customer_id))
    cursor.execute('UPDATE rooms SET status = "occupied" WHERE room_number = ?', (room_number,))
    conn.commit()
    conn.close()
    return room_number

def remove_booking(booking_id):
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT room_number FROM customers WHERE id = ?', (booking_id,))
    result = cursor.fetchone()
    if result and result[0]:
        room_number = result[0]
        cursor.execute('UPDATE rooms SET status = "available" WHERE room_number = ?', (room_number,))
    cursor.execute('UPDATE customers SET room_number = NULL, date_till = "" WHERE id = ?', (booking_id,))
    conn.commit()
    conn.close()

def remove_expired_bookings():
    today = date.today().isoformat()
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    # Find all expired bookings
    cursor.execute('SELECT id, room_number FROM customers WHERE room_number IS NOT NULL AND date_till < ?', (today,))
    expired = cursor.fetchall()
    for booking_id, room_number in expired:
        # Set room as available
        cursor.execute('UPDATE rooms SET status = "available" WHERE room_number = ?', (room_number,))
        # Remove booking from customer
        cursor.execute('UPDATE customers SET room_number = NULL, date_till = "" WHERE id = ?', (booking_id,))
    conn.commit()
    conn.close()

# ======================= CUSTOMER ROUTES =======================
@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        customer = get_customer_by_username(username)
        if customer and check_password_hash(customer[2], password):
            session['customer_id'] = customer[0]
            return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('customer.html')

@app.route('/customer_register', methods=['GET', 'POST'])
def customer_register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        try:
            hashed_pw = generate_password_hash(password)
            conn = sqlite3.connect('hotel.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO customers (username, password_hash, name, phone, date_till)
                VALUES (?, ?, ?, ?, '')
            ''', (username, hashed_pw, name, phone))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login', 'success')
            return redirect(url_for('customer_login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')
    return render_template('register.html')

@app.route('/customer_dashboard', methods=['GET', 'POST'])
def customer_dashboard():
    remove_expired_bookings()
    customer_id = session.get('customer_id')
    if not customer_id:
        return redirect(url_for('customer_login'))
    customer = get_customer_by_id(customer_id)
    booking = get_customer_booking(customer_id)
    bookings = []
    if booking:
        bookings.append({'room_number': booking[0], 'date_till': booking[1]})
    return render_template('customer_dashboard.html', bookings=bookings)

@app.route('/book_room', methods=['POST'])
def book_room():
    customer_id = session.get('customer_id')
    if not customer_id:
        return redirect(url_for('customer_login'))
    date_till = request.form.get('date_till')
    if not date_till:
        flash('Please select a date.', 'error')
        return redirect(url_for('customer_dashboard'))
    # Prevent booking for past dates
    try:
        selected_date = datetime.strptime(date_till, '%Y-%m-%d').date()
        if selected_date < date.today():
            flash('Cannot book for a past date.', 'error')
            return redirect(url_for('customer_dashboard'))
    except ValueError:
        flash('Invalid date format.', 'error')
        return redirect(url_for('customer_dashboard'))
    if get_customer_booking(customer_id):
        flash('You already have a booking.', 'error')
        return redirect(url_for('customer_dashboard'))
    room_number = book_room_for_customer(customer_id, date_till)
    if room_number:
        flash(f'Booking successful! Your room number is {room_number}.', 'success')
    else:
        flash('All rooms are currently booked! Please try again later.', 'error')
    return redirect(url_for('customer_dashboard'))

@app.route('/customer_logout')
def customer_logout():
    session.pop('customer_id', None)
    return redirect(url_for('index'))

# ======================= ADMIN ROUTES =======================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "admin" and password == "1234":
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    remove_expired_bookings()
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('dashboard.html')

@app.route('/manage_bookings', methods=['GET', 'POST'])
def manage_bookings():
    remove_expired_bookings()
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        remove_booking(booking_id)
        return redirect(url_for('manage_bookings'))
    bookings = get_all_bookings()
    return render_template('manage.html', bookings=bookings)

@app.route('/view_rooms')
def view_rooms():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT room_number, status FROM rooms ORDER BY room_number')
    rooms = [{'room_number': row[0], 'status': row[1]} for row in cursor.fetchall()]
    conn.close()
    return render_template('rooms.html', rooms=rooms)

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        if count_available_rooms() == 0:
            flash('No rooms available! All rooms are occupied.', 'error')
            return redirect(url_for('add_customer'))
        name = request.form.get('first_name')
        phone = request.form.get('phone')
        date_till = request.form.get('date_till')
        room_number = get_available_room()
        if room_number:
            conn = sqlite3.connect('hotel.db')
            cursor = conn.cursor()
            # Insert a dummy username/hashed password for admin-added customers
            cursor.execute('''
                INSERT INTO customers (username, password_hash, name, phone, date_till, room_number)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (phone, '', name, phone, date_till, room_number))
            cursor.execute('UPDATE rooms SET status = "occupied" WHERE room_number = ?', (room_number,))
            conn.commit()
            conn.close()
            return redirect(url_for('manage_bookings'))
    return render_template('add.html')

@app.route('/view_customer_details')
def view_customer_details():
    remove_expired_bookings()
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    bookings = get_all_bookings()
    formatted_bookings = [(b[1], b[2], b[3], b[4]) for b in bookings]
    return render_template('view.html', bookings=formatted_bookings)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/customer')
def customer():
    return redirect(url_for('customer_login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
