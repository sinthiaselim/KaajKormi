# Study Guide: Feedback & Rating Logic
# This file demonstrates how reviews are submitted and how the worker's average rating is updated.

@app.route('/submit_review/<int:request_id>', methods=['GET', 'POST'])
def submit_review(request_id):
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        rating = request.form['rating']
        comment = request.form['comment']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # 1. VALIDATION: Ensure user can only review after a job is COMPLETED
            cursor.execute("SELECT status FROM requests WHERE id = %s", (request_id,))
            req = cursor.fetchone()
            if not req or req['status'] != 'completed':
                flash('You can only review completed jobs.', 'warning')
                return redirect(url_for('customer_dashboard'))

            # 2. SAVE REVIEW: Insert the new rating and comment
            cursor.execute(
                "INSERT INTO reviews (request_id, rating, comment) VALUES (%s, %s, %s)",
                (request_id, rating, comment)
            )
            
            # 3. UPDATE RATING_AVG: Recalculate and update the worker's average rating
            # This query calculates the average of all reviews for this specific worker
            cursor.execute("""
                UPDATE workers w
                SET w.rating_avg = (
                    SELECT AVG(r.rating) 
                    FROM reviews r 
                    JOIN requests req ON r.request_id = req.id 
                    WHERE req.worker_id = w.user_id
                )
                WHERE w.user_id = (SELECT worker_id FROM requests WHERE id = %s)
            """, (request_id,))
            
            conn.commit()
            flash('Review submitted successfully!', 'success')
        except Exception as e:
            flash(f'Error submitting review: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('customer_dashboard'))
    
    # ... (GET method logic for showing the form)
