from flask import Flask, request, jsonify
import mysql.connector
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config["JWT_SECRET_KEY"] = "your_secret_key"
jwt = JWTManager(app)

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="sleep_meditation"
)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255) UNIQUE,
        password_hash VARCHAR(255)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS sleep_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        sleep_duration FLOAT,
        sleep_quality INT,
        log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS meditation_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        session_type VARCHAR(255),
        duration FLOAT,
        log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
conn.commit()

# User registration
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                   (data["name"], data["email"], hashed_password))
    conn.commit()
    return jsonify({"message": "User registered successfully!"})

# User login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    cursor.execute("SELECT id, password_hash FROM users WHERE email = %s", (data["email"],))
    user = cursor.fetchone()

    if user and bcrypt.check_password_hash(user[1], data["password"]):
        access_token = create_access_token(identity=user[0])
        return jsonify({"access_token": access_token})
    return jsonify({"message": "Invalid credentials"}), 401

# Log sleep data
@app.route("/log/sleep", methods=["POST"])
@jwt_required()
def log_sleep():
    data = request.json
    user_id = get_jwt_identity()
    cursor.execute("INSERT INTO sleep_logs (user_id, sleep_duration, sleep_quality) VALUES (%s, %s, %s)",
                   (user_id, data["sleep_duration"], data["sleep_quality"]))
    conn.commit()
    return jsonify({"message": "Sleep data logged successfully!"})

# Log meditation session
@app.route("/log/meditation", methods=["POST"])
@jwt_required()
def log_meditation():
    data = request.json
    user_id = get_jwt_identity()
    cursor.execute("INSERT INTO meditation_logs (user_id, session_type, duration) VALUES (%s, %s, %s)",
                   (user_id, data["session_type"], data["duration"]))
    conn.commit()
    return jsonify({"message": "Meditation session logged successfully!"})

# Get sleep insights
@app.route("/dashboard/sleep-insights", methods=["GET"])
@jwt_required()
def sleep_insights():
    user_id = get_jwt_identity()
    cursor.execute("SELECT AVG(sleep_quality) as avg_quality, AVG(sleep_duration) as avg_duration FROM sleep_logs WHERE user_id = %s", (user_id,))
    results = cursor.fetchone()
    return jsonify({"average_sleep_quality": results[0], "average_sleep_duration": results[1]})

if __name__ == "__main__":
    app.run(debug=True)
