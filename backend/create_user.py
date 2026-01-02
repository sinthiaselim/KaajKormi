import mysql.connector
from mysql.connector import Error

def create_user():
    try:
        # Connect as root
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        if conn.is_connected():
            cursor = conn.cursor()
            
            # Create user if not exists
            # Note: We use IF NOT EXISTS to avoid errors if it was just a password mismatch
            cursor.execute("CREATE USER IF NOT EXISTS 'FARABI'@'localhost' IDENTIFIED BY '';")
            print("User 'FARABI' created (or already exists).")
            
            # Grant privileges
            cursor.execute("GRANT ALL PRIVILEGES ON *.* TO 'FARABI'@'localhost' WITH GRANT OPTION;")
            print("Privileges granted.")
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
    except Error as e:
        print(f"Error creating user: {e}")
        return False

if __name__ == '__main__':
    create_user()
