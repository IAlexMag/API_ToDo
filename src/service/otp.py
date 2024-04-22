from flask import Flask, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
import bcrypt as bcp
import pyotp

# se declaran variables para la configuración de la app en flask
load_dotenv()

app = Flask(__name__, template_folder='src/Templates')
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT'))
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASS')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

# se instancia el objeto MySQL
mysql = MySQL(app)
# Crear una instancia de TOTP (Time-based One-Time Password)
#totp = pyotp.TOTP(secret_key)


#Guarda el secret_key en la BDD

def save_secret(id):
    try:
        with app.app_context():
            key = pyotp.random_base32()
            salt = bcp.gensalt()
            cursor = mysql.connection.cursor()
            secret_key = bcp.hashpw(key.encode('UTF-8'),salt)
            cursor.execute('UPDATE user SET token = %s WHERE iduser = %s', (secret_key, id))
            mysql.connection.commit()
            cursor.close()
            msg = 'Se ha agregado 2FA con éxito'
            return {'message' : msg, 'clave' : key}
    except ValueError as e:
        print(e)


def modify_pass(id, data):
    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT token FROM user WHWRE iduser=%s', (id,))
            key = cursor.fetchone()
            cursor.close()
            if key:
                secret_key = key[0]
                totp = pyotp.TOTP(secret_key)
                if totp.verify(data.get('TOTP')):
                    return True
            return False
    except ValueError as e:
        print(e)

'''

def verificar_codigo(codigo_ingresado, secret_key):
    # Crear una instancia de TOTP con la clave secreta proporcionada
    
    
    # Verificar el código ingresado
    return totp.verify(codigo_ingresado)

codigo_ingresado = input("Ingresa el codigo: ")

if verificar_codigo(codigo_ingresado, secret_key):
    print("El código ingresado es valido: ")
    resultado = True
else:
    print("Código invaido : ")
    resultado = False

print("El resultado es: ", resultado)

'''