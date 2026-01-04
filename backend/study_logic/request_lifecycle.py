# Study Guide: Service Request Lifecycle
# This file demonstrates how a service request is sent and how its status is updated.

# 1. SENDING A REQUEST
@app.route('/request_service/<int:worker_id>', methods=['POST'])
def request_service(worker_id):
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Default scheduled date is tomorrow
        from datetime import datetime, timedelta
        default_schedule = datetime.now() + timedelta(days=1)
        
        # Insert request with 'pending' status
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


# 2. UPDATING REQUEST STATUS (Accepted, Rejected, Completed)
@app.route('/update_request/<int:request_id>/<status>')
def update_request(request_id, status):
    if 'user_id' not in session or session.get('role') != 'worker':
        return redirect(url_for('login'))
    
    # Ensure only valid status changes are allowed
    if status not in ['accepted', 'rejected', 'completed']:
        return redirect(url_for('worker_dashboard'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update status enum in the database
    cursor.execute("UPDATE requests SET status = %s WHERE id = %s", (status, request_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash(f'Request {status}!', 'success')
    return redirect(url_for('worker_dashboard'))
