import re 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import time
import streamlit as st
import sqlite3
from dotenv import load_dotenv
import os



load_dotenv()

def is_valid_email(email):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_pattern,email) is not None

def is_valid_password(password):
    return len(password)>=12 and any(c.isupper() for c in password)and\
            any(c.islower() for c in password) and any(c.isdigit() for c in password) 
            
def send_reset_password_email(recipient_email, reset_link):
    # Email configuration
    smtp_server = "smtp-mail.outlook.com"
    smtp_port = 587
    sender_email = os.getenv("ENV_EMAIL")  # Your email address
    sender_password = os.getenv("ENV_PASSWORD")  # Your email password
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
    
def send_email_offer(recipient_email,username,titre, description,company):
    # Email configuration
    smtp_server = "smtp-mail.outlook.com"
    smtp_port = 587
    sender_email = os.getenv("ENV_EMAIL")  # Your email address
    sender_password = os.getenv("ENV_PASSWORD")  # Your email password
    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "accusé de reception de {company} pour l'offre {titre}"
    # Email body
    email_body = f"""Cher / Chère {username},

        Merci d’avoir postulé à l’offre {titre} . Nous allons étudier vos expériences et qualifications dans les plus brefs délais. 
        Si votre profil correspond à nos attentes, un membre de notre équipe entrera en contact avec vous.
                        
                     {description}
                        
                     En vous souhaitant bonne chance !
                     {company} """
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
    
def send_acceptation(username, recipient_email, company, offre):
    # Email configuration
    smtp_server = "smtp-mail.outlook.com"
    smtp_port = 587
    sender_email = os.getenv("ENV_EMAIL")  # Your email address
    sender_password = os.getenv("ENV_PASSWORD")  # Your email password
    
    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = f"Accusé de réception de {company} pour l'offre {offre}"
    
    # Email body
    email_body = f"""Cher / Chère {username},

Félicitations ! Nous sommes ravis de vous annoncer que vous avez été sélectionné(e) pour le poste de {offre} chez {company}.

Nous attendons avec impatience votre arrivée. Veuillez trouver ci-joint les documents nécessaires à remplir avant votre première journée.

Si vous avez des questions, n'hésitez pas à nous contacter.

Bienvenue dans l'équipe !

Cordialement,
{company}"""
    
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

def send_declination(username, recipient_email, company, offre):
    # Email configuration
    smtp_server = "smtp-mail.outlook.com"
    smtp_port = 587
    sender_email = os.getenv("ENV_EMAIL")  # Your email address
    sender_password = os.getenv("ENV_PASSWORD")  # Your email password
    
    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = f"Refus de {company} pour l'offre {offre}"
    
    # Email body
    email_body = f"""Cher / Chère {username},
Nous tenons à vous remercier sincèrement pour l'intérêt que vous avez manifesté envers le poste de {offre} chez {company}. Après une évaluation approfondie de toutes les candidatures, nous regrettons de vous informer que votre candidature n'a pas été retenue pour ce poste.

Nous avons apprécié vos compétences et votre expérience, mais le processus de sélection a été extrêmement compétitif.

Nous vous souhaitons le meilleur dans vos recherches futures et espérons que nos chemins pourront se croiser à nouveau.

Merci encore pour l'intérêt que vous avez porté à {company}.

Cordialement,
{company}"""
    
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

    
    
    
def is_token_expired( expiration_time):
    current_time = time.time()
    return current_time > expiration_time

def update_token_user(user_token,user_email):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET reset_token = ? WHERE email_address = ?", (user_token,user_email))
    conn.commit()
    conn.close()
    
def generate_confirmation_link( email):
    token_lifetime = 3600   
    token = hashlib.md5((email + str(time.time())).encode()).hexdigest()
    expiration_time = time.time() + token_lifetime
    confirmation_link = f"http://localhost:5000/reset_password?token={token}&expiration={expiration_time}"
    return confirmation_link, token

def reset_password():
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
            <h1 class="custom-title">Réinitialiser votre mot de passe !</h1>
        '''
    st.markdown(title_html, unsafe_allow_html=True)
    reset_email = st.text_input("Entrez votre adresse e-mail de conenxion").lower()
    if st.button("Reset Password", key="reset_password_button"):
        user_data = fetch_user_data_mail(reset_email)
        if user_data:
            confirmation_link,token = generate_confirmation_link(reset_email)
            update_token_user(token,reset_email)
            send_reset_password_email(reset_email, confirmation_link)  # Send the reset password email
            st.success("Password reset confirmation email sent. Please check your email.")
        else:
            st.error("Email not found. Please enter a registered email address.")


def get_user_email_from_token(token):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email_address FROM Users WHERE reset_token = ?", (token,))
    user = cursor.fetchone()
    if user:
        return user[0]
    return None

def change_password(new_hashed_password, user_id):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE Users SET password = ? WHERE user_id = ?', (new_hashed_password, user_id))
    conn.commit()
    conn.close()

def fetch_user_data_mail(email):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT user_id FROM Users WHERE email_address = ?', (email,))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0] if user_id else None

