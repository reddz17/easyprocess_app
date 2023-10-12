import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
from utils import add_user, create_user_profile, user_profiles
from utils import create_database

# Create a SQLite database
conn = sqlite3.connect('recruitment.db')
cursor = conn.cursor()
create_database(conn, cursor)

# Navigation bar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("Home", "Search Jobs", "Login", "Register"))

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
    password = st.text_input('Password', type='password')

    if st.button('Login', key="login_button"):
        # Verify user credentials
        cursor.execute('SELECT id, password, is_recruiter FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user and pbkdf2_sha256.verify(password, user[1]):
            st.success('Login successful!')
            st.write(f'Hello, {username}!')
            if user[2]:
                st.write('You are a recruiter.')
            else:
                st.write('You are a candidate.')
        else:
            st.error('Login failed. Check your credentials.')

elif page == "Register":
    st.title("User Registration")
    # Implement the registration form
    new_username = st.text_input('Username')
    new_password = st.text_input('Password', type='password')
    new_email = st.text_input('Email')
    is_recruiter = st.checkbox('I am a recruiter')

    if st.button('Register', key="register_button"):
        add_user(new_username, new_password, new_email, is_recruiter, conn, cursor)
        st.success('Registration successful! You can now log in.')