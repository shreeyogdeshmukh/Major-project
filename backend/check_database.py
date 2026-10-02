"""
Simple script to check database status and location
Run this script to verify your database is created and see its contents
"""

import os
import sqlite3

# Database path (same as in app.py)
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

print("=" * 60)
print("DATABASE VERIFICATION SCRIPT")
print("=" * 60)
print()

# Check if database exists
print(f"Database Path: {DATABASE}")
print(f"Database Exists: {os.path.exists(DATABASE)}")
print()

if os.path.exists(DATABASE):
    # Get database size
    size_bytes = os.path.getsize(DATABASE)
    size_kb = size_bytes / 1024
    print(f"Database Size: {size_bytes} bytes ({size_kb:.2f} KB)")
    print()
    
    # Connect to database
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables Found: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        print()
        
        # Check users table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"Total Users: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT id, name, email FROM users LIMIT 5")
            users = cursor.fetchall()
            print("\nSample Users (first 5):")
            for user in users:
                print(f"  ID: {user[0]}, Name: {user[1]}, Email: {user[2]}")
        
        # Check user_preferences table
        cursor.execute("SELECT COUNT(*) FROM user_preferences")
        pref_count = cursor.fetchone()[0]
        print(f"\nUser Preferences Records: {pref_count}")
        
        # Check user_history table
        cursor.execute("SELECT COUNT(*) FROM user_history")
        history_count = cursor.fetchone()[0]
        print(f"Recipe History Records: {history_count}")
        
        if history_count > 0:
            cursor.execute("SELECT recipe_name, timestamp FROM user_history ORDER BY timestamp DESC LIMIT 5")
            history = cursor.fetchall()
            print("\nRecent Recipe History (last 5):")
            for item in history:
                print(f"  Recipe: {item[0]}, Time: {item[1]}")
        
        conn.close()
        print()
        print("=" * 60)
        print("Database verification completed successfully!")
        print("=" * 60)
        
    except sqlite3.Error as e:
        print(f"Error reading database: {e}")
else:
    print("Database does not exist yet.")
    print("It will be created automatically when you run the Flask app for the first time.")
    print()
    print("To create the database:")
    print("  1. Run: python app.py")
    print("  2. The database will be created automatically at:", DATABASE)
