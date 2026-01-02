import mysql.connector
from db import get_db_connection
import random

def populate_workers():
    print("Populating workers...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Worker Data
    workers_data = [
        ("Rahim Uddin", "rahim@example.com", "electrician", 500),
        ("Karim Mia", "karim@example.com", "plumber", 450),
        ("Salma Begum", "salma@example.com", "house_help", 300),
        ("Fatima Akter", "fatima@example.com", "cleaner", 350),
        ("Jamal Hossain", "jamal@example.com", "driver", 600),
        ("Kamal Ahmed", "kamal@example.com", "painter", 550),
        ("Sufia Khatun", "sufia@example.com", "house_help", 320),
        ("Rafiqul Islam", "rafiq@example.com", "electrician", 520),
        ("Nasrin Sultana", "nasrin@example.com", "cleaner", 360),
        ("Abdul Malek", "malek@example.com", "plumber", 480),
        ("Moniruzzaman", "monir@example.com", "ac_repair", 700),
        ("Shahidul Alam", "shahid@example.com", "gardener", 400),
        ("Rina Parvin", "rina@example.com", "house_help", 310),
        ("Farid Uddin", "farid@example.com", "painter", 530),
        ("Jasmine Ara", "jasmine@example.com", "cleaner", 340),
         ("Moklesur Rahman", "mokles@example.com", "driver", 620),
    ]

    for name, email, category, wage in workers_data:
        try:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                print(f"Skipping {email}, already exists.")
                continue

            # Create User
            cursor.execute(
                "INSERT INTO users (name, email, password, role, phone, address) VALUES (%s, %s, %s, 'worker', '01700000000', 'Dhaka, Bangladesh')",
                (name, email, "password123")
            )
            user_id = cursor.lastrowid

            # Create Worker
            cursor.execute(
                "INSERT INTO workers (user_id, job_category, wage, rating_avg) VALUES (%s, %s, %s, %s)",
                (user_id, category, wage, round(random.uniform(3.5, 5.0), 2))
            )
            print(f"Added worker: {name} ({category})")

        except mysql.connector.Error as err:
            print(f"Error adding {name}: {err}")

    conn.commit()
    cursor.close()
    conn.close()
    print("Population complete.")

if __name__ == "__main__":
    populate_workers()
