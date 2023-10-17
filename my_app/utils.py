import sqlite3
from passlib.hash import pbkdf2_sha256
from datetime import datetime


def create_database(conn, cursor):
    # Create the database tables if they don't exist
    # Connect to the database
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
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


def change_password(new_hashed_password, user_id):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET password = ? WHERE user_id = ?', (new_hashed_password, user_id))
    conn.commit()


def fetch_user_data(username):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT user_id, username, password, email_address, is_recruiter FROM users WHERE username = ?', (username,))
    return cursor.fetchone()
# Helper function to save a user's profile picture


def save_profile_picture(profile_picture_path, user_id):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE Users SET profile_picture = ? WHERE user_id = ?',
                       (profile_picture_path, user_id))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error updating profile picture: {e}")
    finally:
        conn.close()

def get_uploaded_candidate_files(u_id):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    # Assuming you have a table in your database that stores candidate files
    cursor.execute(
        'SELECT profile_picture, cv_path FROM Users WHERE user_id = ?', (u_id,))
    user_files = cursor.fetchone()
    profile_picture_path = user_files[0]
    cv_path = user_files[1]
    return profile_picture_path, cv_path


# Helper function to save a user's CV path
def authenticate_user(email, password):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT user_id, password, is_recruiter, email_address, username FROM users WHERE email_address = ?', (email,))
    user = cursor.fetchone()
    return user if user and pbkdf2_sha256.verify(password, user[1]) else None


def save_cv_path(cv_path, user_id):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE Users SET cv_path = ? WHERE user_id = ?', (cv_path, user_id))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error updating CV path: {e}")
    finally:
        conn.close()
