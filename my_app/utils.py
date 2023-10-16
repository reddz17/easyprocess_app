import sqlite3
from passlib.hash import pbkdf2_sha256
from datetime import datetime

# Connect to the database
conn = sqlite3.connect('recruitment.db')
cursor = conn.cursor()

def create_database(conn,cursor):
    # Create the database tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email_address TEXT NOT NULL,
            is_recruiter BOOLEAN NOT NULL,
            profile_picture TEXT,
            cv_path TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS JobOffers (
            job_id INTEGER PRIMARY KEY,
            recruiter_id INTEGER NOT NULL,
            offer_path TEXT NOT NULL,
            name_offer TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            salary REAL,
            FOREIGN KEY (recruiter_id) REFERENCES Users (user_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Applications (
            application_id INTEGER PRIMARY KEY,
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            application_status TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES JobOffers (job_id),
            FOREIGN KEY (candidate_id) REFERENCES Users (user_id)
        )
    ''')
    # Commit changes and close the database connection
    conn.commit()
    conn.close()

# Helper function to add a user
def add_user(username, email_address, password, is_recruiter):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    password_hash = pbkdf2_sha256.hash(password)
    cursor.execute('INSERT INTO Users (username, password, email_address, is_recruiter) VALUES (?, ?, ?, ?)',
                   (username, password_hash, email_address, is_recruiter))
    conn.commit()
    conn.close()

# Helper function to save a job offer
def save_job_offer(recruiter_id, offer_path, name_offer, title, description, location, salary):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO JobOffers (recruiter_id, offer_path, name_offer, title, description, location, salary) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (recruiter_id, offer_path, name_offer, title, description, location, salary))
    conn.commit()
    conn.close()

# Helper function to save a user's profile picture
def save_profile_picture(username, profile_picture_path):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE Users SET profile_picture = ? WHERE username = ?', (profile_picture_path, username))
    conn.commit()
    conn.close()

# Helper function to save a user's CV path
def save_cv_path(username, cv_path):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE Users SET cv_path = ? WHERE username = ?', (cv_path, username))
    conn.commit()
    conn.close()

# Helper function to create a user profile
def create_user_profile(new_name, new_email, new_id, profile_picture, cv_file):
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_profile = {
        "Nom": new_name,
        "Email": new_email,
        "ID Utilisateur": new_id,
        "Date d'inscription": current_datetime,
        "Dernière Connexion": None,
        "Photo de Profil": profile_picture,
        "CV (PDF)": cv_file,
    }
    user_profiles.append(new_profile)
