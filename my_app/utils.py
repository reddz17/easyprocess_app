import sqlite3
from passlib.hash import pbkdf2_sha256
from datetime import datetime


def create_database(conn, cursor):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    # Create the users table

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email_address TEXT NOT NULL,
            is_recruiter BOOLEAN  NOT NULL,
            profile_picture text,
            cv_path text
        )
    ''')

    # Create Job Offers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Job_offers (
            job_id INTEGER PRIMARY KEY,
            recruiter_id INTEGER NOT NULL,
            offer_path TEXT NOT NULL,
            name_offer TEXT NOT NULL
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            salary REAL,
            FOREIGN KEY (recruiter_id) REFERENCES Users (user_id)
        )
    ''')

    # Create Applications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Applications (
            application_id INTEGER PRIMARY KEY,
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            application_status TEXT NOT NULL,
            -- Add other application-specific fields here
            FOREIGN KEY (job_id) REFERENCES JobOffers (job_id),
            FOREIGN KEY (candidate_id) REFERENCES Users (user_id)
        )
    ''')
    # Create other tables (e.g., job listings and applications) if needed
    conn.commit()
    conn.close()

# Helper function to add a user


def add_user(username, email_address, password, is_recruiter, conn, cursor):
    password_hash = pbkdf2_sha256.hash(password)
    cursor.execute('INSERT INTO users (username, password, email_address, is_recruiter) VALUES (?, ?, ?, ?)',
                   (username, password_hash, email_address, is_recruiter))
    conn.commit()


def save_job_offer(recruiter_id, job_offer_path, name_offer, conn, cursor):
    cursor.execute('INSERT INTO job_offers (recruiter_id,offer_path,name_offer) VALUES (?, ?, ?, ?)',
                   (recruiter_id, job_offer_path, name_offer))
    conn.commit()


def save_profile_picture(profile_picture_path, username, conn, cursor):
    cursor.execute('UPDATE users SET profile_picture = ? WHERE username = ?',
                   (profile_picture_path, username))
    conn.commit()


def save_cv_path(cv_path, username, conn, cursor):
    cursor.execute(
        'UPDATE users SET cv_path = ? WHERE username = ?', (cv_path, username))
    conn.commit()


user_profiles = []  # Initialize the user profiles list


def create_user_profile(user_profiles, new_name, new_email, new_id, profile_picture, cv_file, conn, cursor):
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
