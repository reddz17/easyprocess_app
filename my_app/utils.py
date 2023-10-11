import sqlite3
from passlib.hash import pbkdf2_sha256
from datetime import datetime


def create_database():
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()

    # Create the users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            is_recruiter INTEGER NOT NULL
        )
    ''')

    # Create other tables (e.g., job listings and applications) if needed

    conn.commit()
    conn.close()

# Create a SQLite database
# conn = sqlite3.connect('recruitment.db')
# cursor = conn.cursor()


# Helper function to add a user
def add_user(username, password, is_recruiter):
    password_hash = pbkdf2_sha256.hash(password)
    cursor.execute('INSERT INTO users (username, password, is_recruiter) VALUES (?, ?, ?)', (username, password_hash, is_recruiter))
    conn.commit()


def create_user_profile(user_profiles, new_name, new_email, new_id, profile_picture, cv_file):
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_profile = {
        "Nom": new_name,
        "Email": new_email,
        "ID Utilisateur": new_id,
        "Date d inscription": current_datetime,
        "Dernière Connexion": None,
        "Photo de Profil": profile_picture,
        "CV (PDF)": cv_file,
    }
    user_profiles.append(new_profile)
