# Authentication & Database Setup Guide

## 🔐 Sign In / Sign Up Access

### Option 1: Direct Backend Access (Recommended)
1. Start your Flask backend:
   ```bash
   cd "Major project/backend"
   python app.py
   ```

2. Open your browser and go to:
   - **Sign Up**: http://localhost:5000/signup
   - **Sign In**: http://localhost:5000/login
   - **Home**: http://localhost:5000/

### Option 2: Frontend Integration
The frontend (`Major project/frontend/public/index.html`) now has Sign In/Sign Up buttons in the top-right corner that will redirect you to the backend authentication pages.

**Note**: For the frontend to work with authentication:
- Make sure your backend is running on `http://localhost:5000`
- The frontend should be served from `http://localhost:3000` (or similar) for CORS to work properly
- Or use the backend's home page directly at `http://localhost:5000/`

## 📊 Database Location & Verification

### Database Location
The database file is stored at:
```
Major project/backend/database.db
```

### Verify Database (3 Methods)

#### Method 1: Web Interface (Easiest)
1. Start your Flask app: `python app.py`
2. Make sure you're logged in
3. Visit: http://localhost:5000/db-info
4. You'll see all database information including:
   - Database path
   - Whether it exists
   - Database size
   - All tables
   - User count, preferences count, history count

#### Method 2: Python Script
Run the verification script:
```bash
cd "Major project/backend"
python check_database.py
```

This will show:
- Database path
- Whether database exists
- Database size
- All tables
- Sample data (users, preferences, history)

#### Method 3: API Endpoint
Call the API endpoint:
```bash
curl http://localhost:5000/db-info
```

Or visit in browser: http://localhost:5000/db-info

### Database Structure

The database contains 3 tables:

1. **users**
   - `id` (PRIMARY KEY)
   - `name` (TEXT)
   - `email` (TEXT, UNIQUE)
   - `password` (TEXT, SHA-256 hashed)

2. **user_preferences**
   - `id` (PRIMARY KEY)
   - `user_id` (FOREIGN KEY → users.id)
   - `dietary_preference` (TEXT: veg/non-veg/vegan)
   - `favorite_ingredients` (TEXT)
   - `allergies` (TEXT)

3. **user_history**
   - `id` (PRIMARY KEY)
   - `user_id` (FOREIGN KEY → users.id)
   - `recipe_name` (TEXT)
   - `timestamp` (TEXT, ISO format)

## 🚀 Quick Start

1. **Start Backend**:
   ```bash
   cd "Major project/backend"
   python app.py
   ```

2. **Create Account**:
   - Go to http://localhost:5000/signup
   - Fill in name, email, password
   - Click "Sign Up"

3. **Sign In**:
   - Go to http://localhost:5000/login
   - Enter your email and password
   - Click "Sign In"

4. **Use Recipe Generator**:
   - After signing in, you can use the recipe generation API
   - All recipes will be saved to your history

5. **Check Database**:
   - Visit http://localhost:5000/db-info
   - Or run `python check_database.py`

## 🔧 Troubleshooting

### Database not created?
- The database is created automatically when you first run `app.py`
- Make sure you have write permissions in the `backend` directory
- Check the console for any error messages

### Can't see Sign In/Sign Up buttons?
- Make sure you're accessing the correct URL
- If using frontend, ensure backend is running on port 5000
- Try accessing backend directly: http://localhost:5000/signup

### Authentication not working?
- Check browser console for CORS errors
- Make sure `credentials: 'include'` is set in fetch calls
- Verify backend CORS settings allow your frontend origin

## 📝 Notes

- Passwords are hashed using SHA-256 before storage
- Sessions are stored server-side using Flask sessions
- Database is SQLite, stored as a single file (`database.db`)
- All API endpoints require authentication except `/signup`, `/login`, and `/check-auth`
