"""Update favourite_recipes table to add recipe_data column"""
import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

try:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('ALTER TABLE favourite_recipes ADD COLUMN recipe_data TEXT')
    conn.commit()
    print('Successfully added recipe_data column to favourite_recipes table')
    conn.close()
except sqlite3.OperationalError as e:
    if 'duplicate column' in str(e).lower() or 'already exists' in str(e).lower():
        print('Column recipe_data already exists')
    else:
        print(f'Error: {e}')
except Exception as e:
    print(f'Unexpected error: {e}')
