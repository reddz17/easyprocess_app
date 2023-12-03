import sys
sys.path.append('/d/HETIC/Mastère 2/projet entreprenaria/easyprocess_app/new_app')

from flask import Flask, render_template, request
import streamlit.components.v1 as components
from streamlit_app.sender_mail import get_user_email_from_token,is_valid_password
from streamlit_app.user import update_user_password


app = Flask(__name__)

# Your Flask routes and views go here...
# def is_valid_password(password):
#     return len(password)>=12 and any(c.isupper() for c in password)and\
#             any(c.islower() for c in password) and any(c.isdigit() for c in password) 


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
    token = request.args.get('token')
    error_message = ""  # Initialize error_message
    success_message = ""  # Initialize success_message
    if request.method == 'GET':
        if not token:
            return "Invalid or missing token in the URL."
        return render_template('reset_password_form.html', token=token)
    elif request.method == 'POST':
        token = request.form.get('token')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        if new_password != confirm_password:
            error_message = "Passwords do not match. Please try again."
        elif not is_valid_password(new_password):
            error_message = "Password does not meet the required criteria."
        else:
            user_email = get_user_email_from_token(token)
            if user_email:
                update_user_password(user_email, new_password)
                success_message = "Password reset successful! You can now log in with your new password."
                return render_template('success.html', token=token, error_message=error_message, success_message=success_message)
            else:
                error_message = "Invalid token. Please check and try again."
        return render_template('reset_password_form.html', token=token, error_message=error_message, success_message=success_message)



@app.route('/password_reset_success')
def password_reset_success():
    # You can create an HTML template for a success message
    # or simply return a success message here
    return "Password reset successful. You can now log in with your new password."


if __name__ == '__main__':
    app.run(debug=True)


