import sqlite3


def create_database():
    # Create the database tables if they don't exist
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email_address TEXT UNIQUE NOT NULL,
            is_recruiter BOOLEAN NOT NULL,
            profile_picture TEXT,
            cv_path TEXT,
            reset_token TEXT,
            profile_title TEXT,
            experiences INTEGER
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
            publication_date datetime,
            FOREIGN KEY (recruiter_id) REFERENCES Users (user_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Quiz (
            quiz_id INTEGER PRIMARY KEY,  -- Assuming quiz_id is unique for each quiz
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            name_quiz TEXT NOT NULL,
            result_quiz INTEGER NOT NULL,  -- Assuming the result is a percentage (e.g., 90)
            FOREIGN KEY (job_id) REFERENCES JobOffers (job_id),
            FOREIGN KEY (candidate_id) REFERENCES Users (user_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Applications (
            application_id INTEGER PRIMARY KEY,
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            job_title TEXT NOT NULL,
            cv_path TEXT NOT NULL,
            company TEXT NOT NULL,
            application_status TEXT NOT NULL DEFAULT 'En cours',
            FOREIGN KEY (job_id) REFERENCES JobOffers (job_id),
            FOREIGN KEY (candidate_id) REFERENCES Users (user_id)
        )
    ''')
    # Commit changes, but keep the connection open if it was passed as a parameter
    conn.commit()