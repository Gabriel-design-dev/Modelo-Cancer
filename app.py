from flask import Flask,jsonify,flash
from flask import render_template, request, redirect
from flask import Flask, request, Response, render_template, send_file
from flask import Flask,  render_template, request, redirect, url_for, session # pip install Flask
from flask_mysqldb import MySQL,MySQLdb # pip install Flask-MySQLdb
from os import path #pip install notify-py
from openpyxl import Workbook
#librerias para reportes..
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet  # Agrega esta línea
from reportlab.platypus import Paragraph
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle 
from reportlab.lib.colors import HexColor
#librerias para cancer bucal..
import pickle
import numpy as np
import io
import os
from PIL import Image
from PIL import Image 
import pdfkit
#pdf
from reportlab.pdfgen import canvas
from io import BytesIO


app = Flask(__name__,template_folder='template')
app.secret_key = "pinchellave"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cancer'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# Configura pdfkit para usar wkhtmltopdf
config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')  # Reemplaza con la ruta correcta a wkhtmltopdf
@app.route('/generar_pdf')
def generar_pdf():
    user_id = session.get('id')

    # Realiza la consulta del historial del paciente
    cur = mysql.connection.cursor()
    cur.execute("SELECT u.edad, u.genero, c.preg1, c.prediccion,fecha_registro FROM usuarios u JOIN cuestionario c ON u.id = c.id_usu WHERE u.id = %s", (user_id,))
    resultado = cur.fetchall()

    # Realiza la consulta del último diagnóstico
    cur.execute("SELECT c.prediccion FROM cuestionario c WHERE c.id_usu = %s ORDER BY c.id DESC LIMIT 1", (user_id,))
    ultimo_prediccion = cur.fetchone()

    # Crear un nuevo PDF
    pdf_buffer = generar_contenido_pdf(resultado, ultimo_prediccion)

    # Devolver el PDF como respuesta
    response = Response(pdf_buffer.getvalue(), content_type='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=resultado.pdf'
    return response

def generar_contenido_pdf(resultado, ultimo_prediccion):
    # Crear un buffer de bytes para almacenar el PDF
    buffer = BytesIO()

    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Lista de elementos para el PDF
    elements = []

    # Agregar el título
    elements.append(titulo("RESULTADO DEL DIAGNÓSTICO"))
    
    # Agregar el nombre del paciente
    nombre_paciente = session.get('nombre')
    elements.append(parrafo(f"Nombre Completo del Paciente: {nombre_paciente}"))

    # Agregar el historial del paciente
    historial_data = [["Consulta", "Edad", "Género", "Síntoma", "Predicción","Fecha"]]
    for i, resultado in enumerate(resultado):
        consulta = i + 1
        edad = resultado['edad']  # Aquí deberías usar el índice correcto para cada columna en tus resultados
        genero = resultado['genero']
        sintoma = resultado['preg1']
        prediccion = resultado['prediccion']
        fecha=resultado['fecha_registro']
        historial_data.append([consulta, edad, genero, sintoma, prediccion,fecha])

    # Crear la tabla para el historial del paciente
    table = Table(historial_data)

    # Establecer estilo a la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0, 0, 0)),
        ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), (0.9, 0.9, 0.9)),
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0))
    ])

    table.setStyle(style)

    elements.append(cabecera("Historial del Paciente"))
    elements.append(table)

    # Agregar el último diagnóstico
    elements.append(cabecera("Último Diagnostico"))
    elements.append(mensaje(f"Diagnóstico: {ultimo_prediccion['prediccion']}"))

    #Agregar Recomendaciones
    elements.append(cabecera("Recomendaciones"))
    #Recomendaciones
    elements.append(recomendacion("La prevención del cáncer bucal es fundamental para mantener una buena salud oral. Para reducir el riesgo de desarrollar esta enfermedad, se recomienda adoptar hábitos saludables, como evitar el consumo de tabaco y alcohol en exceso, mantener una higiene bucal adecuada, y realizar revisiones dentales periódicas. Además, es importante llevar una dieta equilibrada rica en frutas y verduras, ya que algunos nutrientes pueden ayudar a proteger contra el cáncer bucal. Sin embargo, ningún método de prevención es infalible, por lo que es esencial que cualquier persona que presente síntomas sospechosos, como llagas persistentes, cambios en la voz o dificultades al tragar, consulte a un médico especializado en oncología oral para un diagnóstico y tratamiento adecuados, garantizando así su mejor salud y bienestar."))
    # Construir el PDF
    doc.build(elements)

    # Reiniciar el buffer al principio
    buffer.seek(0)

    return buffer

def cabecera(texto):
       # Crear un estilo personalizado
    estilo = ParagraphStyle(
        name='CustomHeading',  # Nombre del estilo
        fontSize=18,           # Tamaño de fuente
        alignment=1,           # Alineación centrada (0=izquierda, 1=centro, 2=derecha)
        fontName='Times-bold',  # Tipo de fuente
        spaceAfter=23,  # Espacio después del párrafo
        spaceBefore=20  # Espacio antes del párrafo
    )

    # Crear el párrafo con el estilo personalizado
    p = Paragraph(texto, estilo)
    
    return p

def parrafo(texto):
       # Crear un estilo personalizado para los párrafos normales
    estilo = ParagraphStyle(
        name='CustomHeading',  # Nombre del estilo
        fontSize=15,           # Tamaño de fuente
        alignment=1,           # Alineación centrada (0=izquierda, 1=centro, 2=derecha)
        fontName='Times-roman', # Tipo de fuente
        spaceAfter=10,         # Espacio después del párrafo
        spaceBefore=0, 
        leading=22, # Espacio antes del párrafo
        textColor=HexColor('#323331'),  # Color de texto (blanco en este ejemplo)
        backColor=HexColor('#E9EAE8'),  # Color de fondo (azul en este ejemplo)
        borderPadding=8,       # Espacio entre el texto y el borde
        borderWidth=1,         # Ancho del borde
        borderColor=HexColor('#E9EAE8'),  # Color del borde (negro en este ejemplo)
        borderRadius=5,        # Radio de borde (bordes redondeados)
    )

    # Crear el párrafo con el estilo personalizado
    p = Paragraph(texto, estilo)
    
    return p
def mensaje(texto):
       # Crear un estilo personalizado para los Mensajes normales
    estilo = ParagraphStyle(
        name='CustomHeading',  # Nombre del estilo
        fontSize=16,           # Tamaño de fuente
        alignment=1,           # Alineación centrada (0=izquierda, 1=centro, 2=derecha)
        fontName='Times-roman', # Tipo de fuente
        spaceAfter=10,         # Espacio después del párrafo
        spaceBefore=0, 
        leading=22, # Espacio antes del párrafo
        textColor=HexColor('#323331'),  # Color de texto (blanco en este ejemplo)
        backColor=HexColor('#E9EAE8'),  # Color de fondo (azul en este ejemplo)
        borderPadding=8,       # Espacio entre el texto y el borde
        borderWidth=1,         # Ancho del borde
        borderColor=HexColor('#DEDFDD'),  # Color del borde (negro en este ejemplo)
        borderRadius=5,        # Radio de borde (bordes redondeados)
    )

    # Crear el párrafo con el estilo personalizado
    p = Paragraph(texto, estilo)
    
    return p
def recomendacion(texto):
       # Crear un estilo personalizado para los Mensajes normales
    estilo = ParagraphStyle(
        name='CustomHeading',  # Nombre del estilo
        fontSize=12,           # Tamaño de fuente
        alignment=1,           # Alineación centrada (0=izquierda, 1=centro, 2=derecha)
        fontName='Times-roman', # Tipo de fuente
        spaceAfter=10,         # Espacio después del párrafo
        spaceBefore=0, 
        leading=22, # Espacio antes del párrafo
        textColor=HexColor('#395D19'),  # Color de texto (blanco en este ejemplo)
        backColor=HexColor('#C9F79F'),  # Color de fondo (azul en este ejemplo)
        borderPadding=8,       # Espacio entre el texto y el borde
        borderWidth=1,         # Ancho del borde
        borderColor=HexColor('#C9F79F'),  # Color del borde (negro en este ejemplo)
        borderRadius=5,        # Radio de borde (bordes redondeados)
    )

    # Crear el párrafo con el estilo personalizado
    p = Paragraph(texto, estilo)
    
    return p
def titulo(texto):
   # Crear un estilo personalizado
    estilo = ParagraphStyle(
        name='CustomHeading',  # Nombre del estilo
        fontSize=22,           # Tamaño de fuente
        alignment=1,           # Alineación centrada (0=izquierda, 1=centro, 2=derecha)
        fontName='Times-Bold',  # Tipo de fuente
        spaceAfter=27,  # Espacio después del párrafo
        spaceBefore=30  # Espacio antes del párrafo
    )

    # Crear el párrafo con el estilo personalizado
    p = Paragraph(texto, estilo)
    
    return p
#subiendo el archivo de cancer bucal generado en jupyter
phish_model_cancer = pickle.load(open(r'c:\Users\GABRIEL\Pictures\Tesis Gabriel\PROTOTIPO DE TESIS\tesis phising\tesis_cancer\modelo_cancer_bucal.pkl', 'rb'))

@app.route('/cancer_predict', methods = ["GET", "POST"])
def cancer_predict():

    # Cargar el modelo de detección de cáncer bucal
    phish_model_cancer = pickle.load(open(r'c:\Users\GABRIEL\Pictures\Tesis Gabriel\PROTOTIPO DE TESIS\tesis phising\tesis_cancer\modelo_cancer_bucal.pkl', 'rb'))
    
    # Obtener la imagen enviada por el cliente
    file = request.files['file']

    # Verificar si el campo de archivo está vacío
    if file.filename == '':
        mensajes="Por favor seleecione una imagen antes de proceder"
        return render_template("prediccion.html", sms=mensajes)

    # Obtener la ruta temporal para guardar la imagen
    temp_path = "temp_img.jpg"
    file.save(temp_path)

    # Realizar la predicción utilizando el modelo cargado
   
    # Loading Image
    img = Image.open(temp_path)
    img = img.resize((256, 256))  # Redimensionar la imagen a 256x256
    # Normalizing Image
    norm_img = np.array(img) / 255
    # Converting Image to Numpy Array
    input_arr_img = np.array([norm_img])
        # Getting Predictions
    pred = (phish_model_cancer.predict(input_arr_img) > 0.5).astype(int)[0][0]

    # Eliminar la imagen temporal
    os.remove(temp_path)
    
    # Return Model Prediction
 
        
        
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cuestionario")
    roles = cur.fetchall()
    cur.close()
    user_id=session.get('id')

    if request.method == 'GET':
        return render_template("prediccion.html", tipo = roles )
    
    else:
        name = request.form['txtNombre']
        preg1 = request.form['txtPreg1']
        preg2 = request.form['txtPreg2']
        preg3 = request.form['txtPreg3']
        preg4 = request.form['txtPreg4']
    
    if pred == 0:
        print("Cancer")
        resu = 'Presenta Sintomas de Cancer'
      
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO cuestionario (nombre, preg1, preg2, preg3, preg4,id_usu, prediccion) VALUES (%s,%s,%s,%s,%s,%s,%s)", (name, preg1, preg2, preg3, preg4,user_id,resu))
        mysql.connection.commit()
    else:
        print("No tiene Cancer")
        resu = 'No Presenta Sintomas de Cancer'  
      
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO cuestionario (nombre, preg1, preg2, preg3, preg4,id_usu,prediccion) VALUES (%s,%s,%s,%s,%s,%s,%s)", (name, preg1, preg2, preg3, preg4,user_id,resu))
        mysql.connection.commit()
        
    # Ejemplo de respuesta (ajusta esto según la estructura de tu modelo y tus necesidades)
    return render_template("res.html", pred=resu)


 
#pagina de prediccion
@app.route('/prediccion')
def cancer():
    return render_template('prediccion.html')



#pagina inicio (index)
@app.route('/')
def index():
    return render_template('index.html')    

#----------- LOGIN --------------------------
@app.route('/acceso-login', methods= ["GET", "POST"])
def login():
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE correo = %s AND password = %s', (_correo, _password,))
        account = cur.fetchone()
        print(account)
        if account:
            session['logueado'] = True
            session['id'] = account['id']
            session['nombre'] = account['nombre']
            session['correo'] = account['correo']
            session['edad'] = account['edad']
            session['password'] = account['password']
            session['id_rol'] = account['id_rol']
            mensaje5="Inicio de Sesion Exitoso"

            if session['id_rol'] == 1:
                    return render_template("admin.html")
            elif session['id_rol'] == 2:
                    
                    return render_template("prediccion.html",mensajeinicio=mensaje5)
            print(account[0])
        else:
            print("error de ingreso")
            return render_template('index.html',mensaje="Usuario O Contraseña Incorrectas")
  
    return render_template('index.html')
#resultados
@app.route('/resultado', methods=["GET", "POST"])
def mostrar_resultado():
    user_id = session.get('id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT u.edad, u.genero, c.preg1, c.prediccion,c.fecha_registro FROM usuarios u JOIN cuestionario c ON u.id = c.id_usu WHERE u.id = %s", (user_id,))
    resultados = cur.fetchall()
    
    #2da consulta que muestra solo el ultimo dato
    cur.execute("SELECT c.prediccion FROM cuestionario c WHERE c.id_usu = %s ORDER BY c.id DESC LIMIT 1", (user_id,))
    ultimo_prediccion = cur.fetchone()
    
    cur.close()
    print(resultados)  # Imprime los resultados en la consola para verificar si hay datos.
    print(ultimo_prediccion)
    ultimo_prediccion_valor = ultimo_prediccion['prediccion']  # Obtener el valor de la prediccion

    return render_template('resultado.html', resultados=resultados, ultimo_prediccion=ultimo_prediccion_valor)  # Aquí utilizas 'resultados' en lugar de 'resultado'

@app.route('/res')
def res():
    mensaje = None
    if 'message' in flash:
        mensaje = flash['message']
    return render_template('res.html', mensaje=mensaje)

#---REGISTRO DE USUARIOS------------
@app.route('/registro')
def reg():
    return render_template('registro.html')

@app.route('/registro-crear', methods = ["GET", "POST"])
def registro():
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM roles")
    roles = cur.fetchall()
    cur.close()


    if request.method == 'GET':
        return render_template("registro.html", tipo = roles )
    
    else:
        name = request.form['txtNombre']
        carnet= request.form['txtCarnet']
        genero = request.form['txtGenero']
        edad = request.form['txtEdad']
        email = request.form['txtCorreo']
        password = request.form['txtPassword']
      

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE correo=%s",(email,))
        result = cur.fetchone()
        if result:
            return render_template("index.html",resultado="El Usuario Ya Existe")
        
        cur.execute("INSERT INTO usuarios (nombre,carnet,genero,edad,correo, password, id_rol) VALUES (%s,%s,%s,%s,%s,%s,'2')", (name,carnet,genero,edad,email, password))
        mysql.connection.commit()
        
        return render_template('index.html',mensaje2="Registro Exitoso")

#CREACION DE CUESTIONARIO

#MOSTRAR RESULTADOS DEL USUARIO
    
#pagina de resultado
@app.route('/resultado')
def resultado():
    return render_template('resultado.html')

#<---------------SECTOR ADMINISTRADOR------------------->

#funcion pagina --- Mostrar Usuarios en Pagina de administrador
@app.route('/admin_usuarios', methods = ["GET", "POST"])
def mostrar_mensajes():
    
     cur = mysql.connection.cursor()
     cur.execute("SELECT * FROM usuarios ")
     usuarios_admin = cur.fetchall()
     cur.close()
     return render_template('admin_usuarios.html', usuarios_ad = usuarios_admin )  

#pagina de admin ususarios 
@app.route('/admin_usuarios')
def admin_usuarios():
    return render_template('admin_usuarios.html')

#pàgina de admin
@app.route('/admin')
def admin():
    return render_template('admin.html')

#pagina para mostrar las predicciones
@app.route('/admin_predicciones', methods=["GET", "POST"])
def admin_predicciones():
    #user_id = session.get('id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT u.nombre, u.edad, u.genero, c.preg1, c.prediccion FROM usuarios u JOIN cuestionario c ON u.id = c.id_usu WHERE u.id")
    predicciones = cur.fetchall()
    return render_template('admin_predicciones.html', predicciones=predicciones)  # Aquí utilizas 'resultados' en lugar de 'resultado'

@app.route('/admin_predicciones')
def admin_pred():
    return render_template('admin_predicciones.html')

#pagina para ver los usuarios con cancer
@app.route('/admin_us_cancer', methods=["GET", "POST"])
def admin_us_cancer():
    #user_id = session.get('id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT u.nombre, u.edad, u.genero, c.preg1, c.prediccion FROM usuarios u JOIN cuestionario c ON u.id = c.id_usu WHERE u.id AND c.prediccion = 'Presenta Sintomas de Cancer';")
    predicciones = cur.fetchall()
    return render_template('admin_us_cancer.html', predicciones=predicciones)  # Aquí utilizas 'resultados' en lugar de 'resultado'

@app.route('/admin_us_cancer')
def admin_usu_cancer():
    return render_template('admin_us_cancer.html')

#pagina para ver los usuarios que no tienen cancer
@app.route('/admin_us_sin_cancer', methods=["GET", "POST"])
def admin_us_sin_cancer():
    #user_id = session.get('id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT u.nombre, u.edad, u.genero, c.preg1, c.prediccion FROM usuarios u JOIN cuestionario c ON u.id = c.id_usu WHERE u.id AND c.prediccion = 'No Presenta Sintomas de Cancer';")
    predicciones = cur.fetchall()
    return render_template('admin_us_sin_cancer.html', predicciones=predicciones)  # Aquí utilizas 'resultados' en lugar de 'resultado'
#pagina para ver a los usuarios sin cancer
@app.route('/admin_us_sin_cancer')
def admin_usu_sin_cancer():
    return render_template('admin_us_sin_cancer.html')


if __name__ == '__main__':
   
   app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
