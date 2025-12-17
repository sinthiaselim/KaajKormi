import mysql.connector
from mysql.connector import Error

def test_connect():
    print("Attempting to connect with provided credentials (no database specified)...")
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        if conn.is_connected():
            print("SUCCESS: Connection established!")
            print(f"Connected as user: {conn.user}")
            
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            print("\nAvailable Databases:")
            for db in cursor:
                print(db)
            cursor.close()
            conn.close()
            return True
    except Error as e:
        print(f"FAILURE: {e}")
        return False

if __name__ == "__main__":
    test_connect()
