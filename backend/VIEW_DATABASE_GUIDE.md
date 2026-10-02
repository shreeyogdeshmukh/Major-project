# 📊 How to View Your Database

There are **4 easy ways** to view your database. Choose the method that works best for you!

## 🗄️ Database Location

Your database is stored at:
```
Major project/backend/database.db
```

---

## Method 1: Web Interface (Easiest) 🌐

**Best for:** Quick viewing in your browser

1. **Start your Flask app:**
   ```bash
   cd "Major project/backend"
   python app.py
   ```

2. **Sign in** (if not already):
   - Go to: http://localhost:5000/login

3. **View database info:**
   - Go to: http://localhost:5000/db-info
   - You'll see:
     - Database path and size
     - All tables
     - User count, preferences count, history count

**Screenshot:** You'll see a nice web page with all database information!

---

## Method 2: Python Script (Most Detailed) 🐍

**Best for:** Complete database contents with all details

1. **Run the enhanced viewer script:**
   ```bash
   cd "Major project/backend"
   python view_database.py
   ```

2. **What you'll see:**
   - All users with IDs, names, emails
   - All user preferences (dietary preferences, favorite ingredients, allergies)
   - All recipe history (who searched for what recipes and when)
   - Database statistics and summary

**Example Output:**
```
======================================================================
  DATABASE VIEWER
======================================================================

📍 Database Location: D:\College Projects\Project copy\Major project\backend\database.db
✅ Database Exists: True
📊 Database Size: 8,192 bytes (8.00 KB / 0.01 MB)

📋 Tables Found: 3
   • user_history
   • user_preferences
   • users

======================================================================
  USERS TABLE
======================================================================

Total Users: 2

All Users:
----------------------------------------------------------------------
ID    Name                           Email                             
----------------------------------------------------------------------
1     John Doe                       john@example.com                  
2     Jane Smith                     jane@example.com                 
```

---

## Method 3: SQLite Command Line 💻

**Best for:** Advanced users who want to run custom SQL queries

1. **Open terminal/command prompt**

2. **Navigate to backend folder:**
   ```bash
   cd "Major project/backend"
   ```

3. **Open SQLite:**
   ```bash
   sqlite3 database.db
   ```

4. **Useful SQLite commands:**
   ```sql
   -- List all tables
   .tables
   
   -- View users table
   SELECT * FROM users;
   
   -- View user preferences
   SELECT * FROM user_preferences;
   
   -- View recipe history
   SELECT * FROM user_history;
   
   -- View with joins (more readable)
   SELECT u.name, u.email, up.dietary_preference 
   FROM users u 
   LEFT JOIN user_preferences up ON u.id = up.user_id;
   
   -- Exit SQLite
   .exit
   ```

**Note:** If `sqlite3` command is not found, you may need to:
- Install SQLite: https://www.sqlite.org/download.html
- Or use Method 1, 2, or 4 instead

---

## Method 4: SQLite Browser (GUI Tool) 🖥️

**Best for:** Visual database browsing and editing

1. **Download DB Browser for SQLite:**
   - Windows: https://sqlitebrowser.org/dl/
   - Mac: `brew install --cask db-browser-for-sqlite`
   - Linux: Available in most package managers

2. **Open the database:**
   - Launch DB Browser for SQLite
   - Click "Open Database"
   - Navigate to: `Major project/backend/database.db`
   - Click "Open"

3. **Browse your data:**
   - Click on "Browse Data" tab
   - Select a table from the dropdown (users, user_preferences, user_history)
   - View, edit, or export your data!

**Features:**
- Visual table browser
- SQL query editor
- Export data to CSV/JSON
- Edit data directly
- View database structure

---

## 📋 Quick Reference

### Database Tables:

1. **users**
   - `id` - Primary key
   - `name` - User's full name
   - `email` - User's email (unique)
   - `password` - Hashed password (SHA-256)

2. **user_preferences**
   - `id` - Primary key
   - `user_id` - Foreign key to users table
   - `dietary_preference` - veg/non-veg/vegan
   - `favorite_ingredients` - Comma-separated list
   - `allergies` - User's allergies

3. **user_history**
   - `id` - Primary key
   - `user_id` - Foreign key to users table
   - `recipe_name` - Name of the recipe
   - `timestamp` - When the recipe was generated (ISO format)

---

## 🔍 Quick Check Commands

**Check if database exists:**
```bash
cd "Major project/backend"
python -c "import os; print('Exists:', os.path.exists('database.db'))"
```

**View database file size:**
```bash
cd "Major project/backend"
dir database.db  # Windows
ls -lh database.db  # Mac/Linux
```

**Quick user count:**
```bash
cd "Major project/backend"
python -c "import sqlite3; conn = sqlite3.connect('database.db'); print('Users:', conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]); conn.close()"
```

---

## 💡 Tips

- **Database is created automatically** when you first run `app.py`
- **Database file location:** Always in `Major project/backend/database.db`
- **Backup:** Copy `database.db` file to backup your data
- **Reset:** Delete `database.db` to start fresh (it will be recreated)

---

## 🆘 Troubleshooting

**"Database does not exist"**
- Run `python app.py` at least once to create it
- Check you're in the correct directory

**"Permission denied"**
- Make sure you have read/write permissions in the backend folder
- On Windows, run as administrator if needed

**"Module not found: sqlite3"**
- SQLite3 is built into Python, this shouldn't happen
- Try reinstalling Python

---

**Recommended:** Start with **Method 1** (Web Interface) for quick viewing, or **Method 2** (Python Script) for detailed information!
