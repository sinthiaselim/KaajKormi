import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Establish a connection to the database."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='sinthiaselim',
            password='Shoily123@',
            database='kaajkormi_db'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    """Initialize the database with schema."""
    conn = get_db_connection()
    if conn is None:
        # Try connecting without database to create it
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='sinthiaselim',
                password='Shoily123@'
            )
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS kaajkormi_db")
            print("Database 'kaajkormi_db' created or already exists.")
            conn.database = 'kaajkormi_db'
        except Error as e:
            print(f"Error creating database: {e}")
            return

    cursor = conn.cursor()
    
    # Read schema.sql
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(base_dir, 'schema.sql')
    try:
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        # Execute schema commands
        # Split by ';' to execute individual statements
        commands = schema.split(';')
        for command in commands:
            if command.strip():
                cursor.execute(command)
        
        conn.commit()
        print("Database schema initialized.")
    except Exception as e:
        print(f"Error initializing schema: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    init_db()
