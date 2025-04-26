#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="J1GtOVw7og3RtgzJSroLiYXFLmeScjGOcMt"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS apache_db")
            print("Database 'apache_db' created or already exists")
            
            # Use the database
            cursor.execute("USE apache_db")
            
            # Create user if it doesn't exist and grant permissions
            try:
                cursor.execute("CREATE USER IF NOT EXISTS 'jul'@'localhost' IDENTIFIED BY 'J1GtOVw7og3RtgzJSroLiYXFLmeScjGOcMt'")
                cursor.execute("GRANT ALL PRIVILEGES ON apache_db.* TO 'jul'@'localhost'")
                cursor.execute("FLUSH PRIVILEGES")
                print("User 'jul' created and permissions assigned")
            except Error as e:
                print(f"Error creating user: {e}")
            
            # Create table for temperatures
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS temperature_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                day_number INT NOT NULL,
                temperature FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT DEFAULT 1
            )
            """)
            print("Table 'temperature_data' created or already exists")
            
            # Create table for day counter
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cycle_counter (
                id INT AUTO_INCREMENT PRIMARY KEY,
                day_counter INT NOT NULL DEFAULT 1,
                user_id INT DEFAULT 1,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """)
            print("Table 'cycle_counter' created or already exists")
            
            # Insert initial values if necessary
            cursor.execute("SELECT COUNT(*) FROM cycle_counter WHERE user_id = 1")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute("INSERT INTO cycle_counter (day_counter, user_id) VALUES (1, 1)")
                print("Cycle counter initialized")
            
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    create_database() 