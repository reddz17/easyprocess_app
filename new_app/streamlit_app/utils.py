import sqlite3
from passlib.hash import pbkdf2_sha256
from datetime import datetime


def create_database(conn, cursor):
    # Create the database tables if they don't exist
    # Connect to the database
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Candidats (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email_address TEXT UNIQUE NOT NULL,
            is_recruiter BOOLEAN NOT NULL,
            profile_picture TEXT,
            cv_path TEXT,
            reset_token TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS JobOffers (
            job_id INTEGER PRIMARY KEY,
            recruiter_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            description TEXT NOT NULL,
            experience TEXT NOT NULL,
            mode TEXT NOT NULL,
            location TEXT NOT NULL,
            FOREIGN KEY (recruiter_id) REFERENCES Candidats (user_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Applications (
            application_id INTEGER PRIMARY KEY,
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            application_status TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES JobOffers (job_id),
            FOREIGN KEY (candidate_id) REFERENCES Candidats (user_id)
        )
    ''')
    # Commit changes and close the database connection
    conn.commit()
    conn.close()

# Helper function to add a user


def add_user(username, email_address, password, is_recruiter):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Candidats WHERE email_address=?",(email_address,))
    existing_user = cursor.fetchone()
    if existing_user:
        return False
    password_hash = pbkdf2_sha256.hash(password)
    cursor.execute('INSERT INTO Candidats (username, password, email_address, is_recruiter) VALUES (?, ?, ?, ?)',
                   (username, password_hash, email_address, is_recruiter))
    conn.commit()
    conn.close()
    return True

# Helper function to save a job offer


def save_job_offer(recruiter_id, title, description, location, experience, mode, company):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO JobOffers (recruiter_id,  title, description, location, experience, mode, company) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (recruiter_id, title, description, location, experience, mode, company))
    conn.commit()
    conn.close()


def change_password(new_hashed_password, user_id):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE Candidats SET password = ? WHERE user_id = ?', (new_hashed_password, user_id))
    conn.commit()
    conn.close


def fetch_user_data(user_id):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT user_id, username, password, email_address, is_recruiter FROM Candidats WHERE user_id = ?', (user_id,))
    return cursor.fetchone()
# Helper function to save a user's profile picture

def fetch_user_data_mail(email):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT user_id FROM Candidats WHERE email_address = ?', (email,))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0] if user_id else None

def save_profile_picture(profile_picture_path, user_id):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE Candidats SET profile_picture = ? WHERE user_id = ?',
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
        'SELECT profile_picture, cv_path FROM Candidats WHERE user_id = ?', (u_id,))
    user_files = cursor.fetchone()
    profile_picture_path = user_files[0]
    cv_path = user_files[1]
    return profile_picture_path, cv_path


def fetch_recruiter_data(recruiter_id):
    conn = sqlite3.connect('recruitment.db')  # Modify the database path if needed
    cursor = conn.cursor()
    # Execute SQL queries to retrieve the recruiter's profile picture and job offer
    cursor.execute("SELECT profile_picture FROM Candidats WHERE user_id = ? and is_recruiter=True", (recruiter_id,))
    profile_picture = cursor.fetchone()[0]
    #cursor.execute("SELECT * FROM JobOffers WHERE recruiter_id = ?", (recruiter_id,))
    #job_offer = cursor.fetchall()
    return profile_picture



# Helper function to save a user's CV path
def authenticate_user(email, password):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT user_id, password, is_recruiter, email_address, username FROM Candidats WHERE email_address = ?', (email,))
    user = cursor.fetchone()
    return user if user and pbkdf2_sha256.verify(password, user[1]) else None


def save_cv_path(cv_path, user_id):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE Candidats SET cv_path = ? WHERE user_id = ?', (cv_path, user_id))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error updating CV path: {e}")
    finally:
        conn.close()


def check_email_exists(new_email):
    # Connect to the SQLite database (replace with your database connection logic)
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    # Execute a query to check if the email exists
    cursor.execute("SELECT COUNT(*) FROM Candidats WHERE email_address = ?", (new_email,))
    count = cursor.fetchone()[0]
    # Close the database connection
    conn.close()
    # If count > 0, the email exists; otherwise, it doesn't
    return count > 0


def get_user_email_from_token(token):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email_address FROM Candidats WHERE reset_token = ?", (token,))
    user = cursor.fetchone()
    if user:
        return user[0]
    return None

def update_user_password(user_email, new_password):
    # Hash the new password before updating it in the database
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    hashed_password = pbkdf2_sha256.hash(new_password)
    cursor.execute("UPDATE Candidats SET password = ? WHERE email_address = ?", (hashed_password, user_email))
    conn.commit()
    conn.close()
    
def update_token_user(user_token,user_email):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Candidats SET reset_token = ? WHERE email_address = ?", (user_token,user_email))
    conn.commit()
    conn.close()