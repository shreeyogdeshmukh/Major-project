# Favourite Recipes Feature - Implementation Guide

## Overview
This document explains the complete implementation of the "Favourite Recipe" feature for the full-stack web application.

---

## 1. Database Schema Changes

### New Table: `favourite_recipes`

**Location**: `Major project/backend/app.py` (in `init_db()` function)

**Schema**:
```sql
CREATE TABLE IF NOT EXISTS favourite_recipes (
    favourite_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recipe_id TEXT NOT NULL,
    recipe_name TEXT NOT NULL,
    recipe_image TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, recipe_id)
)
```

**Fields Explanation**:
- `favourite_id`: Primary key, auto-increments
- `user_id`: Foreign key linking to `users` table (ensures user-specific favourites)
- `recipe_id`: Unique identifier for the recipe (generated from recipe title)
- `recipe_name`: Display name of the recipe
- `recipe_image`: Optional URL to recipe image
- `created_at`: Timestamp when recipe was favourited
- `UNIQUE(user_id, recipe_id)`: Prevents duplicate favourites for the same user

---

## 2. Backend API Endpoints

### 2.1 GET `/favourites`
**Purpose**: Fetch all favourite recipes for the logged-in user

**Authentication**: Required (`@login_required`)

**Response**:
```json
{
  "favourites": [
    {
      "favourite_id": 1,
      "recipe_id": "spicy-tomato-paneer-soup",
      "recipe_name": "Spicy Tomato and Paneer Soup",
      "recipe_image": "https://...",
      "created_at": "2026-01-16T16:20:12"
    }
  ]
}
```

**Code Location**: `Major project/backend/app.py` (lines ~517-540)

---

### 2.2 POST `/favourites`
**Purpose**: Add a recipe to favourites

**Authentication**: Required (`@login_required`)

**Request Body**:
```json
{
  "recipe_id": "spicy-tomato-paneer-soup",
  "recipe_name": "Spicy Tomato and Paneer Soup",
  "recipe_image": "https://..." // optional
}
```

**Response** (Success - 201):
```json
{
  "message": "Recipe added to favourites",
  "favourite_id": 1,
  "recipe_id": "spicy-tomato-paneer-soup",
  "recipe_name": "Spicy Tomato and Paneer Soup"
}
```

**Response** (Duplicate - 409):
```json
{
  "error": "Recipe already in favourites",
  "favourite_id": 1
}
```

**Code Location**: `Major project/backend/app.py` (lines ~542-600)

**Features**:
- Prevents duplicate favourites (checks before inserting)
- Uses database UNIQUE constraint as backup
- Returns appropriate HTTP status codes

---

### 2.3 DELETE `/favourites/<recipe_id>`
**Purpose**: Remove a recipe from favourites

**Authentication**: Required (`@login_required`)

**URL Parameter**: `recipe_id` (URL-encoded)

**Response** (Success - 200):
```json
{
  "message": "Recipe removed from favourites",
  "recipe_id": "spicy-tomato-paneer-soup"
}
```

**Response** (Not Found - 404):
```json
{
  "error": "Favourite not found"
}
```

**Code Location**: `Major project/backend/app.py` (lines ~602-625)

**Security**: Verifies the favourite belongs to the logged-in user before deletion

---

### 2.4 GET `/favourites/check/<recipe_id>`
**Purpose**: Check if a recipe is favourited by the current user

**Authentication**: Required (`@login_required`)

**Response**:
```json
{
  "is_favourite": true,
  "favourite_id": 1
}
```

**Code Location**: `Major project/backend/app.py` (lines ~627-642)

---

## 3. Frontend Implementation

### 3.1 Favourite Button on Recipe Cards

**Location**: `Major project/frontend/public/script.js` (in `renderRecipes()` function)

**Features**:
- Displays "🤍 Favourite" for non-favourited recipes
- Displays "❤️ Favourited" for favourited recipes
- Only visible when user is authenticated
- Button state updates based on `userFavourites` Set

**Code Snippet**:
```javascript
const recipeId = r.recipe_id || safeTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-');
const isFavourite = userFavourites.has(recipeId);
const favouriteBtnClass = isFavourite ? 'btn-favourite active' : 'btn-favourite';
const favouriteBtnText = isFavourite ? '❤️ Favourited' : '🤍 Favourite';
```

---

### 3.2 State Management

**Location**: `Major project/frontend/public/script.js`

**Variables**:
- `userFavourites`: `Set` object storing favourite recipe IDs
- `currentUserId`: Stores logged-in user's ID
- `isAuthenticated`: Boolean flag for authentication status

**Functions**:
1. **`fetchFavourites()`**: Fetches all favourites from backend on login
2. **`toggleFavourite()`**: Adds/removes favourites via API calls
3. **`updateFavouriteButtons()`**: Updates UI button states
4. **`renderFavourites()`**: Displays favourites in "My Favourites" page

---

### 3.3 My Favourites Page

**Location**: `Major project/frontend/public/index.html`

**Features**:
- Separate section that can be shown/hidden
- "❤️ My Favourites" button in header (visible when logged in)
- "Back to Recipe Generator" button to return to main page
- Displays all user's favourite recipes in card format

**Navigation**:
- `showFavouritesPage()`: Shows favourites, hides main page
- `showMainPage()`: Shows main page, hides favourites

---

### 3.4 CSS Styling

**Location**: `Major project/frontend/public/style.css`

**Styles Added**:
```css
.btn-favourite {
  background: #ffffff;
  color: #ff6a3d;
  border: 2px solid #ff6a3d;
  font-weight: 600;
}
.btn-favourite.active {
  background: linear-gradient(90deg, #ff6a3d, #ff4d6d);
  color: #ffffff;
}
```

---

## 4. Data Flow Explanation

### 4.1 Adding a Favourite

```
User clicks "🤍 Favourite" button
    ↓
Frontend: toggleFavourite() called
    ↓
Frontend: POST request to /favourites
    Body: { recipe_id, recipe_name, recipe_image }
    ↓
Backend: @login_required decorator checks session
    ↓
Backend: Checks for duplicate (user_id + recipe_id)
    ↓
Backend: If not duplicate, INSERT into favourite_recipes table
    ↓
Backend: Returns 201 Created with favourite_id
    ↓
Frontend: Updates userFavourites Set
    ↓
Frontend: Updates button to "❤️ Favourited" (active state)
```

### 4.2 Removing a Favourite

```
User clicks "❤️ Favourited" button
    ↓
Frontend: toggleFavourite() called
    ↓
Frontend: DELETE request to /favourites/<recipe_id>
    ↓
Backend: @login_required decorator checks session
    ↓
Backend: Verifies favourite belongs to user
    ↓
Backend: DELETE from favourite_recipes table
    ↓
Backend: Returns 200 OK
    ↓
Frontend: Removes from userFavourites Set
    ↓
Frontend: Updates button to "🤍 Favourite"
    ↓
Frontend: If on Favourites page, removes card from display
```

### 4.3 Fetching Favourites on Login

```
User logs in
    ↓
Frontend: checkAuthStatus() called
    ↓
Backend: Returns authenticated: true with user_id
    ↓
Frontend: fetchFavourites() called automatically
    ↓
Frontend: GET request to /favourites
    ↓
Backend: SELECT * FROM favourite_recipes WHERE user_id = ?
    ↓
Backend: Returns JSON array of favourites
    ↓
Frontend: Populates userFavourites Set
    ↓
Frontend: All recipe cards show correct favourite state
```

### 4.4 Persistence After Logout/Login

```
User logs out
    ↓
Frontend: Clears userFavourites Set
    ↓
Backend: Session cleared
    ↓
Database: Favourites remain in favourite_recipes table
    ↓
User logs in again
    ↓
Frontend: fetchFavourites() called
    ↓
Backend: Returns all favourites for user_id
    ↓
Frontend: Restores userFavourites Set
    ↓
All favourites are displayed correctly
```

---

## 5. Error Handling

### Backend Error Handling:
- **400 Bad Request**: Missing required fields (recipe_id, recipe_name)
- **401 Unauthorized**: User not authenticated
- **404 Not Found**: Favourite not found when trying to delete
- **409 Conflict**: Duplicate favourite (already exists)
- **500 Internal Server Error**: Database errors

### Frontend Error Handling:
- **Network Errors**: Try-catch blocks with user-friendly alerts
- **API Errors**: Displays error messages from backend
- **Authentication Errors**: Redirects to login page
- **Duplicate Prevention**: Handles 409 status gracefully

---

## 6. Security Features

1. **Authentication Required**: All endpoints use `@login_required` decorator
2. **User Isolation**: Favourites are filtered by `user_id` in all queries
3. **Ownership Verification**: DELETE endpoint verifies favourite belongs to user
4. **SQL Injection Prevention**: Uses parameterized queries (`?` placeholders)
5. **Session Management**: Uses Flask sessions with secure cookies

---

## 7. Testing the Feature

### Test Scenarios:

1. **Add Favourite**:
   - Login → Generate recipes → Click "🤍 Favourite" → Button changes to "❤️ Favourited"

2. **Remove Favourite**:
   - Click "❤️ Favourited" → Button changes to "🤍 Favourite"

3. **View Favourites Page**:
   - Click "❤️ My Favourites" in header → See all favourite recipes

4. **Persistence**:
   - Add favourites → Logout → Login → Favourites are restored

5. **Duplicate Prevention**:
   - Try to favourite same recipe twice → Second attempt shows "already in favourites"

---

## 8. Files Modified/Created

### Backend:
- ✅ `Major project/backend/app.py` - Added table schema and 4 API endpoints

### Frontend:
- ✅ `Major project/frontend/public/script.js` - Added favourite management functions
- ✅ `Major project/frontend/public/index.html` - Added "My Favourites" section
- ✅ `Major project/frontend/public/style.css` - Added favourite button styles

### Database:
- ✅ `Major project/backend/database.db` - New `favourite_recipes` table created

---

## 9. API Endpoints Summary

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/favourites` | Get all user favourites | Yes |
| POST | `/favourites` | Add recipe to favourites | Yes |
| DELETE | `/favourites/<recipe_id>` | Remove recipe from favourites | Yes |
| GET | `/favourites/check/<recipe_id>` | Check if recipe is favourited | Yes |

---

## 10. Recipe ID Generation

Recipe IDs are generated from recipe titles using this logic:
```javascript
const recipeId = r.recipe_id || safeTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-');
```

**Example**:
- "Spicy Tomato and Paneer Soup" → "spicy-tomato-and-paneer-soup"
- "Paneer Tikka Masala" → "paneer-tikka-masala"

This ensures consistent IDs for the same recipe across sessions.

---

## Conclusion

The Favourite Recipes feature is fully implemented with:
- ✅ Database schema with proper constraints
- ✅ RESTful API endpoints with error handling
- ✅ Frontend UI with favourite buttons
- ✅ "My Favourites" page
- ✅ State management and persistence
- ✅ Security and authentication
- ✅ Clean code structure following MVC/API best practices

The feature is ready for use and maintains data integrity across logout/login cycles.
