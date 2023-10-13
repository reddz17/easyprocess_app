import sqlite3
import streamlit as st
from passlib.hash import pbkdf2_sha256
from datetime import datetime

def create_database(conn, cursor):
    # Create the users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email_address TEXT NOT NULL,
            password TEXT NOT NULL,
            is_recruiter INTEGER NOT NULL,
            profile_picture TEXT,
            cv_file TEXT
        )
    ''')

    # Create the job_offers table with the correct columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_offers (
            id INTEGER PRIMARY KEY,
            recruiter_id INTEGER,
            offer_path TEXT NOT NULL
        )
    ''')

    # Create other tables (e.g., job listings and applications) if needed

    conn.commit()

# Helper function to add a user

def add_user(username, email_address, password, is_recruiter, conn, cursor):
    password_hash = pbkdf2_sha256.hash(password)
    cursor.execute('INSERT INTO users (username, email_address, password, is_recruiter) VALUES (?, ?, ?, ?)', (username, email_address, password_hash, is_recruiter))
    conn.commit()

@st.cache(allow_output_mutation=True)
def save_cv_to_profile(user_id, cv_file_path, conn, cursor):
    cursor.execute("UPDATE users SET cv_file = ? WHERE id = ?", (cv_file_path, user_id))
    conn.commit()
@st.cache(allow_output_mutation=True)
def save_profile_picture_to_profile(user_id, profile_picture_path, conn, cursor):
    cursor.execute("UPDATE users SET profile_picture = ? WHERE id = ?", (profile_picture_path, user_id))
    conn.commit()

@st.cache(allow_output_mutation=True)
def save_job_offer(recruiter_id, job_offer_path, conn, cursor):
    cursor.execute('INSERT INTO job_offers (recruiter_id, offer_path) VALUES (?, ?)', (recruiter_id, job_offer_path))
    conn.commit()
