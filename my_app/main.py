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
    password = st.text_input('Password', type='password')

    if st.button('Login', key="login_button"):
        # Verify user credentials
        cursor.execute('SELECT id, password, is_recruiter FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user and pbkdf2_sha256.verify(password, user[1]):
            st.success('Login successful!')
            st.session_state.user = username
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


if 'user' not in st.session_state:
    st.session_state.user = None

elif page == "User Profile":
    st.title("User Profile")

    if st.session_state.user:
        username = st.session_state.user  # Get the currently logged-in user's username

        # Query the database to fetch user data.
        cursor.execute('SELECT username, email_address FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()

        if user_data:
            username = user_data[0]
            email = user_data[1]

            # Display the user's profile information.
            st.write(f"Username: {username}")
            st.write(f"Email: {email}")

            # Allow the user to upload a profile picture and a CV.
            st.header("Edit Profile")
            uploaded_profile_picture = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
            uploaded_cv = st.file_uploader("Upload CV (PDF)", type=["pdf"])

            if st.button("Save Changes"):
                # Handle profile picture and CV uploads and update the user's data in the database.
                if uploaded_profile_picture:
                    # Process and save the profile picture.
                    pass  # Add your logic here

                if uploaded_cv:
                    # Process and save the CV.
                    pass  # Add your logic here

                # Update the user's data in the database (e.g., username and email).
                # You can use the user_data retrieved from the database to update the user's data.
                # Replace the following lines with your actual database update logic.

                st.success("Changes saved successfully!")
        else:
            st.error("User not found. Please log in.")
    else:
        st.error("You are not logged in. Please log in to view your profile.")
