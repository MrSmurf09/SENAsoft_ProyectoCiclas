from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import bcrypt
import os
import time
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import database as db

app = Flask(__name__)

#--------------------------------------------------- funcion obtener estrato
def obtener_estrato(usuario):
    cursor = db.database.cursor()
    cursor.execute("SELECT usuariousuario, estratousuario FROM usuario WHERE usuariousuario = %s", (usuario,))
    resultado = cursor.fetchone()
    match resultado[1]:
        case 1 | 2:
            descuento = 0.10
        case 3 | 4:
            descuento = 0.05
        case 5 | 6:
            descuento = 0
    
    return descuento

# --------------------------------------------------- Inicio de Sesion
@app.route('/')
def InicioSesion():
    return render_template('InicioSesion.html')

@app.route('/login', methods=['POST'])
def Login():
    try:
        if request.method == 'POST':
            username = request.form['usuariousuario']
            password = request.form['contraseñausuario']

            
            if username == "admin":
                cursor = db.database.cursor()
                cursor.execute("SELECT usuarioadmin, contraseñaadmin FROM admin WHERE usuarioadmin = %s", (username,))
                resultadoadmin = cursor.fetchone()
                cursor.close()
                # verificar admin
                if resultadoadmin[0] == username and resultadoadmin[1] == password:
                    return redirect(url_for('InicioAdmin'))
                else:
                    redirect(url_for('InicioSesion'))
                    
            cursor = db.database.cursor()
            # Seleccionar solo el usuario y la contraseña encriptada de la base de datos
            cursor.execute("SELECT usuariousuario, contraseñausuario FROM usuario WHERE usuariousuario = %s", (username,))
            resultado = cursor.fetchone()
            
            if resultado:
                # Verificar la contraseña con bcrypt
                contraseña_encriptada = resultado[1]  # La contraseña encriptada está en la segunda posición
                if bcrypt.checkpw(password.encode('utf-8'), contraseña_encriptada.encode('utf-8')):
                    session['usuario'] = username
                    return redirect(url_for('InicioUsuario'))
                else:
                    return redirect(url_for('InicioSesion'))
            else:
                return redirect(url_for('InicioSesion'))
        else:
            return redirect(url_for('InicioSesion'))
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for('InicioSesion'))


#---------------------------------------------------- Logout
@app.route('/logout')
def Logout():
    session.pop('usuario', None)  # Eliminar el usuario de la sesión
    return redirect(url_for('InicioSesion'))
    
# --------------------------------------------------- Registrarse
@app.route('/registrar')
def Registrarse():
    return render_template('Registrarse.html')

@app.route('/registrar/usuario', methods=['POST'])
def RegistrarUsuario():
    try:
        if request.method == 'POST':
            usuario = request.form['usuariousuario']
            contraseña = request.form['contraseñausuario']
            tipodocumento = request.form['tipodocumentousuario']
            numerodocumento = request.form['numerodocumentousuario']
            telefono = request.form['telefonousuario']
            email = request.form['emailusuario']
            estrato = request.form['estratousuario']
            rol = request.form['rolusuario']
            if usuario and contraseña and tipodocumento and numerodocumento and telefono and email and estrato and rol:
                # Encriptar la contraseña
                salt = bcrypt.gensalt()
                contraseña_encriptada = bcrypt.hashpw(contraseña.encode('utf-8'), salt)
                cursor = db.database.cursor()
                cursor.execute("INSERT INTO usuario (numerodocumentousuario, tipodocumentousuario, usuariousuario, contraseñausuario, estratousuario, rolusuario, telefonousuario, emailusuario) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (numerodocumento, tipodocumento, usuario, contraseña_encriptada, estrato, rol, telefono, email))
                db.database.commit()
                return redirect(url_for('InicioSesion'))
            else:
                return render_template('Registrarse.html')
        else:
            return render_template('Registrarse.html')
    except Exception as e:
        print(f"Error: {e}")
        return render_template('Registrarse.html')
    
# --------------------------------------------------- Inicio de Usuario
@app.route('/usuario/inicio')
def InicioUsuario():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('InicioUsuario.html', usuario=usuario)
    else:
        return redirect(url_for('Login'))
    
# --------------------------------------------------- Ciclas Usuario
@app.route('/usuario/ciclas')
def CiclasUsuario():
    cursor = db.database.cursor(dictionary=True)
    if 'usuario' in session:
        usuario = session['usuario']
        cursor.execute("SELECT colorcicla, count(*) FROM cicla group by colorcicla having count(*) >= 1")
        colorciclas = cursor.fetchall()
        cursor.execute("SELECT marcacicla, count(*) FROM cicla group by marcacicla having count(*) >= 1")
        marcaciclas = cursor.fetchall()
        return render_template('CiclasUsuario.html', usuario=usuario, colorciclas=colorciclas, marcaciclas=marcaciclas)
    
    
@app.route('/usuario/ciclas/alquilar', methods=['POST'])
def AlquilarCiclasUsuario():
    try:
        if request.method == 'POST':
            colorcicla = request.form['colorcicla']
            marcacicla = request.form['marcacicla']
            precioalquilercicla = request.form['precioalquilercicla']
            if colorcicla and marcacicla and precioalquilercicla:
                if 'usuario' in session:
                    usuario = session['usuario']
                    cursor = db.database.cursor(buffered=True)
                    cursor.execute("SELECT * FROM cicla WHERE colorcicla = %s AND marcacicla = %s and estadocicla = 'Disponible'", (colorcicla, marcacicla))
                    cicla = cursor.fetchone()
                    cursor.execute("SELECT * FROM usuario WHERE usuariousuario = %s", (usuario,))
                    usuarioactual = cursor.fetchone()
                    if cicla:
                        cicla_idcicla = cicla[0]
                        print(cicla_idcicla)
                        usuario_idusuario = usuarioactual[0]
                        print(usuario_idusuario)
                        fecha_actual = datetime.now().date()  # Obtener la fecha actual
                        print(fecha_actual)
                        descuento = obtener_estrato(usuario)
                        precioalquilercicla = int(precioalquilercicla)
                        cursor.execute("INSERT INTO alquiler (cobroalquiler, fechaalquiler, estadoalquiler, cicla_idcicla, usuario_numerodocumentousuario) VALUES (%s, %s, %s, %s, %s)", (precioalquilercicla - (precioalquilercicla * descuento), fecha_actual, "En Deuda", cicla_idcicla, usuario_idusuario))
                        cursor.execute("UPDATE cicla SET estadocicla = 'Ocupada' WHERE idcicla = %s", (cicla_idcicla,))
                        db.database.commit()
                        return redirect(url_for('CiclasUsuario'))
                    else:
                        print("Cicla no disponible")
                        return redirect(url_for('CiclasUsuario'))
                else:
                    print("Usuario no autenticado")
                    return redirect(url_for('InicioUsuario'))
            else:
                print("Faltan datos")
                return redirect(url_for('CiclasUsuario'))
        else:
            print("Faltan datos 2")
            return redirect(url_for('CiclasUsuario'))
    except IntegrityError as e:
        print(e)        
        return redirect(url_for('CiclasUsuario'))
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for('CiclasUsuario'))
    

# --------------------------------------------------- Eventos Usuario
@app.route('/usuario/eventos')
def EventosUsuario():
    cursor = db.database.cursor(dictionary=True)
    if 'usuario' in session:
        usuario = session['usuario']
        cursor.execute("SELECT * FROM evento")
        eventos = cursor.fetchall()
        cursor.close()
        return render_template('EventosUsuario.html', usuario=usuario, eventos=eventos)

# --------------------------------------------------- Perfil Usuario
@app.route('/usuario/perfil')
def PerfilUsuario():
    if 'usuario' in session:
        usuario = session['usuario']
        cursor = db.database.cursor()
        cursor.execute("""SELECT 
                        usuariousuario,
                        emailusuario,
                        numerodocumentousuario,
                        telefonousuario,
                        numerodocumentousuario
                        FROM usuario WHERE usuariousuario = %s""", (usuario,))
        usuarios = cursor.fetchone()
        return render_template('Perfil.html', usuarios=usuarios, usuario = usuario)
    
@app.route('/usuario/perfil/editar', methods=['POST'])
def EditarPerfilUsuario():
    try:
        if request.method == 'POST':
            if 'usuario' in session:
                usuario = session['usuario']
                usuarioactual = request.form['usuariousuario']
                email = request.form['emailusuario']
                numerodocumento = request.form['numerodocumentousuario']
                telefono = request.form['telefonousuario']
                if email and numerodocumento and telefono:
                    cursor = db.database.cursor()
                    cursor.execute("""UPDATE usuario SET 
                                    usuariousuario = %s,
                                    emailusuario = %s,
                                    numerodocumentousuario = %s,
                                    telefonousuario = %s
                                    WHERE usuariousuario = %s""", (usuarioactual, email, numerodocumento, telefono, usuario))
                    db.database.commit()
                    return redirect(url_for('PerfilUsuario'))
                else:
                    print("Faltan datos")
                    redirect(url_for('InicioUsuario'))
            else:
                print("Usuario no autenticado")
                return redirect(url_for('InicioUsuario'))
        else:
            print("metodo incorrecto")
            return redirect(url_for('InicioUsuario'))
    except Exception as e:
        print(f"Error: {e}")
        print("Error en el metodo")
        return redirect(url_for('InicioUsuario'))

# --------------------------------------------------- Inicio de Usuario admin
@app.route('/admin/inicio')
def InicioAdmin():
    return render_template('Inicioadmin.html')
# --------------------------------------------------Ciclas Admin
@app.route('/admin/ciclas')
def CiclasAdmin():
    return render_template('CiclasAdmin.html')
# --------------------------------------------------- Eventos Admin
@app.route('/admin/eventos')
def EventosAdmin():
    return render_template('EventosAdmin.html')

# --- crear eventos
app.config['UPLOAD_FOLDER'] = 'src/static/img/imagenes_eventos'  # Cambia esto a la ruta deseada, debe ser absoluta
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite de 16 MB

@app.route('/admin/eventos', methods=['POST'])
def crear_eventos():
    try:
        if request.method == 'POST':
            titulo = request.form['tituloevento']
            descripcion = request.form['descripcionevento']
            fechahora = request.form['fechahoraevento']
            ubicacion = request.form['ubicacionevento']
            imagen = request.files['imagenevento']
            
            if imagen and titulo and descripcion and fechahora and ubicacion:
                nombre_imagen = guardar_imagen(imagen)
                cursor = db.database.cursor()
                cursor.execute("INSERT INTO evento (tituloevento, descripcionevento, fechahoraevento, ubicacionevento, imagenevento) VALUES (%s, %s, %s, %s, %s)", (titulo, descripcion, fechahora, ubicacion, nombre_imagen))
                db.database.commit()
                return redirect(url_for('EventosAdmin'))
            else:
                return render_template('EventosAdmin.html')
        else:
            return render_template('EventosAdmin.html')
    except IntegrityError as e:
        print(e)        
        return render_template('EventosAdmin.html')
#----------------------------guardar imagen evento
def guardar_imagen(imagen):
    # Obtener la extensión del archivo
    carpeta_destino = app.config['UPLOAD_FOLDER']
    
    # Crear la carpeta si no existe
    os.makedirs(carpeta_destino, exist_ok=True)
    extension = imagen.filename.split('.')[-1]
    nombre_unico = f"{uuid.uuid4()}_{int(time.time())}.{extension}"  # Combinar UUID con timestamp
    imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], nombre_unico)
    imagen.save(imagen_path)
    return nombre_unico


# --------------------------------------------------- Perfil Admin
@app.route('/admin/perfil')
def PerfilAdmin():
    return render_template('PerfilAdmin.html')
# --------------------------------------------------diccionario
@app.route('/admin/diccionario')
def Diccionario_datos_bd_sistemaciclassena():
    return render_template('Diccionario_datos_bd_sistemaciclassena.html')
# --------------------------------------------------fin diccionario

#--------------------------------------------------- Contraseña para session
app.secret_key = 'ciclassena'

if __name__ == '__main__':
    app.run(debug=True, port=5000)