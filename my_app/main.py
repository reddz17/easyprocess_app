import os

import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
from utils import add_user, save_profile_picture_to_profile, save_cv_to_profile, save_job_offer
from utils import create_database

# Create a SQLite database
conn = sqlite3.connect('recruitment.db')
cursor = conn.cursor()

# Create the database tables
create_database(conn, cursor)

# Ensure session state user is initialized
if 'user' not in st.session_state:
    st.session_state.user = None

# Navigation bar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("Home", "Search Jobs", "Login", "Register", "User Profile"))

if page == "Home":
    st.title("Welcome to Your Recruitment Platform")
    st.write("Browse the latest job listings below:")
    # Display job listings here

elif page == "Search Jobs":
    st.title("Search for Jobs")
    # Implement your job search functionality

elif page == "Login":
    st.title("User Login")
    # Implement the login form
    username = st.text_input('Username')
    email = st.text_input('Email')
    password = st.text_input('Password', type='password')
    print(f"DEBUG: Entered username: {username}")
    print(f"DEBUG: Entered email: {email}")

    # Initialize a variable to track if a login attempt was made
    if 'login_attempted' not in st.session_state:
        st.session_state.login_attempted = False

    # Verify user credentials only when login_attempted is True
    if st.session_state.login_attempted:
        # Verify user credentials
        cursor.execute('SELECT id, password, is_recruiter FROM users WHERE username = ? AND email_address = ?', (username, email))
        user = cursor.fetchone()
        print(f"DEBUG: Retrieved user: {user}")  # Check the user retrieved from the database
        if user and pbkdf2_sha256.verify(password, user[1]):
            st.success('Login successful!')
            st.session_state.user = username
            st.write(f'Hello, {username}!')
        else:
            st.error('Login failed. Check your credentials.')
    if username or email or password:
        st.session_state.login_attempted = True

elif page == "Register":
    st.title("User Registration")
    # Implement the registration form
    new_username = st.text_input('Username')
    new_email = st.text_input('Email')
    new_password = st.text_input('Password', type='password')
    is_recruiter = st.checkbox('I am a recruiter')

    if st.button('Register', key="register_button"):
        add_user(new_username, new_email, new_password, is_recruiter, conn, cursor)
        st.success('Registration successful! You can now log in.')

elif page == "User Profile":
    st.title("User Profile")

    # Check if the user is logged in
    if st.session_state.user:
        username = st.session_state.user

        cursor.execute('SELECT id, is_recruiter FROM users WHERE username = ?', (username,))
        user_info = cursor.fetchone()

        if user_info:
            if user_info[1]:  # If the user is a recruiter
                st.write('You are a recruiter.')
                st.write('You can submit a job offer.')

                # Create a form to submit a job offer
                job_offer_file = st.file_uploader("Upload Job Offer (PDF)", type=["pdf"])
                if st.button('Submit Job Offer'):
                    if job_offer_file is not None:
                        # Define the base directory where job offer files are stored
                        base_dir = "data/"
                        job_offers_path = os.path.join(base_dir, f"user_{user_info[0]}/job offer/{job_offer_file.name}")
                        os.makedirs(os.path.dirname(job_offers_path), exist_ok=True)

                        # Save the job offer
                        with open(job_offers_path, "wb") as f:
                            f.write(job_offer_file.read())
                            st.success("Job offer uploaded successfully.")

                        # Save the job offer to the database
                        save_job_offer(user_info[0], job_offers_path, conn, cursor)

                    else:
                        st.error("Please upload a valid PDF file for the job offer.")
            else:
                st.write('You are a candidate.')
                st.write('You can edit your profile.')

                # Create a form to upload a profile picture
                profile_picture = st.file_uploader("Upload Profile Picture (Image)", type=["jpg", "jpeg", "png"])
                if st.button('Upload Profile Picture'):
                    if profile_picture is not None:
                        # Define the base directory where profile pictures are stored
                        base_dir = "data/"
                        profile_picture_path = os.path.join(base_dir, f"user_{user_info[0]}/profile picture/{profile_picture.name}")
                        os.makedirs(os.path.dirname(profile_picture_path), exist_ok=True)

                        # Save the profile picture
                        with open(profile_picture_path, "wb") as f:
                            f.write(profile_picture.read())
                            st.success("Profile picture uploaded successfully.")

                        # Save the profile picture to the user's profile in the database
                        save_profile_picture_to_profile(user_info[0], profile_picture_path, conn, cursor)
                    else:
                        st.error("Please upload a valid image (jpg, jpeg, or png).")

                # Create a form to upload a CV
                cv_file = st.file_uploader("Upload CV (PDF)", type=["pdf"])
                if st.button('Upload CV'):
                    if cv_file is not None:
                        # Define the base directory where CV files are stored
                        base_dir = "data/"
                        cv_file_path = os.path.join(base_dir, f"user_{user_info[0]}/CV/{cv_file.name}")
                        os.makedirs(os.path.dirname(cv_file_path), exist_ok=True)

                        # Save the CV
                        with open(cv_file_path, "wb") as f:
                            f.write(cv_file.read())
                            st.success("CV uploaded successfully.")

                        # Save the CV to the user's profile in the database
                        save_cv_to_profile(user_info[0], cv_file_path, conn, cursor)
                    else:
                        st.error("Please upload a valid PDF file.")
        else:
            st.error('User not found in the database. Please log in again.')
    else:
        st.error("Please log in to access your user profile.")
