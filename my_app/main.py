from streamlit_option_menu import option_menu
import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
import pickle 
import os
from utils import *


class RecruitmentApp:
    def __init__(self):
        # Create or connect to the SQLite database
        self.conn = sqlite3.connect('recruitment.db')
        self.cursor = self.conn.cursor()
        self.logo_path = "logo/logo.png"
        self.load_session_state()
        self.initialize_session_state()

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
        
    def show_sidebar(self):
        st.sidebar.image(self.logo_path, width=300)
        with st.sidebar:
            sidebar_options = ["Home", "Search Jobs", "Login"]
            if not self.login_user()[1]:
                if self.session_state['user']:
                    sidebar_options.append("Change Password")
                    sidebar_options.remove("Login")
                    sidebar_options.append("Log Out")
                else:
                    sidebar_options.append("Register")
                sidebar_options.append("User Profile")
                selected = option_menu("Main Menu", sidebar_options, icons=['house', 'lightbulb', 'star', 'person', 'gear'], menu_icon="cast", default_index=1)
            else:
                if self.session_state['user']:
                    sidebar_options.append("Change Password")
                    sidebar_options.remove("Login")
                    sidebar_options.append("Log Out")
                else:
                    sidebar_options.append("Register")
                sidebar_options.append("User Profile")
                selected = option_menu("Main Menu", sidebar_options, icons=['house', 'lightbulb', 'star', 'person', 'gear'], menu_icon="cast", default_index=1)
        return selected
    
    def authenticate_user(self, email, password):
        self.cursor.execute(
            'SELECT id, password, is_recruiter, email_address, username FROM users WHERE email_address = ?', (email,))
        user = self.cursor.fetchone()
        return user if user and pbkdf2_sha256.verify(password, user[1]) else None
    
    def login_user(self):
        st.title("User Login")
        email = st.text_input('Email')
        password = st.text_input('Password', type='password')
        if st.button('Login', key="login_button"):
            user = self.authenticate_user(email, password)
            if user:
                st.success('Login successful!')
                st.empty()
                self.session_state['user'] = user[4]  # Store the username in the session
                self.save_session_state()
                st.write(f'Hello, {user[4]}!')
                if user[2]:  # Check if the user is a recruiter
                    st.write('You are a recruiter.')
                    return 0,user[0]
                else:
                    st.write('You are a candidate.')
                    return 1,user[0]
            else:
                return st.error('Login failed. Check your credentials.')
                

    def update_password(self, user_id, new_hashed_password):
        try:
            self.cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_hashed_password, user_id))
            self.conn.commit()
            st.success('Password changed successfully!')
            # Update session state to avoid log out on page refresh
            self.session_state['user'] = self.fetch_user_data(self.session_state['user'])[3]
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
            self.add_user(new_username, new_password, new_email, is_recruiter)
            st.success('Registration successful! You can now log in.')
            self.session_state['user'] = new_username
            self.save_session_state()

    def add_user(self, username, password, email, is_recruiter):
        hashed_password = pbkdf2_sha256.hash(password)
        self.cursor.execute('INSERT INTO users (username, password, email_address, is_recruiter) VALUES (?, ?, ?, ?)',
                            (username, hashed_password, email, is_recruiter))
        self.conn.commit()

    def update_user_data(self, username, email, profile_picture, cv):
        # self.cursor.execute('UPDATE users SET email_address = ? WHERE username = ?', (email, username))
        # self.conn.commit()
        if profile_picture:
            profile_picture_path = os.path.join(f"data/user_{username}/profile_picture/{username}.jpg")
            os.makedirs(os.path.dirname(profile_picture_path),exist_ok=True)
            with open(profile_picture_path, "wb") as f:
                f.write(profile_picture.read())
            save_profile_picture(profile_picture_path, username)
        if cv:
            cv_path = os.path.join(f"data/user_{username}/CV/{username}_cv.pdf")
            os.makedirs(os.path.dirname(cv_path),exist_ok=True)
            with open(cv_path, "wb") as f:
                f.write(cv.read())
            save_cv_path(cv_path,username)
                
    def update_recruiter_data(self, name_offer, username, profile_picture, job_offer):
        if profile_picture:
            profile_picture_path = os.path.join(f"data/user_{username}/profile_picture/{username}.jpg")
            os.makedirs(os.path.dirname(profile_picture_path),exist_ok=True)
            with open(profile_picture_path, "wb") as f:
                f.write(profile_picture.read())
            save_profile_picture(profile_picture_path,username)
        elif job_offer:
            job_offer_path = os.path.join(f"data/user_{username}/offres/{name_offer}.pdf")
            os.makedirs(os.path.dirname(job_offer_path),exist_ok=True)
            with open(job_offer_path, "wb") as f:
                f.write(job_offer.read())
            save_job_offer(self.login_user()[1],job_offer_path,name_offer)
            
    def show_user_profile(self):
        st.title("User Profile")
        if self.session_state['user']:
            username = self.session_state['user']
            user_data = self.fetch_user_data(username)
            if user_data[4]:
                username, email = user_data[1], user_data[3]
                st.write(f"Username: {username}")
                st.write(f"Email: {email}")
                st.header("Edit Profile")
                uploaded_profile_picture = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
                uploaded_cv = st.file_uploader("Upload CV (PDF)", type=["pdf"])
                if st.button("Save Changes"):
                    self.update_user_data(username, email, uploaded_profile_picture, uploaded_cv)
                st.success("Changes saved successfully!")
            else:
                username, email = user_data[1], user_data[3]
                st.write(f"Username: {username}")
                st.write(f"Email: {email}")
                st.header("Edit Profile")
                uploaded_profile_picture = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
                uploaded_offer = st.file_uploader("Upload offer (PDF)", type=["pdf"])
                if st.button("Save Changes"):
                    self.update_recruiter_data(username, email, uploaded_profile_picture, uploaded_offer)
                st.success("Changes saved successfully!")
                    
                st.error("User not found. Please log in.")
        else:
            st.error("You are not logged in. Please log in to view your profile.")


    def fetch_user_data(self, username):
        self.cursor.execute('SELECT id, username, password, email_address, is_recruiter FROM users WHERE username = ?', (username,))
        return self.cursor.fetchone()

    def show_change_password(self):
        st.title("Change Password")
        if self.session_state['user']:
            username = self.session_state['user']
            current_password = pbkdf2_sha256.hash(st.text_input('Current Password', type='password'))
            new_password = st.text_input('New Password', type='password')
            confirm_password = st.text_input('Confirm New Password', type='password')
            if st.button("Change Password"):
                if not new_password:
                    st.error("New password cannot be empty.")
                elif new_password != confirm_password:
                    st.error("New passwords do not match.")
                else:
                    user_data = self.fetch_user_data(username)
                    if user_data:
                        user_id, current_hashed_password = user_data[0], user_data[2]
                        if pbkdf2_sha256.verify(current_password, current_hashed_password):
                            new_hashed_password = pbkdf2_sha256.hash(new_password)
                            self.update_password(user_id, new_hashed_password)
                            st.success("Password changed successfully.")
                        else:
                            st.error("Current password is incorrect.")
                    else:
                        st.error("User not found. Please log in.")
            else:
                st.warning("Fill in the password fields and click 'Change Password' to proceed.")
        else:
            st.error("You are not logged in. Please log in to change your password.")



if __name__ == "__main__":
    app = RecruitmentApp()
    create_database(app.conn,app.cursor)
    selected_option = app.show_sidebar()
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

