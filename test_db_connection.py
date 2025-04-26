#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error

def test_connection():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host="localhost",
            database="apache_db",
            user="jul",
            password="J1GtOVw7og3RtgzJSroLiYXFLmeScjGOcMt",
            port=3306
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL server version: {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"Connected to database: {record[0]}")

            # Check if tables exist
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'apache_db' 
                AND table_name IN ('temperatures', 'cycle_counter');
            """)
            table_count = cursor.fetchone()[0]
            print(f"Tables found: {table_count} of 2")
            
            if table_count < 2:
                print("Creating missing tables...")
                # Create table for temperatures if it doesn't exist
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS temperatures (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    day_number INT NOT NULL,
                    temperature FLOAT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INT DEFAULT 1
                )
                """)
                
                # Create table for day counter if it doesn't exist
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS cycle_counter (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    day_counter INT NOT NULL DEFAULT 1,
                    user_id INT DEFAULT 1,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
                """)
                
                # Insert initial values if necessary
                cursor.execute("SELECT COUNT(*) FROM cycle_counter WHERE user_id = 1")
                count = cursor.fetchone()[0]
                if count == 0:
                    cursor.execute("INSERT INTO cycle_counter (day_counter, user_id) VALUES (1, 1)")
                    connection.commit()
                    print("Cycle counter initialized")
                
                print("Tables created successfully")
            
            return True
            
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return False
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("The database connection is working correctly.")
    else:
        print("Could not establish database connection.") 