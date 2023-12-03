from streamlit_option_menu import option_menu
import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
import pickle
import os
from utils import *
from dotenv import load_dotenv
from user import *
from recruiter import *
from sender_mail import *

load_dotenv()
class RecruitmentApp:
    def __init__(self):
        self.logo_path = os.getenv("logo_path")
        self.load_session_state()
        self.initialize_session_state()
        self.last_activity = time.time()  # Initialize last activity time
        self.SESSION_TIMEOUT = 60
        
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
    
    def show_sidebar(self):
        st.sidebar.image(self.logo_path, width=290)
        with st.sidebar:
            user_data = fetch_user_data(self.session_state['user'])
            sidebar_options = ["Home", "Search Jobs", "Login"]
            if user_data and user_data[4]:
                sidebar_options.append("Change Password")
                sidebar_options.remove("Login")
                sidebar_options.append("Log Out")
                sidebar_options.append("User Profile")
                sidebar_options.append("My Offers")
                sidebar_options.append("My Candidats")
            elif user_data and not user_data[4]:
                sidebar_options.append("Change Password")
                sidebar_options.remove("Login")
                sidebar_options.append("Log Out")
                sidebar_options.append("User Profile")
                sidebar_options.append("My Applications")
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
            if not is_valid_email(new_email):
                st.error("Please enter a valid email address")
                show_error = True  
            # Validate password
            if not is_valid_password(new_password):
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
                

    def show_user_profile(self):
        self.last_activity = time.time()
        st.title("User Profile")
        if self.session_state['user']:
            user_id = self.session_state['user']
            user_data = fetch_user_data(user_id)
            if user_data[4]:
                u_id, username, email = user_data[0], user_data[1], user_data[3]
                pic_path= fetch_recruiter_picture(u_id)
                updated_username = st.text_input("Enter updated username", value=username)
                # Modify Email
                updated_email = st.text_input("Enter updated email", value=email)
                st.header("Your picture")
                if pic_path:
                    st.image(pic_path, caption="Profile Picture", width=150)
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
                title = st.text_input('Title')
                company = st.text_input('Company')
                location = st.text_input('Location')
                experience = st.text_input('Years of experience')
                mode = st.text_input('Work Arrangement')
                description = st.text_area('Description',height=200)
                if st.button("Save Changes"):
                    update_recruiter_data(
                    u_id, uploaded_profile_picture, title, description, location, experience, mode, company)
                    update_candidat_title_profile(u_id, updated_email, updated_username)
                    st.success("Changes saved successfully!")
            else:
                u_id, username, email, profile_title,experiences = user_data[0], user_data[1],\
                user_data[3], user_data[5], user_data[6]
                pic_path, cv_path = get_uploaded_candidate_files(u_id)
                st.header("Your picture")
                if pic_path:
                    st.image(pic_path, caption="Profile Picture", width=200)
                # Download button for CV outside the form
                st.header("Your CV")
                if cv_path:
                    with open(cv_path, 'rb') as pdf_file:
                        pdf_bytes = pdf_file.read()
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        key="pdf_download_button",
                        file_name=(f"{email}.pdf"),
                    )
                # Modify Username
                updated_username = st.text_input("Enter updated username", value=username)
                # Modify Email
                updated_email = st.text_input("Enter updated email", value=email)
                # Modify Profile Title
                updated_profile_title = st.text_input("Enter updated profile title", value=profile_title)
                updated_experiences = st.text_input("Enter updated profile title", value=experiences)
                st.header("Edit Profile")
                uploaded_profile_picture = st.file_uploader(
                    "Upload Profile Picture (max size: 5 MB)",
                    type=["jpg", "jpeg", "png"],
                    key="profile_picture_uploader",
                    accept_multiple_files=False
                )
                uploaded_cv = st.file_uploader(
                    "Upload CV (PDF) (max size: 10 MB)",
                    type=["pdf"],
                    key="cv_uploader",
                    accept_multiple_files=False
                )

                # Save Changes button
                if st.button("Save Changes"):
                    if uploaded_profile_picture:
                        # Check the file size
                        if len(uploaded_profile_picture.getvalue()) > 5 * 1024 * 1024:  # 5 MB limit
                            st.error("File size exceeds the allowed limit (5 MB). Please upload a smaller file.")
                        else:
                            # Process the file
                            st.success("Profile picture uploaded successfully.")
                    if uploaded_cv:
                        # Check the file size
                        if len(uploaded_cv.getvalue()) > 10 * 1024 * 1024:  # 10 MB limit
                            st.error("File size exceeds the allowed limit (10 MB). Please upload a smaller file.")
                        else:
                            # Process the file
                            st.success("CV uploaded successfully.")

                    # Update user data and profile title
                    update_user_data(u_id, uploaded_profile_picture, uploaded_cv)
                    update_user_title_profile(u_id, updated_profile_title, updated_email, updated_username,updated_experiences)
                    st.success("Changes saved successfully!")
                    st.rerun()


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

    def show_offer(self):
        self.last_activity = time.time()
        st.title("Offers")
        if not self.session_state['user']:
            st.error("You are not logged in. Please log in to view and modify your offers.")
            return
        user_id = self.session_state['user']
        job_offers = get_job_offers(user_id)
        job_offers_container = st.container()
        if not job_offers:
            job_offers_container.error("No job offers available at the moment.")
        else:
            # Display job offers in a more visually appealing format
            job_offers_container.subheader("Job Offers")
            for index, job_offer in enumerate(job_offers, start=1):
                with job_offers_container:
                    edit_mode = st.checkbox(f"Edit Offer #{index}", key=f"edit_checkbox_{index}")
                    if edit_mode:
                        title = st.text_input(f"Title: {job_offer[0]}", key=f"title_input_{index}", value=job_offer[0])
                        company = st.text_input(f"Company: {job_offer[3]}", key=f"company_input_{index}", value=job_offer[3])
                        location = st.text_input(f"Location: {job_offer[2]}", key=f"location_input_{index}", value=job_offer[2])
                        experience = st.text_input(f"Experience: {job_offer[4]}", key=f"experience_input_{index}", value=job_offer[4])
                        mode = st.text_input(f"Mode: {job_offer[5]}", key=f"mode_input_{index}", value=job_offer[5])
                        description = st.text_area("Description:", key=f"description_input_{index}", value=job_offer[1],height=280)
                        # Add a save button to save the changes
                        if st.button(f"Save Changes for Offer #{index}", key=f"save_button_{index}"):
                            # Update the job offer in the database
                            update_job_offer(job_offer[6], title, company, location, experience, mode, description)
                            st.success("Changes saved successfully!")
                        if st.button(f"Delete Offer #{index}", key=f"delete_button_{index}"):
                            # Delete the job offer from the database
                            delete_offer(job_offer[6])
                            st.success("Offer deleted successfully!")
                    else:
                        # Display job offer details
                        st.markdown(
                            f"""
                            <div style="background-color: #f5f5f5; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                                <h3>{job_offer[0]}</h3>
                                <p><strong>Company:</strong> {job_offer[1]}</p>
                                <p><strong>Location:</strong> {job_offer[2]}</p>
                                <p><strong>Experience:</strong> {job_offer[4]}</p>
                                <p><strong>Mode:</strong> {job_offer[5]}</p>
                                <p><strong>Description:</strong> {job_offer[3]}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

    def display_apply(self):
        self.last_activity = time.time()
        st.title("Applied")
        if not self.session_state['user']:
            st.error("You are not logged in. Please log in to view and modify your offers.")
            return
        user_id = self.session_state['user']
        applied = applied_offer(user_id)
        cv_path=applied
        applied_container = st.container()
        if not applied:
            applied_container.error("No apply job available at the moment.")
        else:
            st.subheader("Search Results")
            for index, apply in enumerate(applied, start=1):
                # Utilize st.expander to create expandable sections for each job offer
                with st.expander(f"Job Offer #{index} - {apply[0]}"):
                    st.write(f"**Job Title:** {apply[1]}")
                    st.write(f"**Status:** {apply[3]}")
                    st.write(f"**Company:** {apply[4]}")
                    st.write(f"**Description:** {apply[5]}")

                    # Download button for CV
                    if cv_path:
                        with open(cv_path[2][2], 'rb') as pdf_file:
                            pdf_bytes = pdf_file.read()
                        st.download_button(
                            label="Download PDF",
                            data=pdf_bytes,
                            key=f"{index}_pdf_download_button_{apply[2]}",
                            file_name=(f"{apply[2]}.pdf"),
                        )


    def display_candidats(self):
        self.last_activity = time.time()
        st.title("My Candidats")
        search_term = st.text_input("Enter job search term:")
        if not self.session_state['user']:
            st.error("You are not logged in. Please log in to view and modify your offers.")
            return
        applied = applied_candidat(search_term)
        print(applied)
        if st.button("Search"):
            # Récupérez les offres d'emploi filtrées en fonction du terme de recherche
            # Affichez les résultats de la recherche
            if not applied:
                st.write("No job offers match your search.")
            else:
                st.subheader("Search Results")
                for index, apply in enumerate(applied, start=1):
                    # Utilize st.expander to create expandable sections for each job offer
                    with st.expander(f"Job Offer #{index} - {apply[0]}"):
                        if apply[5]:
                            st.image(apply[2], caption="Profile Picture", width=150)
                        st.write(f"**Nom du profile:** {apply[5]}")
                        st.write(f"**Email:** {apply[3]}")
                        if apply[6]:
                            st.write(f"**Experiences:** {apply[6]}")
                        st.write(f"**Status:** {apply[1]}")
                        # Download button for CV
                        with open(apply[4], 'rb') as pdf_file:
                            pdf_bytes = pdf_file.read()
                        st.download_button(
                            label="Download PDF",
                            data=pdf_bytes,
                            key=f"{index}_pdf_download_button_{apply[2]}",
                            file_name=(f"{apply[2]}.pdf"),
                        )
    def seach_job(self):
        st.title("Search for Jobs")
        search_term = st.text_input("Enter job search term:")
            # Si le bouton de recherche est cliqué
        user_id = app.session_state['user']
        user_data = fetch_user_data(user_id)
        if st.button("Search"):
            # Récupérez les offres d'emploi filtrées en fonction du terme de recherche
            job_offers = fetch_job_offers(search_term)
            # Affichez les résultats de la recherche
            if not job_offers:
                st.write("No job offers match your search.")
            else:
                st.subheader("Search Results")
                for index, job_offer in enumerate(job_offers, start=1):
                    # Utilisez st.expander pour créer des sections expansibles pour chaque offre d'emploi
                    with st.expander(f"Job Offer #{index} - {job_offer[0]}"):
                        st.write(f"**Job Title:** {job_offer[0]}")
                        st.write(f"**Company:** {job_offer[1]}")
                        st.write(f"**Location:** {job_offer[2]}")
                        st.write(f"**Mode:** {job_offer[5]}")
                        st.write(f"**Experience:** {job_offer[4]}")
                        st.write(f"**Description:** {job_offer[3]}")
                         # Ajoutez un bouton pour permettre aux candidats de postuler
                        if user_data:
                            if not user_data[4]: 
                                apply_button = st.button(f"Apply for Job #{index}", key=f"apply_button_{index}")
                                user_id = app.session_state['user']
                                if apply_button:
                                    # Enregistrez le CV dans un emplacement spécifique (vous pouvez adapter cela selon votre structure)
                                    cv_path = get_cv_path(user_id)
                                    # Enregistrez les informations de candidature dans la base de données
                                    save_application(user_id, job_offer[0], cv_path)
                                    st.success("Application submitted successfully!")

    def home_page(self):
        st.title("Welcome to Your Recruitment Platform")
        st.write("Browse the latest job listings below:")
        user_id = app.session_state['user']
        user_data = fetch_user_data(user_id)
        # Add a container to hold the job offers section
        job_offers_container = st.container()
        # Display job listings here
        job_offers = fetch_job_offers()
        if not job_offers:
            job_offers_container.error("No job offers available at the moment.")
        else:
            # Display job offers in a more visually appealing format
            job_offers_container.subheader("Job Offers")
            for index, job_offer in enumerate(job_offers, start=1):
                with job_offers_container:
                    pic_path= fetch_recruiter_picture(user_id)
                    print(pic_path)
                    if pic_path:
                        st.image(pic_path, caption="Recruiter Profile Picture", width=100)
                    st.markdown(
                        f"""
                        <div style="background-color: #f5f5f5; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                            <h3>{job_offer[0]}</h3>
                            <p><strong>Company:</strong> {job_offer[1]}</p>
                            <p><strong>Location:</strong> {job_offer[2]}</p>
                            <p><strong>Experience:</strong> {job_offer[4]}</p>
                            <p><strong>Mode:</strong> {job_offer[5]}</p>
                            <p><strong>Description:</strong> {job_offer[3]}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if user_data:
                        if not user_data[4]:
                            apply_button = st.button(f"Apply for Job #{index}", key=f"apply_button_{index}")
                            if apply_button:
                                print(f"Line 490 ----------- {user_id}{job_offer}")
                                # Enregistrez le CV dans un emplacement spécifique (vous pouvez adapter cela selon votre structure)
                                cv_path = get_cv_path(user_id)[0]
                                print(f"Line 493 ----------- {job_offer}")
                                # Enregistrez les informations de candidature dans la base de données
                                save_application(user_id, job_offer[7], job_offer[0], cv_path[0], job_offer[3])
                                st.success("Application submitted successfully!")      
                        
if __name__ == "__main__":
    app = RecruitmentApp()
    create_database()
    selected_option = app.show_sidebar()
    app.check_session_timeout()
    if selected_option == "Reset Password":
        reset_password()
    elif selected_option == "Home":
        app.home_page()
    elif selected_option == "Search Jobs":
        app.seach_job()
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
    elif selected_option == "My Offers":
        app.show_offer()
    elif selected_option == "My Applications":
        app.display_apply()
    elif selected_option== "My Candidats":
        app.display_candidats()