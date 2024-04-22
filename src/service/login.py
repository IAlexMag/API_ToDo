from flask import Flask, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask_mail import Mail
import os
import bcrypt as bcp
import random
import string
from datetime import datetime, timedelta
from datetime import datetime

load_dotenv()

app = Flask(__name__, template_folder='src/Templates')
bcrypt = Bcrypt(app)
mail = Mail()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT'))
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASS')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')

mysql = MySQL(app)





           
# validación de usuario.
def validate_user(data):
    with app.app_context():
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM user WHERE email = %s", (data.get('email'),))
            user = cursor.fetchone()
            cursor.close()
            if user and bcrypt.check_password_hash(user[2], data.get('password')):
                print(user)
                return user
        except TypeError as e:
            print(e)

# registro de usuarios.
def save_user(data):
    with app.app_context():
        salt = bcp.gensalt()
        try:
            data['password'] = bcp.hashpw(data.get('password').encode('utf-8'),salt)
            cursor = mysql.connection.cursor()
            cursor.execute('''INSERT INTO user (email, password, first_name, last_name, age, create_date)
                           VALUES (%s, %s, %s, %s, %s, %s)''', (data.get("email"), data.get("password"), 
                                                              data.get("first_name"), data.get("last_name"), data.get("age"), datetime.now()))
            mysql.connection.commit()
            cursor.close()
            msg = 'te has registrado con éxito'
            return msg
        except ValueError as e:
            msg = e
            return msg

def users():
    with app.app_context():
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT iduser, email FROM user')
            lis = cursor.fetchall()
            cursor.close()
            return lis
        except ValueError as e:
            print(e)

def exists_users(usuario):
    with app.app_context():
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM user WHERE email = %s', (usuario,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except ValueError as e:
            print(e)  
#exists_users((1, 'alexander_orenda@hotmail.com'))

def delete_users(usuario):
    with app.app_context():
        try:
            if usuario is not None:
                cursor = mysql.connection.cursor()
                cursor.execute('CALL sp_delete_users(%s, @cantidad_j);', (usuario[0],))
                cursor.execute('SELECT @cantidad_j;')
                msg = cursor.fetchone()
                mysql.connection.commit()
                cursor.close()
                return str(msg)
            else:
                msg = 'Usuario no encontrado'
                return msg
        except ValueError as e:
            msg = e
            return str(msg)

def update_user(data, user):
    with app.app_context():
        try:
            if data is not None:
                cursor = mysql.connection.cursor()
                cursor.execute('CALL sp_usersupdate(%s, %s, %s, %s, %s, @msg);', 
                               (user, data.get('first_name'), 
                                data.get('last_name'), data.get('age'), data.get('id_empleado'),))
                cursor.execute('SELECT @msg;')
                msg = cursor.fetchone()
                mysql.connection.commit()
                cursor.close()
                return str(msg)
            else:
                msg = 'Usario no encontrado'
                return str(msg)
        except ValueError as e:
            msg = e
            return str(msg)

def val_user(data):
    with app.app_context():
        try:
            if data is not None:
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT * FROM user WHERE iduser = %s', (data,))
                val = cursor.fetchone()
                cursor.close()
                return val
            else:
                val = None
                return val
        except ValueError as e:
            print(e)

def validate_mfa(id):
    with app.app_context():
        try:
            if id is not None:
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT * FROM user WHERE iduser = %s and token IS NOT NULL', (id,))
                data = cursor.fetchone()
                cursor.close()
                if data is not None:
                    msg = True
                    return msg
                else:
                    msg = None
                    return msg
            else:
                msg = None
                return msg
        except ValueError as e:
            print(e)
