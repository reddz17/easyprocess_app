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
    st.title("Reset Password")
    reset_email = st.text_input("Enter your registered email address").lower()
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
    print(conn)
    cursor = conn.cursor()
    print(cursor)
    cursor.execute("SELECT email_address FROM Users WHERE reset_token = ?", (token,))
    user = cursor.fetchone()
    print(user)
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

