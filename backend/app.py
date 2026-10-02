from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from groq import Groq
from flask_cors import CORS
import os
import json
import sqlite3
import hashlib
from datetime import datetime
from urllib.parse import quote_plus
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
# Frontend URL - change this if your frontend runs on a different port
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
# Enable CORS with credentials for session support
CORS(app, supports_credentials=True, origins=[FRONTEND_URL, "http://localhost:5000", "http://127.0.0.1:5000"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# Groq retired llama-3.3-70b-versatile; use a currently available chat model
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# Database configuration
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

# Database connection function
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database tables
def init_db():
    """Create database tables if they don't exist"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # User preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dietary_preference TEXT,
            favorite_ingredients TEXT,
            allergies TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # User history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recipe_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Favourite recipes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favourite_recipes (
            favourite_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recipe_id TEXT NOT NULL,
            recipe_name TEXT NOT NULL,
            recipe_image TEXT,
            recipe_data TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, recipe_id)
        )
    ''')
    
    # Add recipe_data column if it doesn't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE favourite_recipes ADD COLUMN recipe_data TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Password hashing function
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Authentication decorator
def login_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

ALL_INGREDIENTS = [
    'Rice', 'Ridge Gourd', 'Ribeye steak', 'Raspberry', 'Ricotta', 'Radish', 'Ribs',
    'Tomato', 'Onion', 'Potato', 'Garlic', 'Chili', 'Turmeric', 'Coriander', 'Cumin', 'Ginger', 'Spinach', 'Paneer', 'Lentils'
]

# Authentication Routes

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Sign up route - GET shows form, POST processes registration"""
    if request.method == "GET":
        return render_template("signup.html")
    
    data = request.get_json() if request.is_json else request.form
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    
    if not name or not email or not password:
        if request.is_json:
            return jsonify({"error": "All fields are required"}), 400
        return render_template("signup.html", error="All fields are required")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        if request.is_json:
            return jsonify({"error": "Email already registered"}), 400
        return render_template("signup.html", error="Email already registered")
    
    # Hash password and insert user
    hashed_password = hash_password(password)
    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (name, email, hashed_password)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    if request.is_json:
        return jsonify({"message": "User registered successfully", "user_id": user_id}), 201
    
    # For form submission, redirect to frontend login page
    return redirect(f"{FRONTEND_URL}?signup=success")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login route - GET shows form, POST processes authentication"""
    if request.method == "GET":
        return render_template("login.html")
    
    data = request.get_json() if request.is_json else request.form
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    
    if not email or not password:
        if request.is_json:
            return jsonify({"error": "Email and password are required"}), 400
        return render_template("login.html", error="Email and password are required")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check user credentials
    hashed_password = hash_password(password)
    cursor.execute(
        "SELECT id, name, email FROM users WHERE email = ? AND password = ?",
        (email, hashed_password)
    )
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        if request.is_json:
            return jsonify({"error": "Invalid email or password"}), 401
        return render_template("login.html", error="Invalid email or password")
    
    # Create session
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    
    if request.is_json:
        return jsonify({
            "message": "Login successful",
            "user_id": user['id'],
            "user_name": user['name']
        }), 200
    
    # For form submission, redirect to frontend recipe page
    return redirect(FRONTEND_URL)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Logout route - clears session"""
    session.clear()
    if request.is_json:
        return jsonify({"message": "Logged out successfully"}), 200
    # Redirect to frontend after logout
    return redirect(FRONTEND_URL)

@app.route("/check-auth", methods=["GET"])
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        return jsonify({
            "authenticated": True,
            "user_id": session.get('user_id'),
            "user_name": session.get('user_name'),
            "user_email": session.get('user_email')
        }), 200
    return jsonify({"authenticated": False}), 200

@app.route("/db-info", methods=["GET"])
def db_info():
    """Get database information - supports both JSON API and HTML view"""
    db_path = DATABASE
    db_exists = os.path.exists(db_path)
    
    info = {
        "database_path": db_path,
        "database_exists": db_exists,
        "database_size": None,
        "database_size_kb": None,
        "tables": [],
        "user_count": 0,
        "preferences_count": 0,
        "history_count": 0
    }
    
    if db_exists:
        size_bytes = os.path.getsize(db_path)
        info["database_size"] = size_bytes
        info["database_size_kb"] = round(size_bytes / 1024, 2)
        
        # Get table info
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        info["tables"] = [table['name'] for table in tables]
        
        # Get counts
        cursor.execute("SELECT COUNT(*) as count FROM users")
        info["user_count"] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM user_preferences")
        info["preferences_count"] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM user_history")
        info["history_count"] = cursor.fetchone()['count']
        
        conn.close()
    
    # Return HTML if requested via browser, JSON for API
    if request.headers.get('Accept', '').find('text/html') != -1:
        return render_template("db_info.html")
    
    return jsonify(info), 200

@app.route("/", methods=["GET"])
def home():
    """Home page - serves frontend recipe page if authenticated"""
    if 'user_id' not in session:
        return redirect(url_for("login"))
    
    # Serve the frontend index.html
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public')
    index_path = os.path.join(frontend_dir, 'index.html')
    
    if os.path.exists(index_path):
        # Read and return the frontend HTML
        with open(index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    else:
        # Fallback to backend template
        return render_template("index.html", user_name=session.get('user_name'))

@app.route("/generate", methods=["POST"])
def generate_recipe():
    data = request.get_json()
    ingredients = data.get("ingredients", "")
    user_id = session.get('user_id')  # Optional - will be None if not logged in

    if not ingredients:
        return jsonify({"error": "Please provide ingredients"}), 400

    # Get user preferences only if logged in
    preference_context = ""
    if user_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT dietary_preference, favorite_ingredients, allergies FROM user_preferences WHERE user_id = ?",
            (user_id,)
        )
        pref = cursor.fetchone()
        conn.close()
        
        # Build personalized prompt with user preferences
        if pref:
            dietary_pref = pref['dietary_preference']
            favorite_ing = pref['favorite_ingredients']
            allergies = pref['allergies']
            
            if dietary_pref:
                preference_context += f" Dietary preference: {dietary_pref}."
            if favorite_ing:
                preference_context += f" User's favorite ingredients: {favorite_ing}."
            if allergies:
                preference_context += f" IMPORTANT: User has allergies to: {allergies}. Do NOT include these ingredients in any recipe."

    prompt = (
        "You are a master chef. Given the ingredients, propose 4 diverse recipes."
        f"{preference_context} "
        "Return STRICT JSON with this exact shape: {\n"
        "  \"recipes\": [\n"
        "    {\n"
        "      \"title\": string,\n"
        "      \"ingredients\": [string],\n"
        "      \"instructions\": [string]  // 10-14 detailed, sequential steps with times/temps/cues\n"
        "    }\n"
        "  ]\n"
        "}. Ensure between 3 and 4 items, realistic ingredient lists, and granular steps that are easy to follow. Ingredients: "
        f"{ingredients}."
    )

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a master chef who responds in strict JSON when asked."},
                {"role": "user", "content": prompt}
            ]
        )
        content = completion.choices[0].message.content or "{}"

        # Parse JSON (with light fallback extraction)
        try:
            data_json = json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                data_json = json.loads(content[start:end+1])
            else:
                return jsonify({"error": "Model did not return valid JSON."}), 500

        recipes = data_json.get("recipes", [])
        if not isinstance(recipes, list):
            return jsonify({"error": "Malformed response: 'recipes' must be a list."}), 500

        enriched = []
        for item in recipes:
            title = str(item.get("title", "Recipe")).strip() or "Recipe"
            ing_list = item.get("ingredients", [])
            steps = item.get("instructions", [])
            if not isinstance(ing_list, list):
                ing_list = [str(ing_list)]
            if not isinstance(steps, list):
                steps = [str(steps)]

            query = quote_plus(f"{title} recipe")
            video_url = f"https://www.youtube.com/results?search_query={query}"

            image_query = quote_plus(f"food {title}")
            image_url = f"https://source.unsplash.com/800x600/?{image_query}"

            enriched.append({
                "title": title,
                "ingredients": [str(x) for x in ing_list if str(x).strip()],
                "instructions": [str(x) for x in steps if str(x).strip()],
                "video_url": video_url,
                "image_url": image_url,
            })

        if len(enriched) < 3:
            return jsonify({"error": "Model returned fewer than 3 recipes. Try again."}), 500

        # Save recipe history to database only if user is logged in
        if user_id:
            conn = get_db()
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            for recipe in enriched[:4]:
                cursor.execute(
                    "INSERT INTO user_history (user_id, recipe_name, timestamp) VALUES (?, ?, ?)",
                    (user_id, recipe['title'], timestamp)
                )
            conn.commit()
            conn.close()

        return jsonify({"recipes": enriched[:4]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/suggest_ingredients", methods=["GET"])
def suggest_ingredients():
    q = (request.args.get("q", "") or "").strip()
    if not q:
        return jsonify([])
    prompt = f"As a smart ingredient suggestion AI, return a JSON array (only a JSON array, not any text) of up to 10 real, common cooking ingredient names that match or are relevant to the word: '{q}'. Only output the JSON array."
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a culinary assistant who only replies with strict arrays of valid ingredient names for suggestions."},
                {"role": "user", "content": prompt}
            ]
        )
        content = completion.choices[0].message.content or "[]"
        import json as pyjson
        suggestions = pyjson.loads(content)
        if isinstance(suggestions, list):
            return jsonify(suggestions[:10])
    except Exception:
        pass
    # Fallback: simple filter
    suggestions = [i for i in ALL_INGREDIENTS if q.lower() in i.lower()][:10]
    return jsonify(suggestions)

# User Preferences Routes

@app.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():
    """Get or update user preferences"""
    user_id = session.get('user_id')
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == "GET":
        # Get user preferences
        cursor.execute(
            "SELECT dietary_preference, favorite_ingredients, allergies FROM user_preferences WHERE user_id = ?",
            (user_id,)
        )
        pref = cursor.fetchone()
        conn.close()
        
        if pref:
            return jsonify({
                "dietary_preference": pref['dietary_preference'],
                "favorite_ingredients": pref['favorite_ingredients'],
                "allergies": pref['allergies']
            })
        return jsonify({
            "dietary_preference": None,
            "favorite_ingredients": None,
            "allergies": None
        })
    
    # POST - Update preferences
    data = request.get_json() if request.is_json else request.form
    dietary_preference = data.get("dietary_preference", "").strip()
    favorite_ingredients = data.get("favorite_ingredients", "").strip()
    allergies = data.get("allergies", "").strip()
    
    # Check if preferences exist
    cursor.execute("SELECT id FROM user_preferences WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute(
            """UPDATE user_preferences 
               SET dietary_preference = ?, favorite_ingredients = ?, allergies = ?
               WHERE user_id = ?""",
            (dietary_preference, favorite_ingredients, allergies, user_id)
        )
    else:
        cursor.execute(
            """INSERT INTO user_preferences (user_id, dietary_preference, favorite_ingredients, allergies)
               VALUES (?, ?, ?, ?)""",
            (user_id, dietary_preference, favorite_ingredients, allergies)
        )
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Preferences updated successfully"}), 200

@app.route("/history", methods=["GET"])
@login_required
def get_history():
    """Get user recipe history"""
    user_id = session.get('user_id')
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT recipe_name, timestamp FROM user_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50",
        (user_id,)
    )
    history = cursor.fetchall()
    conn.close()
    
    return jsonify({
        "history": [
            {"recipe_name": row['recipe_name'], "timestamp": row['timestamp']}
            for row in history
        ]
    })

# Favourite Recipes Routes

@app.route("/favourites", methods=["GET", "POST"])
@login_required
def favourites():
    """Get all favourites or add a new favourite"""
    user_id = session.get('user_id')
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == "GET":
        # Get all favourites for the logged-in user
        cursor.execute(
            """SELECT favourite_id, recipe_id, recipe_name, recipe_image, recipe_data, created_at 
               FROM favourite_recipes 
               WHERE user_id = ? 
               ORDER BY created_at DESC""",
            (user_id,)
        )
        favourites = cursor.fetchall()
        conn.close()
        
        result = []
        for row in favourites:
            fav_data = {
                "favourite_id": row['favourite_id'],
                "recipe_id": row['recipe_id'],
                "recipe_name": row['recipe_name'],
                "recipe_image": row['recipe_image'],
                "created_at": row['created_at']
            }
            # Parse recipe_data if it exists
            if row['recipe_data']:
                try:
                    parsed_data = json.loads(row['recipe_data'])
                    fav_data['recipe_data'] = parsed_data
                except json.JSONDecodeError as e:
                    print(f"Error parsing recipe_data for favourite {row['favourite_id']}: {e}")
                    fav_data['recipe_data'] = None
                except Exception as e:
                    print(f"Unexpected error parsing recipe_data: {e}")
                    fav_data['recipe_data'] = None
            else:
                fav_data['recipe_data'] = None
            result.append(fav_data)
        
        return jsonify({"favourites": result}), 200
    
    # POST - Add a recipe to favourites
    data = request.get_json()
    if not data:
        conn.close()
        return jsonify({"error": "No data provided"}), 400
    
    recipe_id = data.get("recipe_id", "").strip()
    recipe_name = data.get("recipe_name", "").strip()
    recipe_image = data.get("recipe_image", "").strip()
    recipe_data = data.get("recipe_data")  # Full recipe object (ingredients, instructions, etc.)
    
    if not recipe_id or not recipe_name:
        conn.close()
        return jsonify({"error": "recipe_id and recipe_name are required"}), 400
    
    # Check if already favourited (prevent duplicates)
    cursor.execute(
        "SELECT favourite_id FROM favourite_recipes WHERE user_id = ? AND recipe_id = ?",
        (user_id, recipe_id)
    )
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return jsonify({"error": "Recipe already in favourites", "favourite_id": existing['favourite_id']}), 409
    
    # Serialize recipe_data to JSON string if provided
    recipe_data_json = None
    if recipe_data:
        try:
            recipe_data_json = json.dumps(recipe_data)
        except:
            recipe_data_json = None
    
    # Insert new favourite
    timestamp = datetime.now().isoformat()
    try:
        cursor.execute(
            """INSERT INTO favourite_recipes (user_id, recipe_id, recipe_name, recipe_image, recipe_data, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, recipe_id, recipe_name, recipe_image, recipe_data_json, timestamp)
        )
        favourite_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "Recipe added to favourites",
            "favourite_id": favourite_id,
            "recipe_id": recipe_id,
            "recipe_name": recipe_name
        }), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Recipe already in favourites"}), 409
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

@app.route("/favourites/<recipe_id>", methods=["DELETE"])
@login_required
def remove_favourite(recipe_id):
    """Remove a recipe from favourites"""
    user_id = session.get('user_id')
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if favourite exists and belongs to user
    cursor.execute(
        "SELECT favourite_id FROM favourite_recipes WHERE user_id = ? AND recipe_id = ?",
        (user_id, recipe_id)
    )
    favourite = cursor.fetchone()
    
    if not favourite:
        conn.close()
        return jsonify({"error": "Favourite not found"}), 404
    
    # Delete the favourite
    cursor.execute(
        "DELETE FROM favourite_recipes WHERE user_id = ? AND recipe_id = ?",
        (user_id, recipe_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Recipe removed from favourites", "recipe_id": recipe_id}), 200

@app.route("/search", methods=["GET"])
@login_required
def search_recipes():
    """Search recipes by name in favourites and history"""
    user_id = session.get('user_id')
    query = request.args.get("q", "").strip()
    
    if not query or len(query) < 2:
        return jsonify({"results": []}), 200
    
    conn = get_db()
    cursor = conn.cursor()
    results = []
    
    # Search in favourites (has full recipe data)
    cursor.execute(
        """SELECT favourite_id, recipe_id, recipe_name, recipe_image, recipe_data, created_at 
           FROM favourite_recipes 
           WHERE user_id = ? AND recipe_name LIKE ? 
           ORDER BY created_at DESC
           LIMIT 10""",
        (user_id, f"%{query}%")
    )
    favourites = cursor.fetchall()
    
    for fav in favourites:
        recipe_data = None
        if fav['recipe_data']:
            try:
                recipe_data = json.loads(fav['recipe_data'])
            except:
                recipe_data = None
        
        results.append({
            "type": "favourite",
            "recipe_id": fav['recipe_id'],
            "recipe_name": fav['recipe_name'],
            "recipe_image": fav['recipe_image'],
            "recipe_data": recipe_data,
            "source": "favourites"
        })
    
    # Search in history (only has name, no full data)
    cursor.execute(
        """SELECT DISTINCT recipe_name, timestamp 
           FROM user_history 
           WHERE user_id = ? AND recipe_name LIKE ? 
           ORDER BY timestamp DESC 
           LIMIT 10""",
        (user_id, f"%{query}%")
    )
    history = cursor.fetchall()
    
    # Add history results that aren't already in favourites
    import re
    existing_names = {r['recipe_name'] for r in results}
    for hist in history:
        if hist['recipe_name'] not in existing_names:
            # Generate recipe_id from recipe name
            recipe_id = re.sub(r'[^a-z0-9]+', '-', hist['recipe_name'].lower()).strip('-')
            results.append({
                "type": "history",
                "recipe_id": recipe_id,
                "recipe_name": hist['recipe_name'],
                "recipe_image": None,
                "recipe_data": None,
                "source": "history",
                "timestamp": hist['timestamp']
            })
    
    conn.close()
    
    return jsonify({
        "query": query,
        "results": results,
        "count": len(results)
    }), 200

@app.route("/favourites/check/<recipe_id>", methods=["GET"])
@login_required
def check_favourite(recipe_id):
    """Check if a recipe is favourited by the current user"""
    user_id = session.get('user_id')
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT favourite_id FROM favourite_recipes WHERE user_id = ? AND recipe_id = ?",
        (user_id, recipe_id)
    )
    favourite = cursor.fetchone()
    conn.close()
    
    return jsonify({
        "is_favourite": favourite is not None,
        "favourite_id": favourite['favourite_id'] if favourite else None
    }), 200


@app.route("/translate_instructions", methods=["POST"])
def translate_instructions():
    """
    Translate a list of recipe instruction steps into a target language using Groq LLM.
    
    Expects JSON:
    {
        "instructions": [string, ...],  # original English steps
        "target_lang": "en" | "hi" | "mr"
    }
    """
    data = request.get_json() or {}
    instructions = data.get("instructions") or []
    target_lang = (data.get("target_lang") or "en").lower()

    if not isinstance(instructions, list) or not instructions:
        return jsonify({"error": "instructions must be a non-empty list of strings"}), 400

    # Normalise steps to strings and strip empties
    steps = [str(s).strip() for s in instructions if str(s).strip()]
    if not steps:
        return jsonify({"error": "No valid instructions to translate"}), 400

    supported_langs = {"en": "English", "hi": "Hindi", "mr": "Marathi"}
    if target_lang not in supported_langs:
        return jsonify({"error": "Unsupported language code"}), 400

    # For English, just return the original instructions – no translation needed
    if target_lang == "en":
        return jsonify({"instructions": steps}), 200

    target_language_name = supported_langs[target_lang]

    # Build a clean, stable prompt for translation.
    # We only translate (rewrite) the instruction sentences, not the recipe title or ingredient list.
    numbered_source = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
    prompt = (
        f"You are a professional native {target_language_name} culinary writer and translator from India.\n\n"
        f"Task: Rewrite the following numbered cooking instructions from English into {target_language_name}.\n\n"
        f"Style requirements:\n"
        f"- Write as a native {target_language_name} speaker in a polite, instructional recipe tone (clear step-by-step commands).\n"
        f"- Treat this as high-quality native-language rewriting, not literal word-by-word translation.\n"
        f"- Use natural, fluent sentence structure and grammatically correct {target_language_name} that sounds like a native cook.\n"
        f"- Keep verb tense and style consistent across all steps.\n"
        f"- Preserve cooking terminology and measurements accurately, using words and phrases real home cooks use.\n"
        f"- Avoid mixing English words except for ingredient names, brand names, and unavoidable technical terms.\n"
        f"- Do NOT translate ingredient NAMES or recipe titles; when they appear inside a sentence, keep those specific words in English.\n"
        f"- You are rewriting ONLY the instruction sentences, not the ingredient list or recipe title.\n\n"
        f"Output format requirements:\n"
        f"- Keep the output as a JSON object with this exact shape:\n"
        f"  {{\n"
        f"    \"instructions\": [\n"
        f"      \"step 1 in natural {target_language_name}\",\n"
        f"      \"step 2 in natural {target_language_name}\",\n"
        f"      \"... more steps ...\"\n"
        f"    ]\n"
        f"  }}\n"
        f"- The number of items in \"instructions\" MUST match the number of source steps exactly.\n"
        f"- Do NOT include any other keys or text outside this JSON object.\n\n"
        f"Source instructions to translate:\n"
        f"{numbered_source}\n"
    )

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful translator. You ALWAYS respond with STRICT JSON only, "
                        "never with explanations or natural language outside the JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        content = completion.choices[0].message.content or "{}"

        # Parse JSON with light fallback extraction
        try:
            data_json = json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                data_json = json.loads(content[start : end + 1])
            else:
                return jsonify({"error": "Model did not return valid JSON."}), 500

        translated = data_json.get("instructions", [])
        if not isinstance(translated, list):
            return jsonify({"error": "Malformed response: 'instructions' must be a list."}), 500

        # Normalise and ensure we have the same number of steps; if not, fall back to originals
        translated_clean = [str(s).strip() for s in translated if str(s).strip()]
        if len(translated_clean) != len(steps):
            # Preserve UX by not returning partial/mismatched data
            return jsonify({"error": "Translation returned an unexpected number of steps."}), 500

        return jsonify({"instructions": translated_clean}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve frontend static files (CSS, JS, images) - must be last route
@app.route("/<path:filename>")
def serve_frontend_files(filename):
    """Serve frontend static files (CSS, JS, images) - catch-all for static files only"""
    # List of static file extensions
    static_extensions = ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot']
    
    # Only serve files with static extensions
    if any(filename.lower().endswith(ext) for ext in static_extensions):
        frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public')
        file_path = os.path.join(frontend_dir, filename)
        
        # Security: only serve files from the public directory
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                # Verify the file is within the frontend directory
                if os.path.commonpath([os.path.abspath(frontend_dir), os.path.abspath(file_path)]) == os.path.abspath(frontend_dir):
                    return send_from_directory(frontend_dir, filename)
            except ValueError:
                pass  # Paths don't share a common path
    
    # For non-static files or files not found, return 404
    return "File not found", 404

if __name__ == "__main__":
    app.run(port=5000, debug=True)
