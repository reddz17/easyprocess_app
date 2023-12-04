import os
import sqlite3
from passlib.hash import pbkdf2_sha256


# Helper function to save a user's CV path
def authenticate_user(email, password):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT user_id, password, is_recruiter, email_address, username FROM Users WHERE email_address = ?', (email,))
    user = cursor.fetchone()
    return user if user and pbkdf2_sha256.verify(password, user[1]) else None


def update_user_data(user_id, profile_picture, cv):
    if profile_picture:
        profile_picture_path = os.path.join(
            f"{os.getenv('profile_path')}{user_id}.jpg")
        os.makedirs(os.path.dirname(
            profile_picture_path), exist_ok=True)
        with open(profile_picture_path, "wb") as f:
            f.write(profile_picture.read())
        save_profile_picture(profile_picture_path, user_id)
    if cv:
        cv_path = os.path.join(
            f"{os.getenv('cv_path')}{user_id}_cv.pdf")
        os.makedirs(os.path.dirname(cv_path), exist_ok=True)
        with open(cv_path, "wb") as f:
            f.write(cv.read())
        save_cv_path(cv_path, user_id)

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


def add_user(username, email_address, password, is_recruiter):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Users WHERE email_address=?",(email_address,))
    existing_user = cursor.fetchone()
    if existing_user:
        return False
    password_hash = pbkdf2_sha256.hash(password)
    cursor.execute('INSERT INTO Users (username, password, email_address, is_recruiter) VALUES (?, ?, ?, ?)',
                   (username, password_hash, email_address, is_recruiter))
    conn.commit()
    conn.close()
    return True



def fetch_user_data(user_id):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT user_id, username, password, email_address, is_recruiter, profile_title, experiences FROM Users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()
    if user_data is None:
        # Handle the case when the user is not found
        print(f"User with ID {user_id} not found.")
        return None  # You can return a default value or raise an exception if needed
    return user_data


def update_user_title_profile(user_id, updated_profile_title, updated_email, updated_username, updated_experience):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    # Update profile title
    cursor.execute("UPDATE Users SET profile_title = ? WHERE user_id = ?", (updated_profile_title, user_id))
    # Update email
    cursor.execute("UPDATE Users SET email_address = ? WHERE user_id = ?", (updated_email, user_id))
    # Update username
    cursor.execute("UPDATE Users SET username = ? WHERE user_id = ?", (updated_username, user_id))
    # Update experiences
    cursor.execute("UPDATE Users SET experiences = ? WHERE user_id = ?", (updated_experience, user_id))
    # Commit changes and close the connection
    conn.commit()
    conn.close()

def update_candidat_title_profile(user_id, updated_email, updated_username):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    # Update email
    cursor.execute("UPDATE Users SET email_address = ? WHERE user_id = ?", (updated_email, user_id))
    # Update username
    cursor.execute("UPDATE Users SET username = ? WHERE user_id = ?", (updated_username, user_id))
    # Commit changes and close the connection
    conn.commit()
    conn.close()

def update_user_password(user_email, new_password):
    # Hash the new password before updating it in the database
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    hashed_password = pbkdf2_sha256.hash(new_password)
    cursor.execute("UPDATE Users SET password = ? WHERE email_address = ?", (hashed_password, user_email))
    conn.commit()
    conn.close()


def get_cv_path(user_id):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT cv_path FROM Users WHERE user_id = ?',(user_id,))
        cv_path = cursor.fetchone()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error updating CV path: {e}")
    finally:
        conn.close()
    return cv_path[0]

def check_email_exists(new_email):
    # Connect to the SQLite database (replace with your database connection logic)
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    # Execute a query to check if the email exists
    cursor.execute("SELECT COUNT(*) FROM Users WHERE email_address = ?", (new_email,))
    count = cursor.fetchone()[0]
    # Close the database connection
    conn.close()
    # If count > 0, the email exists; otherwise, it doesn't
    return count > 0


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



def applied_offer(user_id):
    conn = sqlite3.connect('recruitment.db')  # Modify the database path if needed
    cursor = conn.cursor()
    # Construisez la requête SQL en fonction du terme de recherche
    cursor.execute("""SELECT a.job_id,a.job_title, a.cv_path,a.application_status,
                   j.company, j.description 
                   FROM Applications a, JobOffers j 
                   WHERE candidate_id = ? and a.job_id = j.job_id""", (user_id,))
    # Exécutez la requête SQL pour récupérer les offres d'emploi
    try:
        offers_applied = cursor.fetchall()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error apply data: {e}")
    finally:
        conn.close()
    return offers_applied
    