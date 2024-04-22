from flask_mail import Mail, Message
from flask import render_template, url_for
from dotenv import load_dotenv
import os

mail = Mail()
load_dotenv()

def send_mail(app, name, token, email):
    with app.app_context():
        enlace = (url_for('reset', token = token, external = True))
        msg = Message('Recuperar contraseña', sender = os.getenv('USER_MAIL'), recipients= [email])
        msg.html = render_template('mail.html', name = name)
        msg.html += f'<p> <a href = "{enlace}">{enlace}>/a></p>'
        mail.send(msg)