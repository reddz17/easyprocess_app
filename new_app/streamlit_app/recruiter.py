import os
import sqlite3
from user import save_profile_picture



def update_recruiter_data(user_id, profile_picture, title, description, location, experience, mode, company, publication_date):
    if profile_picture:
        profile_picture_path = os.path.join(
            f"{os.getenv('profile_path')}{user_id}.jpg")
        os.makedirs(os.path.dirname(profile_picture_path), exist_ok=True)
        with open(profile_picture_path, "wb") as f:
            f.write(profile_picture.read())
        save_profile_picture(profile_picture_path, user_id)
    if title and company and location and experience and mode and description and publication_date :
        save_job_offer(user_id, title, description, location, experience, mode, company, publication_date)


def save_job_offer(recruiter_id, title, description, location, experience, mode, company, publication_date):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO JobOffers (recruiter_id, title, description, location, experience, mode, company, publication_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (recruiter_id, title, description, location, experience, mode, company, publication_date))
    conn.commit()
    conn.close()

def fetch_job_offers(search_term=None):
    conn = sqlite3.connect('recruitment.db')  # Modify the database path if needed
    cursor = conn.cursor()
    # Construisez la requête SQL en fonction du terme de recherche
    if search_term:
        query = f"""SELECT title, company, location, description,
        experience, mode, location, job_id, publication_date, recruiter_id 
        FROM JobOffers 
        WHERE title LIKE '%{search_term}%' OR company LIKE '%{search_term}%' OR description LIKE '%{search_term}%'"""
    else:
        query = """SELECT title, company, location, description,
        experience, mode, location, job_id, publication_date, recruiter_id
        FROM JobOffers"""
    # Exécutez la requête SQL pour récupérer les offres d'emploi
    cursor.execute(query)
    job_offers = cursor.fetchall()
    conn.close()
    return job_offers


def fetch_recruiter_picture(recruiter_id):
    conn = sqlite3.connect('recruitment.db')  # Modify the database path if needed
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT profile_picture 
            FROM Users 
            WHERE user_id = ? AND is_recruiter = 1
        """, (recruiter_id,))
        
        profile_picture = cursor.fetchone()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error retrieving recruiter data: {e}")
        return None
    finally:
        conn.close()
    if profile_picture:
        return profile_picture[0]
    else:
        return None



    
def save_application(user_id, job_id, job_title, cv_path, company):
    conn = sqlite3.connect('recruitment.db')  # Modify the database path if needed
    cursor = conn.cursor()
    try:
        # Insert the application details into the database
        cursor.execute("""
            INSERT INTO Applications (candidate_id, job_id, job_title, cv_path, company)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, job_id, job_title, cv_path, company))
        # Commit the changes to the database
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error saving application: {e}")
    finally:
        # Close the database connection
        conn.close()


def get_picture(user_id):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT user_id, profile_picture FROM Users WHERE user_id = ?', (user_id,))
    return cursor.fetchone()    
    
def get_job_offers(recruiter_id):
    conn = sqlite3.connect('recruitment.db')  # Modify the database path if needed
    cursor = conn.cursor()
    # Construisez la requête SQL en fonction du terme de recherche
    cursor.execute("""SELECT title, company, location, description,
                   experience, mode, job_id, publication_date 
                   FROM JobOffers 
                   WHERE recruiter_id = ?""", (recruiter_id,))
    # Exécutez la requête SQL pour récupérer les offres d'emploi
    job_offers = cursor.fetchall()
    conn.close()
    return job_offers

    # Function to get offer details by index
def update_job_offer(job_id, title, company, location, experience, mode, description):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE JobOffers 
        SET title=?, company=?, location=?, experience=?, mode=?, description=?
        WHERE job_id=?
    ''', (title, company, location, experience, mode, description, job_id))
    conn.commit()
    conn.close()
    
def delete_offer(job_id):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM JobOffers WHERE job_id=?', (job_id,))
    conn.commit()
    conn.close()

def applied_candidat(search_term=None):
    conn = sqlite3.connect('recruitment.db')  # Modify the database path if needed
    cursor = conn.cursor()
    # Construisez la requête SQL en fonction du terme de recherche
    if search_term:
        query = f"""SELECT a.job_id, a.application_status,
                   u.profile_picture, u.email_address, u.cv_path, u.profile_title, u.experiences, u.user_id, u.username, j.title, j.company
            FROM Applications a,
                 JobOffers j,
                 Users u 
            WHERE a.candidate_id = u.user_id 
                AND a.job_id = j.job_id
                AND (u.email_address LIKE '%{search_term}%' 
                     OR u.profile_title LIKE '%{search_term}%' 
                     OR a.application_status LIKE '%{search_term}%'
                     OR u.experiences LIKE '%{search_term}')"""
    else:
        query = """SELECT a.job_id, a.application_status,
                  u.profile_picture, u.email_address, u.cv_path, u.profile_title ,u.experiences, u.user_id, u.username, j.title, j.company
                FROM Applications a,
                    JobOffers j, 
                    Users u 
                WHERE a.candidate_id = u.user_id and a.job_id = j.job_id"""
    cursor.execute(query)
    # Exécutez la requête SQL pour récupérer les offres d'emploi
    try:
        candidats = cursor.fetchall()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error apply data: {e}")
    finally:
        conn.close()
    return candidats

def update_application_status(new_status, candidate_id, job_id):
    conn = sqlite3.connect('recruitment.db')  # Modify the database path if needed
    cursor = conn.cursor()
    update_query = f"""
        UPDATE Applications
        SET application_status = ?
        WHERE candidate_id = ? AND job_id = ?
    """
    try:
        cursor.execute(update_query, (new_status, candidate_id, job_id))
    # Exécutez la requête SQL pour récupérer les offres d'emploi
        conn.commit()
        # Close the connection
        conn.close()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error updating data: {e}")