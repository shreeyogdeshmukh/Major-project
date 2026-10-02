"""
Enhanced Database Viewer Script
Shows all database contents in a readable format
"""

import os
import sqlite3
from datetime import datetime

# Database path (same as in app.py)
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

# Set UTF-8 encoding for Windows compatibility
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def view_database():
    """View all database contents"""
    print_section("DATABASE VIEWER")
    
    # Check if database exists
    print(f"\n📍 Database Location: {DATABASE}")
    print(f"✅ Database Exists: {os.path.exists(DATABASE)}")
    
    if not os.path.exists(DATABASE):
        print("\n❌ Database does not exist yet!")
        print("   It will be created automatically when you run the Flask app.")
        return
    
    # Get database size
    size_bytes = os.path.getsize(DATABASE)
    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024
    print(f"📊 Database Size: {size_bytes:,} bytes ({size_kb:.2f} KB / {size_mb:.2f} MB)")
    
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print(f"\n📋 Tables Found: {len(tables)}")
        for table in tables:
            print(f"   • {table[0]}")
        
        # ========== USERS TABLE ==========
        print_section("USERS TABLE")
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        print(f"\nTotal Users: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT id, name, email FROM users ORDER BY id")
            users = cursor.fetchall()
            print("\nAll Users:")
            print("-" * 70)
            print(f"{'ID':<5} {'Name':<30} {'Email':<35}")
            print("-" * 70)
            for user in users:
                print(f"{user['id']:<5} {user['name']:<30} {user['email']:<35}")
        else:
            print("\nNo users registered yet.")
        
        # ========== USER PREFERENCES TABLE ==========
        print_section("USER PREFERENCES TABLE")
        cursor.execute("SELECT COUNT(*) as count FROM user_preferences")
        pref_count = cursor.fetchone()['count']
        print(f"\nTotal Preferences Records: {pref_count}")
        
        if pref_count > 0:
            cursor.execute("""
                SELECT up.id, up.user_id, u.name as user_name, u.email,
                       up.dietary_preference, up.favorite_ingredients, up.allergies
                FROM user_preferences up
                LEFT JOIN users u ON up.user_id = u.id
                ORDER BY up.id
            """)
            prefs = cursor.fetchall()
            print("\nAll User Preferences:")
            print("-" * 70)
            for pref in prefs:
                print(f"\n  Preference ID: {pref['id']}")
                print(f"  User: {pref['user_name']} ({pref['email']}) - ID: {pref['user_id']}")
                print(f"  Dietary Preference: {pref['dietary_preference'] or 'Not set'}")
                print(f"  Favorite Ingredients: {pref['favorite_ingredients'] or 'Not set'}")
                print(f"  Allergies: {pref['allergies'] or 'None'}")
        else:
            print("\nNo user preferences set yet.")
        
        # ========== USER HISTORY TABLE ==========
        print_section("RECIPE HISTORY TABLE")
        cursor.execute("SELECT COUNT(*) as count FROM user_history")
        history_count = cursor.fetchone()['count']
        print(f"\nTotal History Records: {history_count}")
        
        if history_count > 0:
            cursor.execute("""
                SELECT uh.id, uh.user_id, u.name as user_name, uh.recipe_name, uh.timestamp
                FROM user_history uh
                LEFT JOIN users u ON uh.user_id = u.id
                ORDER BY uh.timestamp DESC
                LIMIT 50
            """)
            history = cursor.fetchall()
            print("\nRecent Recipe History (Last 50):")
            print("-" * 70)
            print(f"{'ID':<5} {'User':<25} {'Recipe Name':<35} {'Timestamp':<20}")
            print("-" * 70)
            for item in history:
                # Format timestamp for readability
                try:
                    dt = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_time = item['timestamp']
                
                print(f"{item['id']:<5} {item['user_name']:<25} {item['recipe_name']:<35} {formatted_time:<20}")
        else:
            print("\nNo recipe history yet.")
        
        # ========== SUMMARY ==========
        print_section("SUMMARY")
        print(f"\n📊 Database Statistics:")
        print(f"   • Total Users: {user_count}")
        print(f"   • User Preferences: {pref_count}")
        print(f"   • Recipe History Records: {history_count}")
        print(f"   • Database Size: {size_kb:.2f} KB")
        
        conn.close()
        print("\n✅ Database viewing completed!")
        
    except sqlite3.Error as e:
        print(f"\n❌ Error reading database: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    view_database()
