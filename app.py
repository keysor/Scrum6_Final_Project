from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)

DATABASE = 'reservations.db'

# Function to get database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Close database connection at the end of each request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

admin_username = "admin"
admin_password = "admin123"

# Function to generate cost matrix for flights
def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix

# Function to calculate total sales
def calculate_total_sales():
    total_sales = sum(sum(row) for row in get_cost_matrix())
    return total_sales

@app.route('/')
def main_menu():
    return render_template('main_menu.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
        admin = cursor.fetchone()
        cursor.close()
        if admin:
            return redirect(url_for('admin_portal'))
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template('admin_login.html', error_message=error_message)
    return render_template('admin_login.html')

@app.route('/admin_portal')
def admin_portal():
    total_sales = calculate_total_sales()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM reservations")
    reservations = cursor.fetchall()
    cursor.close()
    return render_template('admin_portal.html', total_sales=total_sales, reservations=reservations)

@app.route('/reserve_seat', methods=['GET', 'POST'])
def reserve_seat():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        seat_row = int(request.form['seat_row'])
        seat_column = int(request.form['seat_column'])
        # Generate reservation code
        reservation_code = f"{first_name.upper()}{last_name.upper()}-{seat_row}-{seat_column}"
        # Create a new database connection and cursor
        with sqlite3.connect('reservations.db') as conn:
            cursor = conn.cursor()
            # Insert reservation into reservations table
            cursor.execute("INSERT INTO reservations (passengerName, seatRow, seatColumn, eTicketNumber) VALUES (?, ?, ?, ?)",
                           (f"{first_name} {last_name}", seat_row, seat_column, reservation_code))
            conn.commit()
        return render_template('reservation_success.html', reservation_code=reservation_code)
    return render_template('reserve_seat.html')

if __name__ == '__main__':
    app.run(debug=True)
