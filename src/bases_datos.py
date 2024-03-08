from flask_mysqldb import MySQL
from flask import Flask, render_template, request, redirect, url_for,session, flash, get_flashed_messages


app = Flask(__name__)

app.config['MYSQL_HOST'] = '127.0.0.1'  # Host de la base de datos
app.config['MYSQL_USER'] = 'root'  # Usuario de la base de datos
app.config['MYSQL_PASSWORD'] = ''  # Contraseña de la base de datos
app.config['MYSQL_DB'] = 'juegosdb'  # Nombre de la base de datos

mysql = MySQL(app)

@app.route('/crear_tabla_registro')
def crear_tabla_registro():
    cursor = mysql.connection.cursor()
    cursor.execute('''
    CREATE TABLE registro (
        id INT AUTO_INCREMENT PRIMARY KEY,
        tipo_user INT(11) NOT NULL,
        nombre VARCHAR(255) NOT NULL,
        apellido VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        telefono VARCHAR(20) NOT NULL,
        password VARCHAR(255) NOT NULL
        
    )
    ''')
    mysql.connection.commit()
    cursor.close()
    return 'Tabla de registro creada'