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
import base64
from datetime import datetime


load_dotenv()
class RecruitmentApp:
    def __init__(self):
        self.logo_path = os.getenv("logo_path")
        self.initialize_session_state()
        self.load_session_state()
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
            sidebar_options = ["Accueil", "Chercher une offre", "Connexion"]
            if user_data and user_data[4]:
                sidebar_options.append("Changer mot de passe")
                sidebar_options.remove("Connexion")
                sidebar_options.append("Déconnexion")
                sidebar_options.append("Profile utilisateur")
                sidebar_options.append("Mes Offres")
                sidebar_options.append("Mes Candidats")
            elif user_data and not user_data[4]:
                sidebar_options.append("Changer mot de passe")
                sidebar_options.remove("Connexion")
                sidebar_options.append("Déconnexion")
                sidebar_options.append("Profile utilisateur")
                sidebar_options.append("Mes Candidatures")
            else:
                sidebar_options.append("Crée un compte")
                sidebar_options.append("Mot de passe oublier")
            selected = option_menu("Menu Principal", sidebar_options, icons=[
                                'house', 'search', 'arrow-left-right', 'door-open', 'gear',"list-task","bag-check-fill"], menu_icon="cast", default_index=0)
        return selected

    def login_user(self):
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #FFD700;
                color:#white;
                font-weight: bold;
            }
            div.stButton > button:hover {
                background-color: #FFA500;  /* Change color on hover, e.g., orange */
                }
            </style>""", unsafe_allow_html=True)
        title_html = '''
            <style>
                .custom-title {
                    color: #FFD700; /* Use the same color as the button */
                    font-size: 45px; /* Adjust the font size as needed */
                    font-weight: bold;
                    margin-bottom: 20px; /* Add some margin to space it from other elements */
                }
            </style>
            <h1 class="custom-title">Connectez vous !</h1>
        '''
        st.markdown(title_html,unsafe_allow_html=True)
        email = st.text_input('Email').lower()
        password = st.text_input('Mot de passe', type='password')
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
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #FFD700;
                color:#white;
            }
            div.stButton > button:hover {
                background-color: #FFA500;  /* Change color on hover, e.g., orange */
                }
            </style>""", unsafe_allow_html=True)
        title_html = '''
            <style>
                .custom-title {
                    color: #FFD700; /* Use the same color as the button */
                    font-size: 45px; /* Adjust the font size as needed */
                    font-weight: bold;
                    margin-bottom: 20px; /* Add some margin to space it from other elements */
                }
            </style>
            <h1 class="custom-title">Créez votre compte:</h1>
        '''
        st.markdown(title_html,unsafe_allow_html=True)
        new_username = st.text_input("Nom d'utilisateur")
        new_password = st.text_input('Mot de passe', type='password')
        confirm_password = st.text_input('Comfirmez votre mot de passe', type='password')
        new_email = st.text_input('Email')
        is_recruiter = st.checkbox('Je suis recruteur')
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
        # st.title("Profile Utilisateur")
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #FFD700;
                color:#white;
            }
            div.stButton > button:hover {
                background-color: #FFA500;  /* Change color on hover, e.g., orange */
                }
            </style>""", unsafe_allow_html=True)
        title_html = '''
            <style>
                .custom-title {
                    color: #FFD700; /* Use the same color as the button */
                    font-size: 45px; /* Adjust the font size as needed */
                    font-weight: bold;
                    margin-bottom: 20px; /* Add some margin to space it from other elements */
                }
            </style>
            <h1 class="custom-title">Profile Utilisateur :</h1>
        '''
        st.markdown(title_html,unsafe_allow_html=True)
        if self.session_state['user']:
            user_id = self.session_state['user']
            user_data = fetch_user_data(user_id)
            if user_data[4]:
                u_id, username, email = user_data[0], user_data[1], user_data[3]
                pic_path= fetch_recruiter_picture(u_id)
                updated_username = st.text_input("Nom d'utilisateur", value=username)
                # Modify Email
                updated_email = st.text_input("Email", value=email)
                st.header("Photo de Profile")
                if pic_path:
                    st.image(pic_path, caption="Photo de Profile", width=150)
                st.header("Modifier le Profile")
                uploaded_profile_picture = st.file_uploader(
                    "Upload la photo de profil (max size: 5 MB)",
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
                st.header("Crée une offre")
                publication_date = st.date_input("Date de publication")
                title = st.text_input("Titre de l'offre")
                company = st.text_input('Entreprise')
                location = st.text_input('Localisation')
                experience = st.text_input('Experiences')
                mode = st.text_input('Mode de travail')
                description = st.text_area('Description',height=200)
                if st.button("Sauvegarder"):
                    update_recruiter_data(
                    u_id, uploaded_profile_picture, title, description, location, experience, mode, company, publication_date)
                    update_candidat_title_profile(u_id, updated_email, updated_username)
                    st.success("Modification sauvegardé avec succés !")
            else:
                u_id, username, email, profile_title,experiences = user_data[0], user_data[1],\
                user_data[3], user_data[5], user_data[6]
                pic_path, cv_path = get_uploaded_candidate_files(u_id)
                st.header("Photo de Profile")
                if pic_path:
                    st.image(pic_path, caption="Photo Profile", width=200)
                # Download button for CV outside the form
                st.header("Ton CV")
                if cv_path:
                    with open(cv_path, 'rb') as pdf_file:
                        pdf_bytes = pdf_file.read()
                    # st.download_button(
                    #     label="Télécharger mon CV",
                    #     data=pdf_bytes,
                    #     key="pdf_download_button",
                    #     file_name=(f"{email}.pdf"),
                    # )
                    download_button_html = f'''
                        <style>
                            .custom-button {{
                                background-color: #FFD700;
                                color: white;
                                padding: 10px 20px;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                                text-decoration: none;
                                display: inline-block;
                                margin-top: 10px;
                            }}
                        </style>
                        <a href="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode('utf-8')}" 
                        download="{email}.pdf" 
                        class="custom-button">
                        Télécharger CV
                        </a>
                    '''
                    st.markdown(download_button_html, unsafe_allow_html=True)
                # Modify Username
                updated_username = st.text_input("Nom d'utilisateur", value=username)
                # Modify Email
                updated_email = st.text_input("Email", value=email)
                # Modify Profile Title
                updated_profile_title = st.text_input("Titre de profile", value=profile_title)
                updated_experiences = st.text_input("Année d'éxperiences ", value=experiences)
                st.header("Modifier le Profile")
                uploaded_profile_picture = st.file_uploader(
                    "Upload Photo de Profile  (max size: 5 MB)",
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
                if st.button("Sauvegarder"):
                    if uploaded_profile_picture:
                        # Check the file size
                        if len(uploaded_profile_picture.getvalue()) > 5 * 1024 * 1024:  # 5 MB limit
                            st.error("File size exceeds the allowed limit (5 MB). Please upload a smaller file.")
                        else:
                            # Process the file
                            st.success("La photo de Profile à été uploadé avec succés.")
                    if uploaded_cv:
                        # Check the file size
                        if len(uploaded_cv.getvalue()) > 10 * 1024 * 1024:  # 10 MB limit
                            st.error("File size exceeds the allowed limit (10 MB). Please upload a smaller file.")
                        else:
                            # Process the file
                            st.success("CV uploadé avec succés.")
                    # Update user data and profile title
                    update_user_data(u_id, uploaded_profile_picture, uploaded_cv)
                    update_user_title_profile(u_id, updated_profile_title, updated_email, updated_username,updated_experiences)
                    st.success("Midification effectuée avec succés !")


    def show_change_password(self):
        self.last_activity = time.time()
        # st.title("Changer le mot de passe")
        st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #FFD700;
            color:#white;
        }
        div.stButton > button:hover {
            background-color: #FFA500;  /* Change color on hover, e.g., orange */
                }
            </style>""", unsafe_allow_html=True)
        title_html = '''
            <style>
                .custom-title {
                    color: #FFD700; /* Use the same color as the button */
                    font-size: 45px; /* Adjust the font size as needed */
                    font-weight: bold;
                    margin-bottom: 20px; /* Add some margin to space it from other elements */
                }
            </style>
            <h1 class="custom-title">Profile Utilisateur :</h1>
        '''
        st.markdown(title_html, unsafe_allow_html=True)
        if not self.session_state['user']:
            st.error("Vous n'êtes pas connecté. Veuillez vous connecter pour modifier votre mot de passe.")
            return
        user_id = self.session_state['user']
        user_data = fetch_user_data(user_id)
        if not user_data:
            st.error("Utilisateur introuvable. Veuillez vous connecter.")
            return
        user_id, current_hashed_password = user_data[0], user_data[2]
        current_password = st.text_input('Mot de passe actuel', type='password')
        new_password = st.text_input('Nouveau mot de passe', type='password')
        confirm_password = st.text_input('Confirmer le nouveau mot de passe', type='password')
        # if st.button("Changer le mot de passe"):
        if st.button("Changer mot de passe"):
            if not new_password:
                st.error("Le nouveau mot de passe ne peut pas être vide.")
                return
            if new_password != confirm_password:
                st.error("Les nouveaux mots de passe ne correspondent pas.")
                return
            if pbkdf2_sha256.verify(current_password,current_hashed_password ):
                new_hashed_password = pbkdf2_sha256.hash(new_password)
                self.update_password(user_id, new_hashed_password)
                st.success("Le mot de passe a été modifié avec succès.")
                # st.rerun()
            else:
                st.error("Le mot de passe actuel est incorrect.")

    def show_offer(self):
        self.last_activity = time.time()
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #FFD700;
                color:#white;
                font-weight: bold;
            }
            div.stButton > button:hover {
                background-color: #FFA500;  /* Change color on hover, e.g., orange */
                }
            </style>""", unsafe_allow_html=True)
        # st.title("Offers")
        title_html = '''
            <style>
                .custom-title {
                    color: #FFD700; /* Use the same color as the button */
                    font-size: 45px; /* Adjust the font size as needed */
                    font-weight: bold;
                    margin-bottom: 20px; /* Add some margin to space it from other elements */
                }
            </style>
            <h1 class="custom-title">Mes offres d'emplois :</h1>
        '''
        st.markdown(title_html, unsafe_allow_html=True)
        if not self.session_state['user']:
            st.error("You are not logged in. Please log in to view and modify your offers.")
            return
        user_id = self.session_state['user']
        job_offers = get_job_offers(user_id)
        job_offers_container = st.container()
        if not job_offers:
            job_offers_container.error("Aucune offre d'emploi n'est disponible pour le moment.")
        else:
            # Display job offers in a more visually appealing format
            job_offers_container.subheader("Offres d'emploi")
            for index, job_offer in enumerate(job_offers, start=1):
                with job_offers_container:
                    edit_mode = st.checkbox(f"Modifier l'offre #{index}", key=f"edit_checkbox_{index}")
                    if edit_mode:
                        title = st.text_input(f"Titre : {job_offer[0]}", key=f"title_input_{index}", value=job_offer[0])
                        company = st.text_input(f"Companie : {job_offer[1]}", key=f"company_input_{index}", value=job_offer[1])
                        location = st.text_input(f"Localisation : {job_offer[2]}", key=f"location_input_{index}", value=job_offer[2])
                        experience = st.text_input(f"Experiences : {job_offer[4]}", key=f"experience_input_{index}", value=job_offer[4])
                        mode = st.text_input(f"Mode : {job_offer[5]}", key=f"mode_input_{index}", value=job_offer[5])
                        description = st.text_area("Description:", key=f"description_input_{index}", value=job_offer[3],height=280)
                        # Add a save button to save the changes
                        if st.button(f"Enregistrer les modifications #{index}", key=f"save_button_{index}"):
                            # Update the job offer in the database
                            update_job_offer(job_offer[6], title, company, location, experience, mode, description)
                            st.success("Changes saved successfully!")
                        if st.button(f"Supprimer l'offre #{index}", key=f"delete_button_{index}"):
                            # Delete the job offer from the database
                            delete_offer(job_offer[6])
                            st.success("L'offre a été supprimée avec succès !")
                    else:
                        # Display job offer details
                        st.markdown(
                            f"""
                            <div style="background-color: #f5f5f5; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);height: 400px; overflow-y: scroll;">
                                <h3>{job_offer[0]}</h3>
                                <p><strong>Date de publication :</strong> {job_offer[7]}</p>
                                <p><strong>Companie :</strong> {job_offer[1]}</p>
                                <p><strong>Location :</strong> {job_offer[2]}</p>
                                <p><strong>Experiences :</strong> {job_offer[4]}</p>
                                <p><strong>Mode :</strong> {job_offer[5]}</p>
                                <p><strong>Description :</strong></p><div style="height: 400px; overflow-y: scroll;">{job_offer[3]}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

    def display_apply(self):
        self.last_activity = time.time()
        # st.title("Candidaté")
        title_html = '''
            <style>
                .custom-title {
                    color: #FFD700; /* Use the same color as the button */
                    font-size: 44px; /* Adjust the font size as needed */
                    font-weight: bold;
                    margin-bottom: 20px; /* Add some margin to space it from other elements */
                }
            </style>
            <h1 class="custom-title">Candidatures :</h1>
        '''
        st.markdown(title_html, unsafe_allow_html=True)
        if not self.session_state['user']:
            st.error("Vous n'êtes pas connecté. Veuillez vous connecter pour consulter et modifier vos offres.")
            return
        user_id = self.session_state['user']
        applied = applied_offer(user_id)
        cv_path=applied
        applied_container = st.container()
        if not applied:
            applied_container.error("Aucun emploi n'est disponible pour le moment.")
        else:
            st.subheader("Résultats de la recherche")
            for index, apply in enumerate(applied, start=1):
                # Utilize st.expander to create expandable sections for each job offer
                with st.expander(f"Offre d'emploi #{index} - {apply[0]}"):
                    st.write(f"**Titre du poste :** {apply[1]}")
                    st.write(f"**date :** {apply[6]}")
                    st.write(f"**Statut :** {apply[3]}")
                    st.write(f"**Compagnie:** {apply[4]}")
                    st.write(f"**Description:** {apply[5]}")
                    # Download button for CV
                    if cv_path:
                        with open(cv_path[0][2], 'rb') as pdf_file:
                            pdf_bytes = pdf_file.read()
                        # st.download_button(
                        #     label="Télécharger CV",
                        #     data=pdf_bytes,
                        #     key=f"{index}_pdf_download_button_{apply[2]}",
                        #     file_name=(f"{apply[2]}.pdf"),
                        # )
                        # Create a custom HTML link for the "Télécharger CV" button
                        download_button_html = f'''
                            <style>
                                .custom-button {{
                                    background-color: #FFD700;
                                    color: white;
                                    padding: 10px 20px;
                                    border: none;
                                    border-radius: 5px;
                                    cursor: pointer;
                                    text-decoration: none;
                                    display: inline-block;
                                    margin-top: 10px;
                                }}
                            </style>
                            <a href="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode('utf-8')}" 
                            download="{apply[2]}.pdf" 
                            class="custom-button">
                            Télécharger CV
                            </a>
                        '''
                        st.markdown(download_button_html, unsafe_allow_html=True)

    
    def search_job(self):
        st.markdown("""
            <style>
                div.stButton > button:first-child {
                    background-color: #FFD700;
                    color: white;
                }
                div.stButton > button:hover {
                    background-color: #FFA500;
                }
            </style>""", unsafe_allow_html=True)
        title_html = '''
            <style>
                .custom-title {
                    color: #FFD700;
                    font-size: 44px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }
            </style>
            <h1 class="custom-title">Choisissez le job fait pour vous !</h1>
        '''
        st.markdown(title_html, unsafe_allow_html=True)
        user_id = app.session_state['user']
        user_data = fetch_user_data(user_id)
        cv_path = get_cv_path(user_id)
        # Use text_input instead of button for search and capture changes dynamically
        search_term = st.text_input("Cherchez le job fait pour vous ! :")
        # Récupérez les offres d'emploi filtrées en fonction du terme de recherche
        job_offers = fetch_job_offers(search_term)
        # Affichez les résultats de la recherche
        if not job_offers:
            st.write("Aucune offre d'emploi ne correspond à votre recherche.")
        else:
            st.subheader("Résultats de la recherche")
            for index, job_offer in enumerate(job_offers, start=1):
                # Utilisez st.expander pour créer des sections expansibles pour chaque offre d'emploi
                with st.expander(f"Offre d'emploi #{index} - {job_offer[0]}"):
                    st.write(f"**Intituler du poste :** {job_offer[0]}")
                    st.write(f"**Date de publication :** {job_offer[8]}")
                    st.write(f"**Companie :** {job_offer[1]}")
                    st.write(f"**Location :** {job_offer[2]}")
                    st.write(f"**Mode :** {job_offer[5]}")
                    st.write(f"**Experiences :** {job_offer[4]}")
                    # st.write(f"**Description :** {job_offer[3]}")
                    st.write(f"**Description :**")
                    st.text_area("", job_offer[3], height=300) 
                    # Ajoutez un bouton pour permettre aux candidats de postuler
                    if user_data and not user_data[4] and get_cv_path(user_data[0]):
                        apply_button_key = f"apply_button_{job_offer[7]}_{index}"
                        apply_button = st.button("Postuler", key=apply_button_key)
                        # Check if the user has already applied for this job
                        applied_jobs = [apply[0] for apply in applied_offer(user_id)]
                        if job_offer[7] in applied_jobs:
                            st.warning("Vous avez déjà postulé pour ce poste.")
                        elif apply_button:
                            # Use a spinner while processing
                            with st.spinner("On y est presque..."):
                                # Enregistrez les informations de candidature dans la base de données
                                save_application(user_id, job_offer[7], job_offer[0], cv_path, job_offer[1])
                                send_email_offer(user_data[3], user_data[1], job_offer[0], job_offer[3], job_offer[1])
                                st.success("Bravos ! Ton CV a été envoyé avec succés.")

    
    def home_page(self):
        # st.title("Bienvenue sur votre plateforme de recrutement")
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #FFD700;
                color:#white;
                font-weight: bold;
            }
            div.stButton > button:hover {
                background-color: #FFA500;  /* Change color on hover, e.g., orange */
                }
            </style>""", unsafe_allow_html=True)
        title_html = '''
            <style>
                .custom-title {
                    color: #FFD700; /* Use the same color as the button */
                    font-size: 44px; /* Adjust the font size as needed */
                    font-weight: bold;
                    margin-bottom: 20px; /* Add some margin to space it from other elements */
                }
            </style>
            <h1 class="custom-title">Explorer, s’enthousiasmer, candidater. Choisissez le job fait pour vous !</h1>
        '''
        st.markdown(title_html, unsafe_allow_html=True)
        st.write("Parcourez les dernières offres d'emploi ci-dessous :")
        user_id = app.session_state['user']
        user_data = fetch_user_data(user_id)
        
        # Display job listings here
        job_offers = fetch_job_offers()
        if not job_offers:
            st.error("Aucune offre d'emploi n'est disponible pour le moment.")
        else:
            # Display job offers in a more visually appealing format
            st.subheader("Offres d'emploi")
            job_offer_containers = []
            for index, job_offer in enumerate(job_offers, start=1):
                job_offer_container = st.container()
                job_offer_containers.append(job_offer_container)
                with job_offer_container:
                    recruiter_id = job_offer[9]
                    # Assuming the recruiter_id is at the 7th index in your job_offer tuple
                    pic_path = fetch_recruiter_picture(recruiter_id)
                    if pic_path:
                        st.image(pic_path, caption="Entreprise", width=150)
                    st.markdown(
                        f"""
                        <div style="background-color: #f5f5f5; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); height: 400px; overflow-y: scroll; ">
                            <h3>{job_offer[0]}</h3>
                            <p><strong>Date de publication :</strong>{job_offer[8]}</p>
                            <p><strong>Companie:</strong> {job_offer[1]}</p>
                            <p><strong>Location:</strong> {job_offer[2]}</p>
                            <p><strong>Experiences:</strong> {job_offer[4]}</p>
                            <p><strong>Mode:</strong> {job_offer[5]}</p>
                            <p><strong>Description :</strong></p><div style="height: 400px; overflow-y: scroll;">{job_offer[3]}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if user_data and not user_data[4]:
                        if get_cv_path(user_data[0]): 
                            button_pos = st.button("Postuler", key=f"apply_button_{index}")
                            user_id = self.session_state['user']
                            # Check if the user has already applied for this job
                            applied_jobs = [apply[0] for apply in applied_offer(user_id)]
                            if job_offer[7] in applied_jobs:
                                st.warning("Vous avez déjà postulé pour ce poste.")
                            elif button_pos:
                                with st.spinner("On y est presque..."):
                                    # Enregistrez le CV dans un emplacement spécifique (vous pouvez adapter cela selon votre structure)
                                    cv_path = get_cv_path(user_id)
                                    # Enregistrez les informations de candidature dans la base de données
                                    save_application(user_id, job_offer[7], job_offer[0], cv_path, job_offer[1])
                                    send_email_offer(user_data[3], user_data[1], job_offer[0], job_offer[3], job_offer[1])
                                    st.success("Bravos ! Ton CV a été envoyé avec succès.")
                        


    def display_candidats(self):
        self.last_activity = time.time()
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #FFD700;
                color:#white;
                font-weight: bold;
            }
            div.stButton > button:hover {
                background-color: #FFA500;  /* Change color on hover, e.g., orange */
                }
            </style>""", unsafe_allow_html=True)
        title_html = '''
            <style>
                .custom-title {
                    color: #FFD700; /* Use the same color as the button */
                    font-size: 44px; /* Adjust the font size as needed */
                    font-weight: bold;
                    margin-bottom: 20px; /* Add some margin to space it from other elements */
                }
            </style>
            <h1 class="custom-title">Mes candidats !</h1>
        '''
        st.markdown(title_html, unsafe_allow_html=True)
        if not self.session_state['user']:
            st.error("You are not logged in. Please log in to view and modify your offers.")
            return
        search_term = st.text_input("Cherchez votre candiat fait pour vous ! :")
        applied = applied_candidat(search_term)
        # Récupérez les offres d'emploi filtrées en fonction du terme de recherche
        # Affichez les résultats de la recherche
        if not applied:
            st.warning("Aucune candidats n'a postulé.")
        else:
            st.subheader("Résultats de la recherche")
            for index, apply in enumerate(applied, start=1):
                # Utilize st.expander to create expandable sections for each job offer
                with st.expander(f"Offre #{index} - {apply[0]}"):
                    if apply[5]:
                        st.image(apply[2], caption="Profile Picture", width=150)
                    st.write(f"**Nom du profile:** {apply[5]}")
                    st.write(f"**Email:** {apply[3]}")
                    if apply[6]:
                        st.write(f"**Experiences:** {apply[6]}")
                    # Allow editing of the status
                    new_status = st.selectbox("Select Status", options=["En cours", "Accepter", "Refuser"], key=f"status_select_{index}")
                    st.write(f"**Status:** {apply[1]}")
                    enreg = st.button("enregistrer les modifications", key=f"je_modifie_{index}")
                    if enreg:
                        if new_status =="Accepter":
                            with st.spinner("On y est presque..."):
                                send_acceptation(apply[8],apply[3],apply[10],apply[9])
                        elif new_status=="Refuser":
                            with st.spinner("On y est presque..."):
                                send_declination(apply[8],apply[3],apply[10],apply[9])  
                        # Corrected function name
                        update_application_status(str(new_status), apply[7], apply[0])
                        st.success("Les modifications ont été enregistrées avec succès !")
                    # Download button for CV
                    with open(apply[4], 'rb') as pdf_file:
                        pdf_bytes = pdf_file.read()
                    download_button_html = f'''
                        <style>
                            .custom-button {{
                                background-color: #FFD700;
                                color: white;
                                padding: 10px 20px;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                                text-decoration: none;
                                display: inline-block;
                                margin-top: 10px;
                            }}
                        </style>
                        <a href="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode('utf-8')}" 
                        download="{apply[3]}.pdf" 
                        class="custom-button">
                        Télécharger CV
                        </a>
                    '''
                    st.markdown(download_button_html, unsafe_allow_html=True)

if __name__ == "__main__":
    app = RecruitmentApp()
    create_database()
    selected_option = app.show_sidebar()
    app.check_session_timeout()
    if selected_option == "Mot de passe oublier":
        reset_password()
    elif selected_option == "Accueil":
        app.home_page()
    elif selected_option == "Chercher une offre":
        app.search_job()
    elif selected_option == "Connexion":
        app.login_user()
    elif selected_option == "Crée un compte":
        app.register_user()
    elif selected_option == "Changer mot de passe":
        app.show_change_password()
    elif selected_option == "Profile utilisateur":
        app.show_user_profile()
    elif selected_option == "Déconnexion":
        app.log_out()
    elif selected_option == "Mes Offres":
        app.show_offer()
    elif selected_option == "Mes Candidatures":
        app.display_apply()
    elif selected_option== "Mes Candidats":
        app.display_candidats()