from streamlit_option_menu import option_menu
import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
import pickle
import os
from utils import *
import time
import re 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
from env import ENV_PASSWORD, ENV_EMAIL

class RecruitmentApp:
    def __init__(self):
        # Create or connect to the SQLite database
        self.conn = sqlite3.connect('recruitment.db')
        self.cursor = self.conn.cursor()
        self.logo_path = "static/logo/logo.png"
        self.load_session_state()
        self.initialize_session_state()
        self.last_activity = time.time()  # Initialize last activity time
        self.SESSION_TIMEOUT = 60
        self.token_lifetime = 3600 
        
        
        
    def check_session_timeout(self):
        # Check if the session has timed out due to inactivity
        if time.time() - self.last_activity > self.SESSION_TIMEOUT:
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
        st.rerun()
    
    def is_valid_email(self,email):
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(email_pattern,email) is not None
    
    def is_valid_password(self,password):
        return len(password)>=12 and any(c.isupper() for c in password)and\
               any(c.islower() for c in password) and any(c.isdigit() for c in password) 
      
    def show_sidebar(self):
        self.last_activity = time.time()
        st.sidebar.image(self.logo_path, width=300)
        with st.sidebar:
            sidebar_options = ["Home", "Search Jobs", "Login"]
            if self.session_state['user']:
                sidebar_options.append("Change Password")
                sidebar_options.remove("Login")
                sidebar_options.append("Log Out")
                sidebar_options.append("User Profile")
            else:
                sidebar_options.append("Register")
                sidebar_options.append("Reset Password")
            selected = option_menu("Main Menu", sidebar_options, icons=[
                                'house', 'lightbulb', 'star', 'person', 'gear'], menu_icon="cast", default_index=0)
        return selected

    def login_user(self):
        st.title("User Login")
        email = st.text_input('Email').lower()
        password = st.text_input('Password', type='password')
        if st.button('Login', key="login_button"):
            user = authenticate_user(email, password)
            if user:
                st.success('Login successful!')
                # Store the username in the session
                self.session_state['user'] = user[0]
                self.save_session_state()
                st.write(f'Hello, {user[4]}!')
                st.rerun()
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
        confirm_password = st.text_input('Confirm Password', type='password')
        new_email = st.text_input('Email')
        is_recruiter = st.checkbox('I am a recruiter')
        show_error = False
        email_already_exists = check_email_exists(new_email)
        if st.button('Register', key="register_button"):
            # Convert email to lowercase
            new_email = new_email.lower()
            # Check if the email already exists
            if check_email_exists(new_email):
                st.error("Email already exists. Please use a different email.")
                show_error = True
            # Validate email
            if not self.is_valid_email(new_email):
                st.error("Please enter a valid email address")
                show_error = True  
            # Validate password
            if not self.is_valid_password(new_password):
                st.error("Password must be at least 12 characters with at least one uppercase letter, one lowercase letter, and one digit")
                show_error = True       
            # Check if passwords match
            if new_password != confirm_password:
                st.error("Passwords do not match")
                show_error = True
            if email_already_exists:
                # Display the "Reset Password" button if the email already exists
                st.warning("This email is already registered. You can reset your password.")
            if not show_error:
                registration = add_user(new_username, new_email, new_password, is_recruiter)
                if registration:
                    st.success('Registration successful! You can now log in.')
                    self.session_state['user'] = fetch_user_data_mail(new_email)
                    self.save_session_state()
                    st.rerun()
                else:
                    st.error('User registration failed. Please try again.')
        else:
            if show_error:
                st.error("Please correct the errors in the form")
                
                
    def reset_password(self):
        st.title("Reset Password")
        reset_email = st.text_input("Enter your registered email address").lower()
        if st.button("Reset Password", key="reset_password_button"):
            user_data = fetch_user_data_mail(reset_email)
            if user_data:
                confirmation_link,token = self.generate_confirmation_link(reset_email)
                update_token_user(token,reset_email)
                self.send_reset_password_email(reset_email, confirmation_link)  # Send the reset password email
                st.success("Password reset confirmation email sent. Please check your email.")
            else:
                st.error("Email not found. Please enter a registered email address.")



    def send_reset_password_email(self,recipient_email, reset_link):
        # Email configuration
        smtp_server = "smtp-mail.outlook.com"
        smtp_port = 587
        sender_email = ENV_EMAIL  # Your email address
        sender_password = ENV_PASSWORD  # Your email password
        # Create the email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = "Password Reset Request"
        # Email body
        email_body = f"Click the following link to reset your password: {reset_link}"
        message.attach(MIMEText(email_body, "plain"))
        # Connect to the SMTP server and send the email
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            server.quit()
            return True
        except Exception as e:
            st.error(f"Error sending password reset email: {str(e)}")
            return False

    def generate_confirmation_link(self, email):
        token = hashlib.md5((email + str(time.time())).encode()).hexdigest()
        expiration_time = time.time() + self.token_lifetime
        confirmation_link = f"http://localhost:5000/reset_password?token={token}&expiration={expiration_time}"
        return confirmation_link, token

    def is_token_expired(self, expiration_time):
        current_time = time.time()
        return current_time > expiration_time

    # Modify the change_password_with_token function
    def change_password_with_token(self):
        st.title("Change Password with Token")
        token = st.text_input("Enter the password reset token")
        stored_token, expiration_time = self.retrieve_token_locally()
        feedback_message = st.empty()  # Create an empty space for feedback
        if st.button("Reset Password"):
            if token == stored_token and not self.is_token_expired(expiration_time):
                feedback_message.success("Token is valid and not expired. You can now reset your password.")
                feedback_message = st.empty()
                # Implement the password reset functionality here
                # Allow the user to enter and confirm the new password
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                if confirm_password == new_password:
                    # Perform the password reset
                    user_email = self.retrieve_user_email_from_token(token)
                    new_hashed_password = pbkdf2_sha256.hash(new_password)
                    change_password(new_hashed_password, user_email)
                    feedback_message.success("Password reset successfully. You can now log in with your new password.")
                else:
                    feedback_message.error("Invalid password. Please check and try again.")
            elif self.is_token_expired(expiration_time):
                feedback_message.error("Token has expired. Please request a new password reset link.")
            else:
                feedback_message.error("Invalid token. Please check and try again.")


    
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
            save_job_offer(user_id, job_offer, name_offer, title, description, location, salary )

    def show_user_profile(self):
        self.last_activity = time.time()
        st.title("User Profile")
        if self.session_state['user']:
            user_id = self.session_state['user']
            user_data = fetch_user_data(user_id)
            if user_data[4]:
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
                    st.rerun()
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
                    st.rerun()
        else:
            st.error("You are not logged in. Please log in to view your profile.")

    def show_change_password(self):
        self.last_activity = time.time()
        st.title("Change Password")
        if not self.session_state['user']:
            st.error("You are not logged in. Please log in to change your password.")
            return
        user_id = self.session_state['user']
        user_data = fetch_user_data(user_id)
        if not user_data:
            st.error("User not found. Please log in.")
            return
        user_id, current_hashed_password = user_data[0], user_data[2]
        current_password = st.text_input('Current Password', type='password')
        new_password = st.text_input('New Password', type='password')
        confirm_password = st.text_input('Confirm New Password', type='password')
        if st.button("Change Password"):
            if not new_password:
                st.error("New password cannot be empty.")
                return
            if new_password != confirm_password:
                st.error("New passwords do not match.")
                return
            # Print for debugging purposes
            if pbkdf2_sha256.verify(current_password,current_hashed_password ):
                new_hashed_password = pbkdf2_sha256.hash(new_password)
                self.update_password(user_id, new_hashed_password)
                st.success("Password changed successfully.")
                # st.rerun()
            else:
                st.error("Current password is incorrect.")


if __name__ == "__main__":
    app = RecruitmentApp()
    create_database(app.conn, app.cursor)
    selected_option = app.show_sidebar()
    app.check_session_timeout()
    if selected_option == "Reset Password":
        app.reset_password()
    elif selected_option == "Home":
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