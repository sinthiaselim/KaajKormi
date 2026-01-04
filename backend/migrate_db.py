import mysql.connector
from db import get_db_connection

def migrate():
    print("Migrating database...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Add payment_method column
        try:
            cursor.execute("ALTER TABLE requests ADD COLUMN payment_method ENUM('cash', 'bkash', 'nagad') DEFAULT NULL")
            print("Added payment_method column.")
        except mysql.connector.Error as err:
            if err.errno == 1060: # Key constraint/Duplicate column name
                print("payment_method column already exists.")
            else:
                print(f"Error adding payment_method: {err}")

        # Add payment_status column
        try:
            cursor.execute("ALTER TABLE requests ADD COLUMN payment_status ENUM('pending', 'paid') DEFAULT 'pending'")
            print("Added payment_status column.")
        except mysql.connector.Error as err:
            if err.errno == 1060:
                print("payment_status column already exists.")
            else:
                print(f"Error adding payment_status: {err}")

        conn.commit()
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
