import mysql.connector
from mysql.connector import Error
from db import get_db_connection
import random
from datetime import datetime, timedelta

def wipe_data(cursor):
    """Clear existing data to avoid duplicates."""
    print("Clearing existing data...")
    # Order matters due to foreign keys
    tables = ['reviews', 'requests', 'workers', 'users']
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
        cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
    print("Data cleared.")

def seed_data():
    conn = get_db_connection()
    if not conn:
        print("Could not connect to database.")
        return

    cursor = conn.cursor()
    
    try:
        # Wipe old data
        wipe_data(cursor)

        # predefined lists for generation
        dhaka_areas = ["Mirpur", "Dhanmondi", "Gulshan", "Uttara", "Mohakhali", "Banani", "Bashundhara", "Farmgate", "Malibagh", "Old Dhaka", "Badda", "Rampura", "Mohammadpur"]
        cities = ["Chittagong", "Sylhet", "Rajshahi", "Khulna", "Barisal", "Comilla"]
        
        job_categories = ["electrician", "plumber", "house_help", "driver", "cleaner", "ac_repair", "painter", "gardener", "cook", "tutor", "carpenter"]
        
        first_names = ["Rahim", "Karim", "Jamal", "Kamal", "Hasan", "Sokina", "Salma", "Fatema", "Ayesha", "Nasrin", "Rafiq", "Jabbar", "Salam", "Borkot", "Sujon", "Mizan", "Tarek", "Rubel", "Sohan", "Nadia", "Farah", "Sadia", "Mitu", "Rina"]
        last_names = ["Uddin", "Mia", "Hossain", "Khan", "Ali", "Begum", "Akter", "Islam", "Ahmed", "Chowdhury", "Sarker", "Rahman", "Haque"]

        def generate_name():
            return f"{random.choice(first_names)} {random.choice(last_names)}"

        def generate_phone():
            return f"01{random.choice(['7', '8', '3', '9', '5'])}{random.randint(10000000, 99999999)}"

        def generate_address():
            if random.random() < 0.7:
                return f"Dhaka, {random.choice(dhaka_areas)}"
            else:
                city = random.choice(cities)
                return f"{city}, {random.choice(['Center', 'Bazar', 'Road 1', 'Housing', 'Colony'])}"

        # 1. Create Workers
        print("Seeding workers...")
        worker_ids = []
        for i in range(30): # Generate 30 workers
            name = generate_name()
            email = f"worker{i+1}@example.com"
            pwd = "password123"
            phone = generate_phone()
            addr = generate_address()
            cat = random.choice(job_categories)
            wage = random.choice([200, 300, 350, 400, 450, 500, 600, 800, 1000])
            
            cursor.execute(
                "INSERT INTO users (name, email, password, role, phone, address) VALUES (%s, %s, %s, 'worker', %s, %s)",
                (name, email, pwd, phone, addr)
            )
            user_id = cursor.lastrowid
            worker_ids.append(user_id)
            
            cursor.execute(
                "INSERT INTO workers (user_id, job_category, wage, rating_avg) VALUES (%s, %s, %s, %s)",
                (user_id, cat, wage, round(random.uniform(3.0, 5.0), 2))
            )

        # 2. Create Customers
        print("Seeding customers...")
        customer_ids = []
        for i in range(15): # Generate 15 customers
            name = generate_name()
            email = f"customer{i+1}@example.com"
            pwd = "password123"
            phone = generate_phone()
            addr = generate_address()
            
            cursor.execute(
                "INSERT INTO users (name, email, password, role, phone, address) VALUES (%s, %s, %s, 'customer', %s, %s)",
                (name, email, pwd, phone, addr)
            )
            customer_ids.append(cursor.lastrowid)

        # 3. Create Requests and Reviews
        print("Seeding requests and reviews...")
        statuses = ['pending', 'accepted', 'completed', 'rejected', 'cancelled']
        
        for _ in range(60): # 60 requests
            cust_id = random.choice(customer_ids)
            work_id = random.choice(worker_ids)
            status = random.choice(statuses)
            # Random date in last 3 months
            days_ago = random.randint(0, 90)
            date = datetime.now() - timedelta(days=days_ago)
            
            cursor.execute(
                "INSERT INTO requests (customer_id, worker_id, status, request_date) VALUES (%s, %s, %s, %s)",
                (cust_id, work_id, status, date)
            )
            req_id = cursor.lastrowid
            
            # If completed, maybe add a review
            if status == 'completed' and random.choice([True, True, False]): # Higher chance of review
                rating = random.choices([1, 2, 3, 4, 5], weights=[5, 5, 15, 35, 40], k=1)[0]
                comments = [
                    "Excellent service!", "Very professional.", "Good, but came late.", 
                    "Not satisfied.", "Highly recommended.", "Will hire again.", 
                    "Friendly behavior.", "Did a quick job.", "Average service."
                ]
                cursor.execute(
                    "INSERT INTO reviews (request_id, rating, comment, created_at) VALUES (%s, %s, %s, %s)",
                    (req_id, rating, random.choice(comments), date + timedelta(hours=2))
                )

        conn.commit()
        print(f"Database seeded with {len(worker_ids)} workers, {len(customer_ids)} customers, and 60 requests!")
        
    except Error as e:
        print(f"Error seeding data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    seed_data()
