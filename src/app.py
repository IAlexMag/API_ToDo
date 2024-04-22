from flask import Flask, request, session, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from service.login import *
from service.otp import *
import os
load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT'))
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASS')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')


mysql = MySQL(app)


@app.route("/", methods = ['GET'])
def index():
    print(request.endpoint)
    return jsonify({'message' : 'Hola'})

@app.route("/register", methods = ['POST'])
def registro():
    try:
        if request.method == 'POST':
                data = request.json
                msg = save_user(data)
                return jsonify({'message' : msg})
        else:
            return jsonify({'message' : 'Método inválido'})
    except ValueError as e:
        return jsonify({'message' : e})

@app.route('/login', methods = ['POST'])
def login():
    try:
        if request.method == 'POST':
            data = request.json
            user = validate_user(data)
            if user:
                session['user_id'] = user[0]
                session['logged_in'] = True
                print(session)
                return jsonify({'message' : 'se ha iniciado sesión con éxito',
                                'Nombre de usuario' : user[3]})
            else:
                return jsonify({'message' : 'Correo o contraseña inválidos'})
        else:
            return jsonify({'message' : 'método inválido'})
    except ValueError as e:
        return jsonify({'message' : e})
    
@app.route('/logout')
def logout():
    try:
        session.clear()
        return jsonify({'message' : 'se ha cerrado sesión con éxito'})
    except ValueError as e:
        return jsonify({'message' : e})



@app.route('/list_users', methods = ['GET'])
def list_users():
    try:
        if 'user_id' in session:
            if request.method == 'GET':
                lis = users() 
                usuarios = []
                for i in lis:
                    usuario = {'Id de usuario' : i[0], 'Correo' : i[1]}
                    usuarios.append(usuario)
                return jsonify({'usuarios' : usuarios})
            else:
                return jsonify({'message': 'Método inválido'})
        else:
            return jsonify({'message' : 'es necesario inicie sesión'})
    except ValueError as e:
        return jsonify({'message': e})


@app.route('/delete_user/<usuario>', methods = ['DELETE'])
def delete_user(usuario):
    try:
        if 'user_id' in session:    
            mail = usuario
            user = exists_users(mail)
            if user is not None and session['user_id'] != user[0]:
                msg = delete_users(user)
                return jsonify({'mensaje' : msg})
            else:
                msg = 'Usuario no encontrado o activo en la sesión en curso'
                return jsonify({'mensaje' : msg})
        else:
            return jsonify({'mensaje' : 'es necesario inicie sesión'})
    except ValueError as ex:
        return jsonify({'mensaje' : ex})

@app.route('/update_user/<id>', methods = ['PUT'])
def update_users(id):
    try:
        if 'user_id' in session:
            data = id
            val = val_user(data)
            if val is not None:
                user = request.json
                msg = update_user(user, data)
                return jsonify({'mensaje' : msg})
            else:
                msg = 'Uusario no encontrado'
                return jsonify({'mensaje' : msg})
        else:
            msg = 'Es necesario inicie sesión'
            return jsonify({'mensaje' : msg})
    except ValueError as e:
        return jsonify({'mensaje' : e})


@app.route('/two_factor', methods = ['PUT'])
def add_two_factor():
    if 'user_id' in session:
        id = session['user_id']
        msg = validate_mfa(id)
        if msg is None:
            result = save_secret(id)
            return jsonify({'message' : result.get('message'), 'clave' : result.get('clave')})
        else:
            return jsonify({'message' : 'Usuario no encontrado o con veriicación en dos pasos ya activa'})

    else:
        return jsonify({'message' : 'Es necesario inicie sesión'})


@app.route('/change_pass', methods = ['PUT'])
def change_password():
    if 'user_id' in session:
        id = session['user_id']
        msg = validate_mfa(id)
        if msg is not None:
            data = request.json
            msg = modify_pass(id, data)
        else:
            return jsonify({'message' : 'Es necesario se agregue 2FA'})
    else:
        return jsonify({'message' : 'Es necesario inicie sesión'})

def method_not(error):
    return "<h1> El método seleccionado no es permitido para esta ruta </h1>", 405

def not_found(error):
    return"<h1> La página o ruta ingresada no ha sido encontrada </h1>", 404




if __name__ == "__main__":
    app.register_error_handler(405, method_not)
    app.register_error_handler(404, not_found)
    app.run(host='0.0.0.0', port=7796, debug=True)