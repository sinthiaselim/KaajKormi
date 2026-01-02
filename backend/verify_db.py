import mysql.connector
from db import get_db_connection

def verify_data():
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            
            tables = ['users', 'workers', 'requests', 'reviews']
            print("\nTable Counts:")
            print("-" * 20)
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table.capitalize()}: {count}")
            
            print("\nSample Workers:")
            cursor.execute("SELECT u.name, w.job_category, u.address FROM users u JOIN workers w ON u.id = w.user_id LIMIT 3")
            for row in cursor.fetchall():
                print(f"- {row[0]} ({row[1]}) from {row[2]}")

            cursor.close()
            conn.close()
            return True
        else:
            print("Failed to connect.")
            return False
    except mysql.connector.Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return False

if __name__ == "__main__":
    verify_data()
