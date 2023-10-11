import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sqlite3
from passlib.hash import pbkdf2_sha256
from utils import add_user, create_user_profile
from utils import create_database

# Create the SQLite database and tables
create_database()


# Create a SQLite database
conn = sqlite3.connect('recruitment.db')
cursor = conn.cursor()

# Define a user model
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        is_recruiter INTEGER NOT NULL
    )
''')
conn.commit()

# # Helper function to add a user
# def add_user(username, password, is_recruiter):
#     password_hash = pbkdf2_sha256.hash(password)
#     cursor.execute('INSERT INTO users (username, password, is_recruiter) VALUES (?, ?, ?)', (username, password_hash, is_recruiter))
#     conn.commit()


# User registration form
st.subheader('User Registration')
new_username = st.text_input('Username', key="username_input")
new_password = st.text_input('Password', type='password', key="password_input")
is_recruiter = st.checkbox('I am a recruiter')

if st.button('Register'):
    add_user(new_username, new_password, is_recruiter)
    st.success('Registration successful! You can now log in.')

# User login form
st.subheader('User Login')
username = st.text_input('Username')
password = st.text_input('Password', type='password')

if st.button('Login'):
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


# Créez une liste fictive de profils utilisateur
user_profiles = [
    {
        "Nom": "John Doe",
        "Email": "john.doe@email.com",
        "ID Utilisateur": "12345",
        "Date d inscription": "2022-01-15",
        "Dernière Connexion": "2023-10-15 14:30:00",
        "Photo de Profil": None,  # Ajout de la photo de profil
        "CV (PDF)": None,  # Ajout du CV (PDF)
    },
    {
        "Nom": "Jane Smith",
        "Email": "jane.smith@email.com",
        "ID Utilisateur": "67890",
        "Date d'Inscription": "2022-03-20",
        "Dernière Connexion": "2023-10-15 09:45:00",
        "Photo de Profil": None,
        "CV (PDF)": None,
    },
    # Ajoutez d'autres profils utilisateur fictifs si nécessaire
]

# # Fonction pour créer un nouveau compte utilisateur
# def create_user_profile():
#     st.header("Création d'un Nouveau Compte Utilisateur")
#
#     # Formulaire pour saisir les informations du nouveau compte
#     new_name = st.text_input("Nom complet:")
#     new_email = st.text_input("Email:")
#     new_id = st.text_input("ID Utilisateur:")
#
#     # Widget pour télécharger un fichier PDF (CV)
#     cv_file = st.file_uploader("Télécharger le CV (PDF)", type=["pdf"])
#
#     # Widget pour télécharger une photo de profil (image)
#     profile_picture = st.file_uploader("Télécharger une Photo de Profil (Image)", type=["jpg", "jpeg", "png"])
#
#     # Ajoutez ici la logique pour enregistrer le nouveau profil utilisateur
#     if st.button("Créer le Compte"):
#         new_profile = {
#             "Nom": new_name,
#             "Email": new_email,
#             "ID Utilisateur": new_id,
#             "Date d inscription": pd.to_datetime("now"),
#             "Dernière Connexion": None,
#             "Photo de Profil": profile_picture,  # Enregistrez la photo de profil téléchargée
#             "CV (PDF)": cv_file,  # Enregistrez le fichier PDF téléchargé (CV)
#         }
#         user_profiles.append(new_profile)
#         st.success("Compte utilisateur créé avec succès!")
#
#     # Vous pouvez ajouter une validation des données ou d'autres vérifications si nécessaire

# Titre de la page
st.title("EasyProcess - Plateforme d'Optimisation de Processus")

# Barre de navigation
menu = ["Accueil", "Tableau de Bord", "Profil", "Paramètres"]  # Retirez "Analyse des Données"
choice = st.sidebar.selectbox("Navigation", menu)

# Section Accueil
if choice == "Accueil":
    st.header("Bienvenue sur EasyProcess")
    st.write("Cette plateforme vous permet d'optimiser vos processus métier de manière efficace.")

# Section Tableau de Bord
elif choice == "Tableau de Bord":
    st.header("Tableau de Bord")

    # Création de données fictives avec des valeurs spécifiées
    data = pd.DataFrame({
        "A": [1, 2, 3, 4, 5],
        "B": [10, 9, 8, 7, 6],
        "C": [15, 12, 10, 8, 6]
    })

    # Affichage du tableau de données
    st.subheader("Données de Performance")
    st.dataframe(data)

    # Création d'un graphique interactif avec des données spécifiées
    st.subheader("Graphique interactif")
    fig = px.scatter(data, x="A", y="B", color="C", size="C")
    st.plotly_chart(fig)


elif choice == "Profil":
    st.header("Profil de l'Utilisateur")

    # Widget for selecting a user or creating a new account
    selected_user = st.selectbox(
        "Sélectionnez un Utilisateur ou Créez un Nouveau Compte",
        ["Nouveau Compte"] + [profile["Nom"] for profile in user_profiles],
        )

    if selected_user == "Nouveau Compte":
        # Call the create_user_profile function
        create_user_profile(
            user_profiles,
            new_name=st.text_input("Nom complet:"),
            new_email=st.text_input("Email:"),
            new_id=st.text_input("ID Utilisateur:"),
            profile_picture=st.file_uploader("Télécharger une Photo de Profil (Image)", type=["jpg", "jpeg", "png"]),
            cv_file=st.file_uploader("Télécharger le CV (PDF)", type=["pdf"]),
        )

        st.success("Compte utilisateur créé avec succès!")

# Section Profil (Ajoutée)
# elif choice == "Profil":
#     st.header("Profil de l'Utilisateur")
#
#     # Widget pour sélectionner un utilisateur ou créer un nouveau compte
#     selected_user = st.selectbox("Sélectionnez un Utilisateur ou Créez un Nouveau Compte", ["Nouveau Compte"] + [profile["Nom"] for profile in user_profiles])
#
#     if selected_user == "Nouveau Compte":
#         create_user_profile()  # Afficher le formulaire de création de compte utilisateur
#     else:
#         # Affichez les informations du profil utilisateur sélectionné
#         for profile in user_profiles:
#             if profile["Nom"] == selected_user:
#                 st.subheader("Informations du Profil")
#                 st.write(f"Nom: {profile['Nom']}")
#                 st.write(f"Email: {profile['Email']}")
#                 st.write(f"ID Utilisateur: {profile['ID Utilisateur']}")
#                 st.write(f"Date d'Inscription: {profile['Date d inscription']}")
#                 st.write(f"Dernière Connexion: {profile['Dernière Connexion']}")
#                 st.subheader("Photo de Profil")
#                 if profile["Photo de Profil"] is not None:
#                     st.image(profile["Photo de Profil"], use_column_width=True)
#                 else:
#                     st.write("Aucune photo de profil téléchargée.")
#                     st.subheader("CV (PDF)")
#                 if profile["CV (PDF)"] is not None:
#                     st.write("CV téléchargé. Cliquez sur le lien ci-dessous pour voir le CV.")
#                     st.write(profile["CV (PDF)"])
#                 else:
#                     st.write("Aucun CV (PDF) téléchargé.")

# Section Paramètres
elif choice == "Paramètres":
    st.header("Paramètre")
    # Widget de sélection de date
    selected_date = st.date_input("Sélectionnez une date", pd.to_datetime("2023-01-01"))
    st.write("Date sélectionnée:", selected_date)
    # Widget de sélection de plage de valeurs
    min_value, max_value = st.slider("Sélectionnez une plage de valeurs", 0, 100, (25, 75))
    st.write("Plage de valeurs sélectionnée:", min_value, max_value)
# Ajoutez un pied de page
st.sidebar.title("À Propos")
st.sidebar.info("Cette plateforme a été créée pour l'optimisation de processus.")
st.sidebar.text("© 2023 EasyProcess")
