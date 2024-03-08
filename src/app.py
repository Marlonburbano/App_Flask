from flask import Flask, render_template, request, redirect, url_for,session, flash, get_flashed_messages
from config import config

from flask_mysqldb import MySQL

from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate
from flask import send_from_directory
from passlib.hash import sha256_crypt
import os
import re

from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)

app.secret_key = '97110c78ae51a45af397be6534caef90ebb9b1dcb3380af008f90b23a5d1616bf19bc29098105da20fe'

def dataLoginSesion():
    inforLogin = {
        "idLogin"             :session['id'],
        "tipoLogin"           :session['tipo_user'],
        "nombre"              :session['nombre'],
        "apellido"            :session['apellido'],
        "emailLogin"          :session['email'],
        "telefono"             :session['telefono']
    }
    return inforLogin

def obtener_lista_de_juegos():
    # Retorna la lista de juegos, similar a como lo haces en la ruta /eventos
    return Juego.query.join(Registro).all()


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/juegosdb'
db = SQLAlchemy(app)



class Juego(db.Model):
    __tablename__ = 'juego'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    hora = db.Column(db.String(5), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    lugar = db.Column(db.String(255), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('registro.id'))

    # Corrige la relación utilizando back_populates
    registro = db.relationship('Registro', back_populates='juegos')
 

class Inscrito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), nullable=False)
    semestre = db.Column(db.String(10), nullable=False)
    carrera = db.Column(db.String(100), nullable=False)
     # Agregar un campo de relación con Juego
    juego_id = db.Column(db.Integer, db.ForeignKey('juego.id'))
    juego = db.relationship('Juego', backref='inscritos')


@app.route('/agregar_juego', methods=['POST'])
def agregar_juego():
    if 'conectado' in session:
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        hora = request.form.get('hora')
        fecha = request.form.get('fecha')
        lugar = request.form.get('lugar')

        # Utiliza el id del usuario actual de la sesión
        id_usuario = session['id']

        juego = Juego(nombre=nombre, descripcion=descripcion, hora=hora, fecha=fecha, lugar=lugar, id_usuario=id_usuario)
        db.session.add(juego)
        db.session.commit()

        juegos = obtener_lista_de_juegos()
        return redirect(url_for('index'))
    else:
        return render_template('auth/login.html')



@app.route('/editar_juego/<int:id>', methods=['POST'])
def editar_juego(id):
    if 'conectado' in session:
        juego = Juego.query.get(id)
        if juego is not None:
            juego.nombre = request.form.get('nombre')
            juego.descripcion = request.form.get('descripcion')
            juego.hora = request.form.get('hora')
            juego.fecha = request.form.get('fecha')
            juego.lugar = request.form.get('lugar')
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return render_template('error.html', error='Juego no encontrado')
    else:
        return render_template('error2.html', error='Autenticación obligatoria, Udenar deportes')
    
@app.route('/eliminar_juego/<int:id>')
def eliminar_juego(id):
    if 'conectado' in session:
        juego = Juego.query.get(id)
        db.session.delete(juego)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('error2.html', error='Autenticación obligatoria, Udenar deportes')

@app.route('/inscribirme', methods=['GET', 'POST'])
def inscribirme():
    if 'conectado' in session:
        if request.method == 'POST':
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            codigo = request.form['codigo']
            semestre = request.form['semestre']
            carrera = request.form['carrera']
            juego_id = request.form['juego_id']

            inscrito = Inscrito(nombre=nombre, apellido=apellido, codigo=codigo, semestre=semestre, carrera=carrera, juego_id=juego_id)
            db.session.add(inscrito)
            db.session.commit()

            return redirect(url_for('index'))

        return render_template('inscripcion.html')
    else:
        return render_template('auth/login')
    



class Registro(db.Model):
    __tablename__ = 'registro'
    id = db.Column(db.Integer, primary_key=True)
    tipo_user = db.Column(db.Integer)
    nombre = db.Column(db.String(255))
    apellido = db.Column(db.String(255))
    email = db.Column(db.String(255))
    telefono = db.Column(db.String(15))  # Ajusta la longitud según sea necesario
    password = db.Column(db.String(255))
    
    # Corrige la relación utilizando back_populates
    juegos = db.relationship('Juego', back_populates='registro')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory (os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def inicio():
    return render_template('inicio.html')



@app.route('/registro')
def registro():
        return render_template('auth/registro.html')


@app.route('/login')
def login():
    if 'conectado' in session:
        juegos = obtener_lista_de_juegos()
        return render_template('error3.html', error='Peligro!!')
    else:
        return render_template('auth/login.html')

@app.route('/registro-usuario', methods=['GET', 'POST'])
def registerUser():
    if request.method == 'POST':
        tipo_user = 2
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        password = request.form['password']
        repite_password = request.form['repite_password']
        telefono = request.form['telefono']

        
        # Validación de contraseñas
        if password != repite_password:
            flash('Disculpa, las claves no coinciden!', 'error')
            return redirect(url_for('registro'))

        # Comprobando si ya existe la cuenta de Usuario con respecto al email
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM registro WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            flash('Ya existe el Email!', 'error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Disculpa, formato de Email incorrecto!', 'error')
        elif not email or not password or not repite_password:
            flash('El formulario no debe estar vacío!', 'error')
        else:
            # La cuenta no existe y los datos del formulario son válidos,
            password_encriptada = sha256_crypt.encrypt(str(password))
            cursor.execute('INSERT INTO registro (tipo_user, nombre, apellido, email, telefono, password) VALUES (%s, %s, %s, %s, %s, %s)',
                           (tipo_user, nombre, apellido, email, telefono, password_encriptada))
            mysql.connection.commit()
            flash('Cuenta creada correctamente!', 'success')
            cursor.close()

            session['flash_messages'] = list(get_flashed_messages())
            # Redirigir al usuario a la página de inicio de sesión
            return redirect(url_for('login'))

    # Si hay algún error, o es una solicitud GET, redirigir a la página de registro
    return redirect(url_for('registro'))

@app.route('/dashboard', methods=['GET', 'POST'])
def loginUser():
    if 'conectado' in session:
            if session['tipo_user'] ==1:
                        juegos = obtener_lista_de_juegos()
                        return redirect(url_for('index'))
            elif session['tipo_user'] ==2:
                        juegos = obtener_lista_de_juegos()
                        return redirect(url_for('indexusu')) 
    else:
        msg = ''
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
            email = str(request.form['email'])
            password = str(request.form['password'])

            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM registro WHERE email = %s", [email])

            # Obtener la información sobre las columnas
            columns = [column[0] for column in cursor.description]

            # Obtener la primera fila del resultado de la consulta
            account = cursor.fetchone()

            if account:
                account_dict = dict(zip(columns, account))  # Convertir la tupla a un diccionario
                if sha256_crypt.verify(password, account_dict['password']):
                    # Crear datos de sesión, para poder acceder a estos datos en otras rutas 
                    session['conectado'] = True
                    session['id'] = account_dict['id']
                    session['tipo_user'] = account_dict['tipo_user']
                    session['nombre'] = account_dict['nombre']
                    session['apellido'] = account_dict['apellido']
                    session['email'] = account_dict['email']
                    session['telefono'] = account_dict['telefono']

                    if session['tipo_user'] ==1:
                        flash("Ha iniciado sesión correctamente admin.", 'success')
                        juegos = obtener_lista_de_juegos()
                        return redirect(url_for('index'))
                    elif session['tipo_user'] ==2:
                        flash("Ha iniciado sesión correctamente usuario.", 'success')
                        juegos = obtener_lista_de_juegos()
                        return redirect(url_for('indexusu'))
                else:
                    flash('Datos incorrectos, por favor verifique.', 'error')
            else:
                flash('Cuenta no encontrada.', 'error')
            cursor.close()

    return render_template('auth/login.html', messages=get_flashed_messages())



@app.route('/eventos')
def index():
    if 'conectado' in session:
         juegos = obtener_lista_de_juegos()
         return render_template('index.html', juegos=juegos, dataLogin = dataLoginSesion())
    else:
        return render_template('error2.html', error='Autenticación obligatoria, Udenar deportes')

@app.route('/eventosusu')
def indexusu():
    if 'conectado' in session:
         juegos = obtener_lista_de_juegos()
         return render_template('indexusu.html', juegos=juegos, dataLogin = dataLoginSesion())
    else:
        return render_template('error2.html', error='Autenticación obligatoria, Udenar deportes') 


    
@app.route('/noticias')
def noticias():
    if 'conectado' in session:
        return render_template('noticias.html', dataLogin = dataLoginSesion())
    else:
        return render_template('error2.html', error='Autenticación obligatoria, Udenar deportes')

# Ruta para la página de perfil
@app.route('/perfil')
def perfil():

    enlaces = [
    {"url": "http://www.google.com", "icon_class": "fab fa-google"},
    {"url": "http://www.twitter.com", "icon_class": "fab fa-twitter"},
    {"url": "http://www.facebook.com", "icon_class": "fab fa-facebook"},
    # Agrega más enlaces con iconos según sea necesario
]
    # Obtén la información del usuario, como el nombre de usuario, la descripción y la URL de la foto de perfil
    user_data = {
        'username': 'Nombre de Usuario',
        'user_description': 'Descripción corta sobre el usuario',
        'user_foto_perfil': url_for('static', filename='uploads/foto_perfil.jpg'),
    }
    return render_template('perfil.html', **user_data, enlaces=enlaces)

# Ruta para manejar la carga de fotos
@app.route('/cargar_foto', methods=['POST'])
def cargar_foto():
    if 'foto_perfil' in request.files:
        foto_perfil = request.files['foto_perfil']
        # Crea la carpeta 'uploads' si no existe
        os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
        # Guarda la foto en la ubicación deseada (puedes personalizar esto según tus necesidades)
        foto_perfil.save(os.path.join(app.static_folder, 'uploads', 'foto_perfil.jpg'))
        # Actualiza la URL de la foto de perfil en la base de datos o donde sea que la estés almacenando
        # Puedes utilizar una base de datos para almacenar la ruta de la imagen en lugar de guardar directamente en el sistema de archivos
        return redirect(url_for('perfil'))
    return 'Error al subir la foto'



    
@app.route('/inscritos')
def inscritos():
    if 'conectado' in session:
        inscritos = Inscrito.query.all()
        return render_template('inscritos.html', inscritos=inscritos, dataLogin = dataLoginSesion())
    else:
        return render_template('error2.html', error='Autenticación obligatoria, Udenar deportes')

    


@app.errorhandler(404)
def page_not_found(error):
 return render_template("error.html",
 error="Página no encontrada..."), 404

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



@app.route('/logout')
def logout():
    msgClose = ''
    # Eliminar datos de sesión, esto cerrará la sesión del usuario
    session.pop('conectado', None)
    session.pop('id', None)
    session.pop('email', None)
    msgClose ="La sesión fue cerrada correctamente"
    return render_template('inicio.html', msjAlert = msgClose, typeAlert=1)


    
if __name__ == '__main__':
 app.config.from_object(config['development'])
 app.run()