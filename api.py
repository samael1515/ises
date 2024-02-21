from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import pandas as pd
import json
import sqlite3
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

users = {"user": "password"}

def initialize_database():
    try:
        conn = sqlite3.connect('files.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS files
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           file_type TEXT NOT NULL,
                           file_content TEXT NOT NULL)''')
        conn.commit()
        conn.close()
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print("Error al inicializar la base de datos:", e)

if not os.path.exists('files.db'):
    initialize_database()

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username in users and users[username] == password:
        access_token = create_access_token(identity=username)
        print("Token de autorización:", access_token)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Credenciales inválidas"}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify({'mensaje': '¡Ruta protegida!'})

def read_csv(file):
    try:
        data = pd.read_csv(file, encoding='utf-8')
        data.fillna(0, inplace=True)
        data = data.astype(str)
        print("Datos leídos correctamente:", data)
        return data
    except Exception as e:
        print("Error al leer el archivo CSV:", e)
        return None

def insert_file_data(file_type, file_content):
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO files (file_type, file_content) VALUES (?, ?)", (file_type, json.dumps(file_content.to_dict(orient='records'))))
    conn.commit()
    conn.close()

def basic_analysis(data, selected_columns=None):
    analysis_result = {}
    data = data.dropna()
    if selected_columns:
        data = data[selected_columns]
    data = data.apply(pd.to_numeric, errors='coerce')
    data = data.dropna()
    if data.empty:
        return {'mensaje': 'No hay columnas numéricas en el conjunto de datos después de la conversión'}, []
    numeric_columns = data.select_dtypes(include=['number'])
    means = numeric_columns.mean()
    analysis_result['media'] = means.to_dict()
    std_devs = numeric_columns.std()
    analysis_result['desviacion_estandar'] = std_devs.to_dict()
    correlation_matrix = numeric_columns.corr()
    analysis_result['correlacion'] = correlation_matrix.to_dict()
    column_names = list(numeric_columns.columns)
    return analysis_result, column_names

@app.route('/analisis-basico', methods=['POST'])
@jwt_required()
def basic_data_analysis():
    try:
        file_type = request.form.get('tipo')
        file = request.files.get('ruta')
        print("Tipo de archivo recibido:", file_type)
        print("Nombre del archivo recibido:", file.filename)
        if file_type == 'csv':
            data = read_csv(file)
            if data is not None:
                analysis_result, column_names = basic_analysis(data)
                return jsonify({'resultado': analysis_result, 'columnas': column_names}), 200
            else:
                return jsonify({'mensaje': 'No se pudieron leer los datos del archivo CSV'}), 400
        elif file_type == 'json':
            pass
        else:
            return jsonify({'mensaje': 'Tipo de archivo no soportado'}), 400
    except Exception as e:
        print("Error interno en el servidor:", e)
        return jsonify({'mensaje': 'Error interno en el servidor'}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
