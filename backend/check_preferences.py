import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

print("=" * 70)
print("USER_PREFERENCES TABLE INFORMATION")
print("=" * 70)

if not os.path.exists(DATABASE):
    print("\nDatabase does not exist yet!")
    exit()

conn = sqlite3.connect(DATABASE)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get table structure
print("\n1. TABLE STRUCTURE:")
print("-" * 70)
cursor.execute("PRAGMA table_info(user_preferences)")
columns = cursor.fetchall()
for col in columns:
    nullable = "NULL" if col[3] == 0 else "NOT NULL"
    default = f" DEFAULT {col[4]}" if col[4] else ""
    print(f"  • {col[1]:<25} {col[2]:<15} {nullable}{default}")

# Get all data
print("\n2. CURRENT DATA:")
print("-" * 70)
cursor.execute("""
    SELECT up.*, u.name as user_name, u.email 
    FROM user_preferences up
    LEFT JOIN users u ON up.user_id = u.id
    ORDER BY up.id
""")
prefs = cursor.fetchall()

if len(prefs) == 0:
    print("  No user preferences set yet.")
    print("\n  Users can set preferences via:")
    print("    - API: POST /preferences")
    print("    - Or through the frontend (if implemented)")
else:
    for pref in prefs:
        print(f"\n  Preference ID: {pref['id']}")
        print(f"  User ID: {pref['user_id']} ({pref['user_name']} - {pref['email']})")
        print(f"  Dietary Preference: {pref['dietary_preference'] or '(not set)'}")
        print(f"  Favorite Ingredients: {pref['favorite_ingredients'] or '(not set)'}")
        print(f"  Allergies: {pref['allergies'] or '(none)'}")

# Count
cursor.execute("SELECT COUNT(*) as count FROM user_preferences")
count = cursor.fetchone()['count']
print(f"\n3. SUMMARY:")
print("-" * 70)
print(f"  Total Preference Records: {count}")

conn.close()

print("\n" + "=" * 70)
print("WHAT ARE USER PREFERENCES?")
print("=" * 70)
print("""
User Preferences allow users to personalize their recipe recommendations:

1. DIETARY_PREFERENCE:
   - Options: 'veg', 'non-veg', 'vegan'
   - Used to filter recipes based on dietary restrictions
   - Example: If set to 'veg', only vegetarian recipes will be suggested

2. FAVORITE_INGREDIENTS:
   - Comma-separated list of favorite ingredients
   - Used to prioritize recipes with these ingredients
   - Example: "tomato, onion, garlic, paneer"

3. ALLERGIES:
   - List of ingredients the user is allergic to
   - CRITICAL: Recipes will exclude these ingredients
   - Example: "peanuts, shellfish, dairy"

HOW IT WORKS:
- When a user generates recipes, the AI considers these preferences
- The preferences are added to the AI prompt to personalize results
- Allergies are strictly enforced - recipes won't include allergic ingredients

TO SET PREFERENCES:
- API Endpoint: POST http://localhost:5000/preferences
- Requires authentication (user must be logged in)
- Send JSON: {
    "dietary_preference": "veg",
    "favorite_ingredients": "tomato, onion, paneer",
    "allergies": "peanuts"
  }
""")
