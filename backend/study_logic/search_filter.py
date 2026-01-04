# Study Guide: Search and Filtering
# This file demonstrates how customers can search for workers by name and filter by category, rating, and wage.

@app.route('/workers')
def browse_workers():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. RETRIEVE FILTER PARAMETERS from the URL query string
    category_filter = request.args.get('category') # e.g., ?category=plumber
    search_query = request.args.get('q')           # e.g., ?q=rahim
    min_rating = request.args.get('rating')        # e.g., ?rating=4
    max_wage = request.args.get('wage')            # e.g., ?wage=500
    
    # 2. BASE QUERY: Start with a simple SELECT JOIN
    query = """
        SELECT u.name, u.phone, u.address, w.user_id, w.job_category, w.wage, w.rating_avg 
        FROM users u 
        JOIN workers w ON u.id = w.user_id
        WHERE w.availability = 1
    """
    params = []
    
    # 3. DYNAMICALLY BUILD THE WHERE CLAVSE based on provided filters
    
    # Filter by category
    if category_filter:
        query += " AND w.job_category = %s"
        params.append(category_filter)
        
    # Search by name or address
    if search_query:
        query += " AND (u.name LIKE %s OR u.address LIKE %s)"
        term = f"%{search_query}%"
        params.append(term)
        params.append(term)
        
    # Filter by minimum rating
    if min_rating:
        query += " AND w.rating_avg >= %s"
        params.append(min_rating)
        
    # Filter by maximum wage
    if max_wage:
        query += " AND w.wage <= %s"
        params.append(max_wage)
        
    # 4. EXECUTE the final query with the collected parameters
    cursor.execute(query, tuple(params))
    workers = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('customer/worker_list.html', workers=workers)
