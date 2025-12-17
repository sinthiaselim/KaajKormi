import mysql.connector
from mysql.connector import Error
from db import get_db_connection
import random
from datetime import datetime, timedelta

def wipe_data(cursor):
    """Clear existing data to avoid duplicates."""
    print("Clearing existing data...")
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

        # 1. Create Workers
        workers_data = [
            ("Rahim Uddin", "rahim@example.com", "123456", "01711111111", "Dhaka, Mirpur", "electrician", 500),
            ("Karim Mia", "karim@example.com", "123456", "01722222222", "Dhaka, Dhanmondi", "plumber", 400),
            ("Salma Begum", "salma@example.com", "123456", "01733333333", "Dhaka, Gulshan", "house_help", 300),
            ("Jamal Hossain", "jamal@example.com", "123456", "01744444444", "Dhaka, Uttara", "driver", 600),
            ("Sokina Bibi", "sokina@example.com", "123456", "01755555555", "Dhaka, Mohakhali", "cleaner", 250),
            ("Rajib Ahmed", "rajib@example.com", "123456", "01766666666", "Chittagong, GEC", "ac_repair", 800),
            ("Mamun Khan", "mamun@example.com", "123456", "01777777777", "Sylhet, Zindabazar", "painter", 450),
            ("Hasan Ali", "hasan@example.com", "123456", "01788888888", "Rajshahi, Saheb Bazar", "gardener", 350)
        ]

        print("Seeding workers...")
        worker_ids = []
        for name, email, pwd, phone, addr, cat, wage in workers_data:
            # Insert User
            cursor.execute(
                "INSERT INTO users (name, email, password, role, phone, address) VALUES (%s, %s, %s, 'worker', %s, %s)",
                (name, email, pwd, phone, addr)
            )
            user_id = cursor.lastrowid
            worker_ids.append(user_id)
            
            # Insert Worker Profile
            cursor.execute(
                "INSERT INTO workers (user_id, job_category, wage, rating_avg) VALUES (%s, %s, %s, %s)",
                (user_id, cat, wage, round(random.uniform(3.5, 5.0), 2))
            )
        
        # 2. Create Customers
        customers_data = [
            ("Tanvir Hasan", "tanvir@example.com", "123456", "01811111111", "Dhaka, Banani"),
            ("Fabia Islam", "fabia@example.com", "123456", "01822222222", "Dhaka, Bashundhara"),
            ("Nusrat Jahan", "nusrat@example.com", "123456", "01833333333", "Chittagong, Khulshi")
        ]

        print("Seeding customers...")
        customer_ids = []
        for name, email, pwd, phone, addr in customers_data:
            cursor.execute(
                "INSERT INTO users (name, email, password, role, phone, address) VALUES (%s, %s, %s, 'customer', %s, %s)",
                (name, email, pwd, phone, addr)
            )
            customer_ids.append(cursor.lastrowid)

        # 3. Create Dummy Requests and Reviews
        print("Seeding requests and reviews...")
        statuses = ['pending', 'accepted', 'completed', 'rejected']
        
        for _ in range(15):
            cust_id = random.choice(customer_ids)
            work_id = random.choice(worker_ids)
            status = random.choice(statuses)
            date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            cursor.execute(
                "INSERT INTO requests (customer_id, worker_id, status, request_date) VALUES (%s, %s, %s, %s)",
                (cust_id, work_id, status, date)
            )
            req_id = cursor.lastrowid
            
            # If completed, maybe add a review
            if status == 'completed' and random.choice([True, False]):
                rating = random.randint(3, 5)
                comments = ["Great service!", "Good job.", "Satisfied.", "Could be better.", "Excellent work!"]
                cursor.execute(
                    "INSERT INTO reviews (request_id, rating, comment) VALUES (%s, %s, %s)",
                    (req_id, rating, random.choice(comments))
                )

        conn.commit()
        print("Database seeded successfully!")
        
    except Error as e:
        print(f"Error seeding data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    seed_data()
