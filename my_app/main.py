from streamlit_option_menu import option_menu
import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
import pickle
import os
from utils import *
import time


SESSION_TIMEOUT = 300


class RecruitmentApp:
    def __init__(self):
        # Create or connect to the SQLite database
        self.conn = sqlite3.connect('recruitment.db')
        self.cursor = self.conn.cursor()
        self.logo_path = "static/logo/logo.png"
        self.load_session_state()
        self.initialize_session_state()
        self.last_activity = time.time()  # Initialize last activity time

    def check_session_timeout(self):
        # Check if the session has timed out due to inactivity
        if time.time() - self.last_activity > SESSION_TIMEOUT:
            self.log_out()

    def initialize_session_state(self):
        # Try to load the session state
        self.load_session_state()
        # If it's not loaded, initialize with default values
        if 'user' not in self.session_state:
            self.session_state['user'] = None

    def load_session_state(self):
        try:
            with open('session_state.pkl', 'rb') as file:
                self.session_state = pickle.load(file)
        except FileNotFoundError:
            self.session_state = {'user': None}

    def save_session_state(self):
        with open('session_state.pkl', 'wb') as file:
            pickle.dump(self.session_state, file)

    def log_out(self):
        self.session_state['user'] = None
        if os.path.exists('session_state.pkl'):
            os.remove('session_state.pkl')
        st.experimental_rerun()

    def show_sidebar(self):
        self.last_activity = time.time()
        st.sidebar.image(self.logo_path, width=300)
        with st.sidebar:
            sidebar_options = ["Home", "Search Jobs", "Login"]
            if self.session_state['user']:
                sidebar_options.append("Change Password")
                sidebar_options.remove("Login")
                sidebar_options.append("Log Out")
            else:
                sidebar_options.append("Register")
            sidebar_options.append("User Profile")
            selected = option_menu("Main Menu", sidebar_options, icons=[
                                   'house', 'lightbulb', 'star', 'person', 'gear'], menu_icon="cast", default_index=1)
            return selected

    def login_user(self):
        st.title("User Login")
        email = st.text_input('Email')
        password = st.text_input('Password', type='password')
        if st.button('Login', key="login_button"):
            user = authenticate_user(email, password)
            if user:
                st.success('Login successful!')
                # Store the username in the session
                self.session_state['user'] = user[4]
                self.save_session_state()
                st.write(f'Hello, {user[4]}!')
                st.experimental_rerun()
                if user[2]:  # Check if the user is a recruiter
                    st.write('You are a recruiter.')
                    return 0
                else:
                    st.write('You are a candidate.')
                    return 1
            else:
                return st.error('Login failed. Check your credentials.')

    def update_password(self, user_id, new_hashed_password):
        self.last_activity = time.time()
        try:
            change_password(new_hashed_password, user_id)
            st.success('Password changed successfully!')
            # Update session state to avoid log out on page refresh
            self.session_state['user'] = fetch_user_data(
                self.session_state['user'])[0]
            self.save_session_state()
        except sqlite3.Error as e:
            st.error(f"Error updating password: {e}")

    def register_user(self):
        st.title("User Registration")
        new_username = st.text_input('Username')
        new_password = st.text_input('Password', type='password')
        new_email = st.text_input('Email')
        is_recruiter = st.checkbox('I am a recruiter')
        if st.button('Register', key="register_button"):
            add_user(new_username, new_password, new_email, is_recruiter)
            st.success('Registration successful! You can now log in.')
            self.session_state['user'] = new_username
            self.save_session_state()
            st.experimental_rerun()

    def update_user_data(self, user_id, profile_picture, cv):
        if self.session_state['user']:
            if profile_picture:
                profile_picture_path = os.path.join(
                    f"static/data/user_{user_id}/profile_picture/{user_id}.jpg")
                os.makedirs(os.path.dirname(
                    profile_picture_path), exist_ok=True)
                with open(profile_picture_path, "wb") as f:
                    f.write(profile_picture.read())
                save_profile_picture(profile_picture_path, user_id)
            if cv:
                cv_path = os.path.join(
                    f"static/data/user_{user_id}/CV/{user_id}_cv.pdf")
                os.makedirs(os.path.dirname(cv_path), exist_ok=True)
                with open(cv_path, "wb") as f:
                    f.write(cv.read())
                save_cv_path(cv_path, user_id)

    def update_recruiter_data(self, user_id, profile_picture, job_offer):
        if profile_picture:
            profile_picture_path = os.path.join(
                f"static/data/user_{user_id}/profile_picture/{user_id}.jpg")
            os.makedirs(os.path.dirname(profile_picture_path), exist_ok=True)
            with open(profile_picture_path, "wb") as f:
                f.write(profile_picture.read())
            save_profile_picture(profile_picture_path, user_id)
        if job_offer:
            job_offer_path = os.path.join(
                f"static/data/user_{user_id}/offres/{user_id}.pdf")
            os.makedirs(os.path.dirname(job_offer_path), exist_ok=True)
            with open(job_offer_path, "wb") as f:
                f.write(job_offer.read())
            save_job_offer(job_offer_path, user_id)

    def show_user_profile(self):
        self.last_activity = time.time()
        st.title("User Profile")
        if self.session_state['user']:
            username = self.session_state['user']
            user_data = fetch_user_data(username)
            if user_data[4]:
                u_id, username, email = user_data[0], user_data[1], user_data[3]
                st.write(f"Username: {username}")
                st.write(f"Email: {email}")
                st.header("Edit Profile")
                uploaded_profile_picture = st.file_uploader(
                    "Upload Profile Picture", type=["jpg", "jpeg", "png"])
                job_offer = st.file_uploader(
                    "Upload job offer (PDF)", type=["pdf"])
                if st.button("Save Changes"):
                    self.update_recruiter_data(
                        u_id, uploaded_profile_picture, job_offer)
                    st.success("Changes saved successfully!")
            else:
                u_id, username, email = user_data[0], user_data[1], user_data[3]
                pic_path, cv_path = get_uploaded_candidate_files(u_id)
                st.write(f"Username: {username}")
                st.write(f"Email: {email}")
                st.header("You picture")
                if pic_path:
                    st.image(pic_path, caption="Profile Picture", width=300)
                st.header("You CV")
                if cv_path:
                    with open(cv_path, 'rb') as pdf_file:
                        pdf_bytes = pdf_file.read()
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        key="pdf_download_button",
                        file_name=(f"{email}.pdf"),
                    )
                st.header("Edit Profile")
                uploaded_profile_picture = st.file_uploader(
                    "Upload Profile Picture (max size: 5 MB)",
                    type=["jpg", "jpeg", "png"],
                    key="profile_picture_uploader",
                    accept_multiple_files=False
                )
                if uploaded_profile_picture:
                    # Check the file size
                    if len(uploaded_profile_picture.getvalue()) > 5 * 1024 * 1024:  # 5 MB limit
                        st.error(
                            "File size exceeds the allowed limit (5 MB). Please upload a smaller file.")
                    else:
                        # Process the file
                        st.success("Profile picture uploaded successfully.")
                uploaded_cv = st.file_uploader(
                    "Upload CV (PDF) (max size: 10 MB)",
                    type=["pdf"],
                    key="cv_uploader",
                    accept_multiple_files=False
                )
                if uploaded_cv:
                    # Check the file size
                    if len(uploaded_cv.getvalue()) > 10 * 1024 * 1024:  # 10 MB limit
                        st.error(
                            "File size exceeds the allowed limit (10 MB). Please upload a smaller file.")
                    else:
                        # Process the file
                        st.success("CV uploaded successfully.")
                if st.button("Save Changes"):
                    self.update_user_data(
                        u_id, uploaded_profile_picture, uploaded_cv)
                    st.success("Changes saved successfully!")
                    st.experimental_rerun()
        else:
            st.error("You are not logged in. Please log in to view your profile.")

    def show_change_password(self):
        self.last_activity = time.time()
        st.title("Change Password")
        if self.session_state['user']:
            username = self.session_state['user']
            current_password = pbkdf2_sha256.hash(
                st.text_input('Current Password', type='password'))
            new_password = st.text_input('New Password', type='password')
            confirm_password = st.text_input(
                'Confirm New Password', type='password')
            if st.button("Change Password"):
                if not new_password:
                    st.error("New password cannot be empty.")
                elif new_password != confirm_password:
                    st.error("New passwords do not match.")
                else:
                    user_data = fetch_user_data(username)
                    if user_data:
                        user_id, current_hashed_password = user_data[0], user_data[2]
                        if pbkdf2_sha256.verify(current_password, current_hashed_password):
                            new_hashed_password = pbkdf2_sha256.hash(
                                new_password)
                            self.update_password(user_id, new_hashed_password)
                            st.success("Password changed successfully.")
                        else:
                            st.error("Current password is incorrect.")
                    else:
                        st.error("User not found. Please log in.")
            else:
                st.warning(
                    "Fill in the password fields and click 'Change Password' to proceed.")
        else:
            st.error(
                "You are not logged in. Please log in to change your password.")


if __name__ == "__main__":
    app = RecruitmentApp()
    create_database(app.conn, app.cursor)
    selected_option = app.show_sidebar()
    app.check_session_timeout()
    if selected_option == "Home":
        st.title("Welcome to Your Recruitment Platform")
        st.write("Browse the latest job listings below:")
        # Display job listings here

    elif selected_option == "Search Jobs":
        st.title("Search for Jobs")
        # Implement your job search functionality

    elif selected_option == "Login":
        app.login_user()

    elif selected_option == "Register":
        app.register_user()

    elif selected_option == "Change Password":
        app.show_change_password()

    elif selected_option == "User Profile":
        app.show_user_profile()
    elif selected_option == "Log Out":
        app.log_out()
