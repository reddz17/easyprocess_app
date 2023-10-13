from streamlit_option_menu import option_menu
import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
from utils import add_user, create_user_profile, user_profiles, create_database

# Create or connect to the SQLite database
conn = sqlite3.connect('recruitment.db')
cursor = conn.cursor()

# Define the image path for your logo
logo_path = "logo/logo.png"  # Replace with the actual path to your logo

# Initialize the user session state
if 'user' not in st.session_state:
    st.session_state.user = None

# Define a function to show the sidebar and return the selected option
def show_sidebar():
    st.sidebar.image(logo_path, width=300)
    with st.sidebar:
        sidebar_options = ["Home", "Search Jobs", "Login"]
        if st.session_state.user:
            sidebar_options.append("Change Password")
            sidebar_options.remove("Login")
        else:
            sidebar_options.append("Register")
        sidebar_options.append("User Profile")
        selected = option_menu("Main Menu", sidebar_options, icons=['house', 'lightbulb', 'star', 'person', 'gear'], menu_icon="cast", default_index=1)
    return selected

# Define a function to show the login form and authenticate the user
def login_user():
    st.title("User Login")
    email = st.text_input('Email')
    password = st.text_input('Password', type='password')
    if st.button('Login', key="login_button"):
        user = authenticate_user(email, password)
        if user:
            st.success('Login successful!')
            st.empty()
            st.session_state.user = user[4]  # Store the username in the session
            st.write(f'Hello, {user[4]}!')
            st.write('You are a recruiter.' if user[2] else 'You are a candidate.')
        else:
            st.error('Login failed. Check your credentials.')

def update_password(user_id, new_hashed_password, conn):
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_hashed_password, user_id))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error updating password: {e}")

# Define a function to authenticate the user
def authenticate_user(email, password):
    cursor.execute(
        'SELECT id, password, is_recruiter, email_address, username FROM users WHERE email_address = ?', (email,))
    user = cursor.fetchone()
    return user if user and pbkdf2_sha256.verify(password, user[1]) else None

# Define a function to register a new user
def register_user():
    st.title("User Registration")
    new_username = st.text_input('Username')
    new_password = st.text_input('Password', type='password')
    new_email = st.text_input('Email')
    is_recruiter = st.checkbox('I am a recruiter')

    if st.button('Register', key="register_button"):
        add_user(new_username, new_password, new_email, is_recruiter, conn)
        st.success('Registration successful! You can now log in.')

# Define a function to show the change password form
def show_change_password():
    st.title("Change Password")
    if st.session_state.user:
        username = st.session_state.user
        # Create input fields for the current password and the new password
        current_password = pbkdf2_sha256.hash(st.text_input('Current Password', type='password'))
        new_password = st.text_input('New Password', type='password')
        confirm_password = st.text_input('Confirm New Password', type='password')
        if st.button("Change Password"):
            if not new_password:
                st.error("New password cannot be empty.")
            elif new_password != confirm_password:
                st.error("New passwords do not match.")
            else:
                user_data = fetch_user_data(username)
                if user_data:
                    user_id, current_hashed_password = user_data[0], user_data[1]
                    if pbkdf2_sha256.verify(current_password, current_hashed_password):
                        # Passwords match, update the password
                        new_hashed_password = pbkdf2_sha256.hash(new_password)
                        update_password(user_id, new_hashed_password)
                        st.success("Password changed successfully.")
                    else:
                        st.error("Current password is incorrect.")
                else:
                    st.error("User not found. Please log in.")
        else:
            st.warning("Fill in the password fields and click 'Change Password' to proceed.")
    else:
        st.error("You are not logged in. Please log in to change your password.")


# Define a function to show the user profile
def show_user_profile():
    st.title("User Profile")
    if st.session_state.user:
        username = st.session_state.user
        user_data = fetch_user_data(username)

        if user_data:
            username, email = user_data[0], user_data[1]

            st.write(f"Username: {username}")
            st.write(f"Email: {email}")

            st.header("Edit Profile")
            uploaded_profile_picture = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
            uploaded_cv = st.file_uploader("Upload CV (PDF)", type=["pdf"])

            if st.button("Save Changes"):
                update_user_data(username, email, uploaded_profile_picture, uploaded_cv)

            st.success("Changes saved successfully!")
        else:
            st.error("User not found. Please log in.")
    else:
        st.error("You are not logged in. Please log in to view your profile.")

# Define a function to fetch user data from the database
def fetch_user_data(username):
    cursor.execute('SELECT username, email_address FROM users WHERE username = ?', (username,))
    return cursor.fetchone()

# Define a function to update user data in the database
def update_user_data(username, email, profile_picture, cv):
    # Add your logic to update user data and handle file uploads
    pass

# Main app logic
selected_option = show_sidebar()

if selected_option == "Home":
    st.title("Welcome to Your Recruitment Platform")
    st.write("Browse the latest job listings below:")
    # Display job listings here

elif selected_option == "Search Jobs":
    st.title("Search for Jobs")
    # Implement your job search functionality

elif selected_option == "Login":
    login_user()

# Main app logic (continued)

elif selected_option == "Register":
    register_user()

elif selected_option == "Change Password":
    show_change_password()

elif selected_option == "User Profile":
    show_user_profile()

