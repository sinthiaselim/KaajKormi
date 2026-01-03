from db import get_db_connection, init_db
import mysql.connector

def reset_schema():
    print("Dropping all tables to apply new schema...")
    conn = get_db_connection()
    if not conn:
        print("Failed to connect.")
        return
        
    cursor = conn.cursor()
    
    # Disable foreign key checks to allow dropping tables in any order
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    tables = ['reviews', 'payments', 'requests', 'workers', 'users']
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"Dropped table {table}")
        except Exception as e:
            print(f"Error dropping {table}: {e}")
            
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Re-initializing database schema...")
    init_db()
    print("Done. Now run seed_data.py")

if __name__ == '__main__':
    reset_schema()
