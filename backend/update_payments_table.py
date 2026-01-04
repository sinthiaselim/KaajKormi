import mysql.connector
from db import get_db_connection

def update_table():
    print("Updating payments table...")
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return
        
    cursor = conn.cursor()
    
    try:
        # Update ENUM
        # Note: We use MODIFY to change the enum values. Existing 'nagad' values might cause issues if they exist.
        # But since this is a dev/test environment, we'll assume it's safe or we'll handle it if it fails.
        cursor.execute("ALTER TABLE payments MODIFY COLUMN payment_method ENUM('cash', 'bkash', 'card') NOT NULL")
        print("Updated payment_method enum successfully.")
        
        # Add new columns
        cols_to_add = [
            ("sender_name", "VARCHAR(100)"),
            ("sender_number", "VARCHAR(20)"),
            ("transaction_id", "VARCHAR(100)")
        ]
        
        for col_name, col_type in cols_to_add:
            try:
                cursor.execute(f"ALTER TABLE payments ADD COLUMN {col_name} {col_type}")
                print(f"Added column: {col_name}")
            except mysql.connector.Error as err:
                if err.errno == 1060: # Missing column error or duplicate column
                    print(f"Column {col_name} already exists.")
                else:
                    print(f"Error adding {col_name}: {err}")
        
        conn.commit()
        print("Payments table updated successfully.")
    except Exception as e:
        print(f"Update failed: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_table()
