import sys
sys.path.append('/d/HETIC/Mastère 2/projet entreprenaria/easyprocess_app/new_app')

from flask import Flask, render_template, request
import streamlit.components.v1 as components
from streamlit_app.utils import get_user_email_from_token, update_user_password

app = Flask(__name__)

# Your Flask routes and views go here...

@app.route('/')
def index():
    # Embed a Streamlit app within an HTML template
    streamlit_app = components.declare_component(
        "streamlit",  # Replace with the actual component name
        url="http://localhost:8501",  # URL where Streamlit app is running
    )
    return render_template('index.html', streamlit_app=streamlit_app)

@app.route('/forgot_password')
def forgot_password():
    password_reset_url = "http://localhost:5000/reset_password"  # URL of the Streamlit password reset component
    return render_template('forgot_password.html', password_reset_url=password_reset_url)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        # Handle the GET request (e.g., show a form to input a new password)
        # Extract the token from the URL
        token = request.args.get('token')
        if token:
            # Process the token and show the password reset form
            return render_template('reset_password_form.html', token=token)
        else:
            return "Invalid or missing token in the URL."
    elif request.method == 'POST':
        # Handle the POST request to reset the password
        token = request.form.get('token')
        print("the token",token)
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        # Check if the passwords match and other validation logic
        if new_password != confirm_password:
            return "Passwords do not match. Please try again."
        # Implement the logic to update the user's password with the new one
        user_email = get_user_email_from_token(token)  # Implement this function
        if user_email:
            # Update the password in the database for the user with this email
            print(user_email,new_password)
            update_user_password(user_email, new_password)
        # Once the password is reset, you can return a success message or redirect the user to a login page
        return "Password reset successful!"  # You can replace this with a redirect

@app.route('/password_reset_success')
def password_reset_success():
    # You can create an HTML template for a success message
    # or simply return a success message here
    return "Password reset successful. You can now log in with your new password."


if __name__ == '__main__':
    app.run(debug=True)


