from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_db_connection
import mysql.connector
import stripe

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'  # Change this for production
stripe.api_key = 'sk_test_51SlOfuPu4qRXX70nfcV7wSt5vwvZx8XUE36sN5saDyIWcqcsrj758RaJTRv97gMTXuTP2YtVhbJPhBwRRecGTB7B00xHUrmsiP'

# Context Processor for Worker Images
@app.context_processor
def utility_processor():
    def get_worker_image(worker_name, worker_id=0):
        name_lower = worker_name.lower()
        
        # Gender Heuristic for common Bangladeshi/Muslim names
        female_keywords = ['begum', 'akter', 'khatun', 'sultana', 'parvin', 'ara', 'fatima', 'salma', 'sufia', 'nasrin', 'rina', 'jasmine', 'fahmida', 'sabina', 'monira']
        
        is_female = any(keyword in name_lower for keyword in female_keywords)
        
        if is_female:
            # Assign from female images pool (2, 4, 6)
            img_pool = [2, 4, 6]
        else:
            # Assign from male images pool (1, 3, 5)
            img_pool = [1, 3, 5]
            
        # Deterministic assignment based on worker_id, but limited to gender pool
        idx = (worker_id % len(img_pool))
        img_id = img_pool[idx]
        
        return url_for('static', filename=f'img/workers/worker_{img_id}.png')
    return dict(get_worker_image=get_worker_image)

# --- Authentication Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'customer':
            return redirect(url_for('customer_dashboard'))
        else:
            return redirect(url_for('worker_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and user['password'] == password: # In real app, hash passwords!
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            if user['role'] == 'customer':
                return redirect(url_for('customer_dashboard'))
            else:
                return redirect(url_for('worker_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role', 'customer')
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Insert into users
            cursor.execute(
                "INSERT INTO users (name, email, password, role, phone, address) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, email, password, role, phone, address)
            )
            user_id = cursor.lastrowid
            
            # If worker, insert into workers table
            if role == 'worker':
                job_category = request.form['job_category']
                wage = request.form['wage']
                cursor.execute(
                    "INSERT INTO workers (user_id, job_category, wage) VALUES (%s, %s, %s)",
                    (user_id, job_category, wage)
                )
            
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- Customer Routes ---

@app.route('/customer_dashboard')
def customer_dashboard():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch Workers (filter optional)
    category_filter = request.args.get('category')
    search_query = request.args.get('q')
    
    cursor.close()
    conn.close()
    
    return render_template('customer/dashboard.html')

@app.route('/workers')
def browse_workers():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    category_filter = request.args.get('category')
    search_query = request.args.get('q')
    min_rating = request.args.get('rating')
    max_wage = request.args.get('wage')
    
    query = """
        SELECT u.name, u.phone, u.address, w.user_id, w.job_category, w.wage, w.rating_avg 
        FROM users u 
        JOIN workers w ON u.id = w.user_id
        WHERE w.availability = 1
    """
    params = []
    
    if category_filter:
        query += " AND w.job_category = %s"
        params.append(category_filter)
        
    if search_query:
        query += " AND (u.name LIKE %s OR u.address LIKE %s)"
        term = f"%{search_query}%"
        params.append(term)
        params.append(term)
        
    if min_rating:
        query += " AND w.rating_avg >= %s"
        params.append(min_rating)
        
    if max_wage:
        query += " AND w.wage <= %s"
        params.append(max_wage)
        
    cursor.execute(query, tuple(params))
    workers = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('customer/worker_list.html', workers=workers)

@app.route('/worker/<int:worker_id>')
def worker_profile(worker_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Fetch Worker Details
    cursor.execute("""
        SELECT u.name, u.phone, u.address, w.user_id, w.job_category, w.wage, w.rating_avg 
        FROM users u 
        JOIN workers w ON u.id = w.user_id
        WHERE w.user_id = %s
    """, (worker_id,))
    worker = cursor.fetchone()
    
    if not worker:
        flash('Worker not found', 'danger')
        return redirect(url_for('customer_dashboard'))
        
    # 2. Fetch Reviews
    cursor.execute("""
        SELECT r.rating, r.comment, r.created_at
        FROM reviews r
        JOIN requests req ON r.request_id = req.id
        WHERE req.worker_id = %s
        ORDER BY r.created_at DESC
    """, (worker_id,))
    reviews = cursor.fetchall()
    
    # 3. Check if user can review (Has a completed request with no review)
    can_review = None
    if session.get('role') == 'customer':
        cursor.execute("""
            SELECT req.id 
            FROM requests req
            LEFT JOIN reviews r ON req.id = r.request_id
            WHERE req.customer_id = %s AND req.worker_id = %s AND req.status = 'completed' AND r.id IS NULL
            LIMIT 1
        """, (session['user_id'], worker_id))
        can_review = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('customer/worker_profile.html', worker=worker, reviews=reviews, can_review=can_review)

@app.route('/submit_review/<int:request_id>', methods=['POST'])
def submit_review(request_id):
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
        
    rating = request.form['rating']
    comment = request.form['comment']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO reviews (request_id, rating, comment) VALUES (%s, %s, %s)",
            (request_id, rating, comment)
        )
        
        # Update worker average rating (Simplified logic)
        # In a real app, you'd trigger a recalculation
        
        conn.commit()
        flash('Review submitted successfully!', 'success')
    except Exception as e:
        flash(f'Error submitting review: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('customer_dashboard'))

@app.route('/my_requests')
def my_requests():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch My Requests
    cursor.execute("""
        SELECT r.id, r.status, r.request_date, u.name as worker_name, w.job_category 
        FROM requests r
        JOIN users u ON r.worker_id = u.id
        JOIN workers w ON u.id = w.user_id
        WHERE r.customer_id = %s
        ORDER BY r.request_date DESC
    """, (session['user_id'],))
    my_requests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('customer/my_requests.html', my_requests=my_requests)

@app.route('/request_service/<int:worker_id>', methods=['POST'])
def request_service(worker_id):
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
        
    # Optional: Get scheduled date from form, or default to now + 1 day
    # scheduled_date = request.form.get('scheduled_date') 
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        from datetime import datetime, timedelta
        default_schedule = datetime.now() + timedelta(days=1)
        
        cursor.execute(
            "INSERT INTO requests (customer_id, worker_id, status, scheduled_date) VALUES (%s, %s, 'pending', %s)",
            (session['user_id'], worker_id, default_schedule)
        )
        conn.commit()
        flash('Service request sent!', 'success')
    except Exception as e:
        flash(f'Error sending request: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('customer_dashboard'))

@app.route('/pay_now/<int:request_id>')
def pay_now(request_id):
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Fetch Request & Worker Wage
    cursor.execute("""
        SELECT w.wage, r.id 
        FROM requests r 
        JOIN workers w ON r.worker_id = w.user_id 
        WHERE r.id = %s
    """, (request_id,))
    req_data = cursor.fetchone()
    
    if not req_data:
        cursor.close()
        conn.close()
        flash('Request not found', 'danger')
        return redirect(url_for('customer_dashboard'))

    # 2. Check Payment Status in Payments Table
    cursor.execute("SELECT status FROM payments WHERE request_id = %s", (request_id,))
    payment = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if payment and payment['status'] == 'paid':
        flash('Already paid!', 'info')
        return redirect(url_for('customer_dashboard'))

    return render_template('customer/payment_selection.html', request_id=request_id, amount=req_data['wage'])

@app.route('/process_payment/<int:request_id>', methods=['POST'])
def process_payment(request_id):
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
        
    payment_method = request.form.get('payment_method')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch request details + worker wage
    query = """
        SELECT r.id, w.wage, w.job_category, u.name as worker_name
        FROM requests r
        JOIN workers w ON r.worker_id = w.user_id
        JOIN users u ON w.user_id = u.id
        WHERE r.id = %s
    """
    cursor.execute(query, (request_id,))
    req_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if not req_data:
        flash('Request not found.', 'danger')
        return redirect(url_for('my_requests'))

    try:
        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'bdt',
                    'product_data': {
                        'name': f"Service: {req_data['job_category']} by {req_data['worker_name']}",
                    },
                    'unit_amount': int(float(req_data['wage']) * 100),  # Stripe expects amount in cents/poisha
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payment_success', request_id=request_id, _external=True) + '?session_id={CHECKOUT_SESSION_ID}&pm=' + payment_method,
            cancel_url=url_for('payment_cancel', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f'Error creating payment session: {str(e)}', 'danger')
        return redirect(url_for('my_requests'))

@app.route('/payment_success/<int:request_id>')
def payment_success(request_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    payment_method = request.args.get('pm', 'card') # Default to card if from stripe callback
    
    # Logic simplification
    status = 'completed' # Service is completed once paid
    payment_status = 'pending' if payment_method == 'cash' else 'paid'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Update Request Status
        cursor.execute("UPDATE requests SET status = %s WHERE id = %s", (status, request_id))
        
        # 2. Insert into Payments Table
        # Fetch wage first
        cursor.execute("SELECT w.wage FROM requests r JOIN workers w ON r.worker_id = w.user_id WHERE r.id = %s", (request_id,))
        res = cursor.fetchone()
        wage = res[0] if res else 0
        
        cursor.execute("""
            INSERT INTO payments (request_id, amount_paid, payment_method, status) 
            VALUES (%s, %s, %s, %s)
        """, (request_id, wage, payment_method, payment_status))
        
        conn.commit()
        
        if payment_method == 'cash':
            flash('Order confirmed! Please pay cash to the worker.', 'info')
        else:
            flash('Payment successful! Service marked as completed.', 'success')
            
    except Exception as e:
        conn.rollback()
        flash(f'Error recording payment: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('customer_dashboard'))

@app.route('/payment_cancel')
def payment_cancel():
    flash('Payment cancelled.', 'info')
    return redirect(url_for('my_requests'))

# --- Chat Routes ---

@app.route('/chat/<int:other_user_id>', methods=['GET'])
def chat(other_user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if other user exists
    cursor.execute("SELECT id, name, role FROM users WHERE id = %s", (other_user_id,))
    other_user = cursor.fetchone()
    
    if not other_user:
        flash('User not found.', 'danger')
        conn.close()
        return redirect(url_for('index'))

    # Fetch conversation
    user_id = session['user_id']
    query = """
        SELECT * FROM messages 
        WHERE (sender_id = %s AND receiver_id = %s) 
           OR (sender_id = %s AND receiver_id = %s)
        ORDER BY timestamp ASC
    """
    cursor.execute(query, (user_id, other_user_id, other_user_id, user_id))
    messages = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('chat.html', other_user=other_user, messages=messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    sender_id = session['user_id']
    receiver_id = request.form['receiver_id']
    message = request.form['message']
    
    if not message:
         return redirect(url_for('chat', other_user_id=receiver_id))
         
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
        (sender_id, receiver_id, message)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('chat', other_user_id=receiver_id))

@app.route('/messages')
def view_messages():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    user_id = session['user_id']
    
    # Find list of people user has chatted with (GROUP BY tricky in strict mode, simpler to iterate in python or complex query)
    # Using a slightly complex query to get latest message per user
    query = """
        SELECT 
            u.id, u.name, u.role,
            m.message as last_message,
            m.timestamp
        FROM users u
        JOIN (
            SELECT 
                CASE 
                    WHEN sender_id = %s THEN receiver_id 
                    ELSE sender_id 
                END as other_id,
                MAX(id) as max_msg_id
            FROM messages
            WHERE sender_id = %s OR receiver_id = %s
            GROUP BY other_id
        ) latest ON u.id = latest.other_id
        JOIN messages m ON m.id = latest.max_msg_id
        ORDER BY m.timestamp DESC
    """
    
    cursor.execute(query, (user_id, user_id, user_id))
    conversations = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('my_messages.html', conversations=conversations)

# --- Worker Routes ---

@app.route('/worker_dashboard')
def worker_dashboard():
    if 'user_id' not in session or session.get('role') != 'worker':
        return redirect(url_for('login'))
        
    # Dashboard is now just the landing/marketplace view for workers
    return render_template('worker/dashboard.html')

@app.route('/worker/requests')
def worker_requests():
    if 'user_id' not in session or session.get('role') != 'worker':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch Incoming Requests
    cursor.execute("""
        SELECT r.id, r.status, r.request_date, u.name as customer_name, u.address, u.phone
        FROM requests r
        JOIN users u ON r.customer_id = u.id
        WHERE r.worker_id = %s AND r.status = 'pending'
    """, (session['user_id'],))
    incoming_requests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('worker/requests.html', incoming_requests=incoming_requests)

@app.route('/worker/history')
def worker_history():
    if 'user_id' not in session or session.get('role') != 'worker':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch History
    cursor.execute("""
        SELECT r.id, r.status, r.request_date, u.name as customer_name
        FROM requests r
        JOIN users u ON r.customer_id = u.id
        WHERE r.worker_id = %s AND r.status != 'pending'
        ORDER BY r.request_date DESC
    """, (session['user_id'],))
    history = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('worker/history.html', history=history)

@app.route('/update_request/<int:request_id>/<status>')
def update_request(request_id, status):
    if 'user_id' not in session or session.get('role') != 'worker':
        return redirect(url_for('login'))
    
    if status not in ['accepted', 'rejected', 'completed']:
        return redirect(url_for('worker_dashboard'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE requests SET status = %s WHERE id = %s", (status, request_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash(f'Request {status}!', 'success')
    return redirect(url_for('worker_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
