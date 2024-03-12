import os
import socket
import pathlib
import sys
import shutil
from pathlib import Path
'''
Nombres: Hernández Hernández Jorge Gabriel
         Galvan Sanchez Citlalli
Grupo:6CM1
Aplicaciones para Comunicaciones en Red
Profesor: Axel Ernesto Moreno Cervantes 
'''

# Crea un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('127.0.0.1', 1234)
print('\nCliente Conectado: \x1b[1;31m{}\x1b[0m : \x1b[1;31m{}\x1b[0m'.format(*server_address))
sock.connect(server_address)
# Carpeta Local
carpeta = 'local'

#Funcion para ver la Carpeta Local
def verCarpetaLocal():
    print('\n\t\x1b[1;31mCarpeta Local\x1b[0m')
    # Se itera sobre los archivos y carpetas en la carpeta local
    for file in os.listdir(carpeta):
        # Si el archivo no tiene una extensión (es decir, es una carpeta), se imprime como tal
        if '.' not in file:
            print(f"'Carpeta'| {file}")
        # Si el archivo tiene una extensión (es decir, no es una carpeta), se imprime como un archivo
        else:
            print(f"'Archivo'| {file}")

#Funcion para ver la Carpeta Remota
def verCarpetaRemota():
    print('\n\t\x1b[1;31mCarpeta Remota\x1b[0m')
    # Se itera sobre los archivos y carpetas en la carpeta remota
    for file in os.listdir('remota'):
        # Si el archivo no tiene una extensión (es decir, es una carpeta), se imprime como tal
        if '.' not in file:
            print(f"'Carpeta'| {file}")
        # Si el archivo tiene una extensión (es decir, no es una carpeta), se imprime como un archivo
        else:
            print(f"'Archivo'| {file}")

#Funcion para Crear Carpetas en la Carpeta Local
def crear_carperta1(nombre):
    # Cambiar al directorio 'local'
    os.chdir('local')
    # Verificar si la carpeta ya existe
    if os.path.exists(nombre):
        print('La carpeta ya existe')
        sys.stdin.flush()
        data = b'ERROR'
    else:
        # Crear la carpeta y enviar señal de finalización al cliente
        os.makedirs(nombre, exist_ok=True)
        print(nombre, 'Carpeta creada correctamente en la Carpeta Local')
        sys.stdin.flush()
        data = b'DONE'
    os.chdir('..')
    return data

#Funcion para Crear Carpetas en la Carpeta Remota
def crear_carpeta(nombre):
    os.chdir('remota')
    # Verificar si la carpeta ya existe
    if os.path.exists(nombre):
        print('La carpeta ya existe')
        sys.stdin.flush()
        data = b'ERROR'
    else:
        # Crear la carpeta y enviar señal de finalización al cliente
        os.makedirs(nombre, exist_ok=True)
        print(nombre, 'Carpeta creada correctamente en la Carpeta Remota')
        sys.stdin.flush()
        data = b'DONE'
    # Regresar al directorio padre
    os.chdir('..')
    return data

#Función para eliminar un Archivo en la Carpeta cliente
def eliminar_archivo1(nombre):
    print('Eliminando...', nombre)
    # Eliminar el archivo especificado de la carpeta local
    os.unlink(os.path.join('local', nombre))
    print('Archivo eliminado correctamente')
    # Imprimir la confirmación de eliminación del archivo
    print('\n', data.decode())

#Función para eliminar un Archivo en la Carpeta Servidor
def eliminar_archivo(nombre):
    while True:
        # Esperar a recibir datos del cliente
        data = sock.recv(1024)
        # Si el cliente envía la señal de finalización 'DONE'
        if data == b'DONE':
            # Imprimir un mensaje que indica que el archivo ha sido eliminado de la carpeta remota
            print(nombre, 'eliminado de la Carpeta Remota')
            sys.stdin.flush()
            break
    sys.stdin.flush()

#Función para eliminar una Carpeta en la Carpeta Cliente
def eliminar_carpeta1(nombre):
    ruta = 'local/' + nombre
    # Verificar si la carpeta especificada existe en el directorio local
    if os.path.exists(ruta):
        # Eliminar la carpeta especificada
        os.rmdir(ruta)
        print(f'Se ha eliminado la carpeta {nombre} correctamente')
    else:
        print(f'La carpeta {nombre} no existe en el directorio')

#Función para eliminar una Carpeta en la Carpeta Servidor
def eliminar_carpeta(nombre):
    while True:
        # Esperar a que el servidor envíe la señal de finalización
        data = sock.recv(1024)
        # Si se recibe la señal de finalización, imprimir un mensaje indicando que la carpeta ha sido eliminada
        if data == b'DONE':
            print(nombre, 'eliminada de la Carpeta Remota')
            sys.stdin.flush()
            break
    sys.stdin.flush()


#Función para Subir Archivos a la Carpeta Remota
def subir_archivo(nombre):
    # Carpeta Local
    os.chdir(carpeta)
    # Abrir el archivo en modo de lectura binario
    file = open(nombre, "rb")
    # Lee los primeros 1024 bytes del archivo
    data = file.read(1024)
    print("Solicitud enviada...")
    print("Subiendo Archivo a la Carpeta Local...")
    # Mientras hay datos en el archivo
    while data:
        # Envia los datos a través del socket
        sock.send(data)
        # Lee los siguientes 1024 bytes del archivo
        data = file.read(1024)
        # Limpiar el buffer del teclado
        sys.stdin.flush()
    # Cerrar el archivo
    file.close()
    # Cambiar al directorio anterior
    os.chdir('..')
    # Indica que se ha completado la transferencia del archivo
    sock.send(b"DONE")
    print(nombre, "subido a la Carpeta Remota")

#Función para Subir Carpeta a la Carpeta Remota
def subir_carpeta(nombre):
    # Cambia el directorio de trabajo al directorio de la carpeta a comprimir
    os.chdir(carpeta)
    # Comprime la carpeta en formato zip
    shutil.make_archive(nombre, "zip", nombre)
    # Abre el archivo zip y lo lee en pequeños fragmentos
    file = open(nombre+'.zip', "rb")
    data = file.read(1024)
    # Envia el archivo en fragmentos hasta que se envíe todo el archivo
    print("Subiendo...")
    while data:
        sock.send(data)
        data = file.read(1024)
        sys.stdin.flush()
    sys.stdin.flush()
    file.close()
    # Eliminar el archivo zip del directorio local
    os.unlink(nombre+'.zip')
    # Cambiar el directorio de trabajo al directorio padre
    os.chdir('..')
    # Enviar una señal de finalización al servidor
    sock.send(b"DONE")
    print(nombre, "enviado a la Carpeta Remota")

#Función para Descargar Archivos a la Carpeta Local
def descargar_archivo(nombre):
    # Cambia el directorio de trabajo a la carpeta local
    os.chdir(carpeta)
    # Crea el archivo en la carpeta local
    file = open(nombre, "wb")
    print("Descargando...", nombre)
    while True:
        # Recibir los datos del archivo desde el servidor
        data = sock.recv(1024)
        if data == b"DONE":
            # Si se recibe la señal de finalización, el archivo se ha descargado correctamente
            print(nombre, "descargado \n")
            sys.stdin.flush()
            break
        # Escribir los datos recibidos en el archivo
        file.write(data)
        sys.stdin.flush()
    sys.stdin.flush()
    # Cerrar el archivo
    file.close()

#Función para Descargar Careptas a la Carpeta Local
def descargar_carpeta(nombre):
    # Cambia el directorio de trabajo actual a la carpeta local
    os.chdir(carpeta)
    # Crea una nueva carpeta con el nombre especificado
    os.makedirs(nombre)
    # Cambia el directorio de trabajo actual a la nueva carpeta
    os.chdir(nombre)
    # Abre un archivo en modo binario para escritura
    file = open(nombre + '.zip', "wb")
    # Imprime un mensaje de estado
    print("Descargando carpeta...", nombre)
    # Recibe datos del socket en bloques de 1024 bytes hasta que recibe la señal "DONE"
    while True:
        data = sock.recv(1024)
        if data == b"DONE":
            # Imprime un mensaje de descarga completa si se recibe la señal "DONE"
            print("Descarga completa. \n")
            sys.stdin.flush()
            break
        # Escribe los datos recibidos en el archivo
        file.write(data)
        sys.stdin.flush()
    # Cierra el archivo
    file.close()
    # Extrae los archivos del archivo ZIP descargado
    shutil.unpack_archive(nombre + '.zip')
    # Elimina el archivo ZIP descargado
    os.unlink(nombre + '.zip')
    os.chdir('..')
    os.chdir('..')

# Función para Renombrar Archivos de la Carpeta Local
def renombrar_archivo1(nombre_actual, nuevo_nombre):
    # Se especifica la ruta actual del archivo a renombrar
    ruta_actual = 'local/' + nombre_actual
    # Se especifica la ruta nueva que tendrá el archivo renombrado
    ruta_nueva = 'local/' + nuevo_nombre
    # Se verifica si el archivo existe en la ruta actual
    if os.path.exists(ruta_actual):
        # Se renombra el archivo con la función "os.rename()"
        os.rename(ruta_actual, ruta_nueva)
        # Se imprime un mensaje de éxito
        print(f'Se ha renombrado el archivo {nombre_actual} a {nuevo_nombre} correctamente')
    else:
        # Se imprime un mensaje de error si el archivo no existe
        print(f'El archivo {nombre_actual} no existe en la ruta especificada')

# Función para Renombrar Archivos de la Carpeta Remota
def renombrar_archivo(nombre_actual, nuevo_nombre):
    # Se especifica la ruta actual del archivo a renombrar
    ruta_actual = 'remota/' + nombre_actual
    # Se especifica la ruta nueva que tendrá el archivo renombrado
    ruta_nueva = 'remota/' + nuevo_nombre
    # Se verifica si el archivo existe en la ruta actual
    if os.path.exists(ruta_actual):
        # Se renombra el archivo con la función "os.rename()"
        os.rename(ruta_actual, ruta_nueva)
        # Se imprime un mensaje de éxito
        print(f'Se ha renombrado el archivo {nombre_actual} a {nuevo_nombre} correctamente')
    else:
        # Se imprime un mensaje de error si el archivo no existe
        print(f'El archivo {nombre_actual} no existe en la ruta especificada')


# Función para Renombrar Carpetas de la Carpeta Local
def renombrar_carpeta1(nombre_actual, nuevo_nombre):
    # Se especifica la ruta actual de la carpeta a renombrar
    ruta_actual = 'local/' + nombre_actual
    # Se especifica la ruta nueva que tendrá la carpeta renombrada
    ruta_nueva = 'local/' + nuevo_nombre
    # Se verifica si la carpeta existe en la ruta actual
    if os.path.exists(ruta_actual):
        # Se renombra la carpeta con la función "os.rename()"
        os.rename(ruta_actual, ruta_nueva)
        # Se imprime un mensaje de éxito
        print(f'Se ha renombrado la carpeta {nombre_actual} a {nuevo_nombre} correctamente')
    else:
        # Se imprime un mensaje de error si la carpeta no existe
        print(f'La carpeta {nombre_actual} no existe en la ruta especificada')

# Función para Renombrar Carpetas de la Carpeta Remota
def renombrar_carpeta(nombre_actual, nuevo_nombre):
    # Se especifica la ruta actual de la carpeta a renombrar
    ruta_actual = 'remota/' + nombre_actual
    # Se especifica la ruta nueva que tendrá la carpeta renombrada
    ruta_nueva = 'remota/' + nuevo_nombre
    # Se verifica si la carpeta existe en la ruta actual
    if os.path.exists(ruta_actual):
        # Se renombra la carpeta con la función "os.rename()"
        os.rename(ruta_actual, ruta_nueva)
        # Se imprime un mensaje de éxito
        print(f'Se ha renombrado la carpeta {nombre_actual} a {nuevo_nombre} correctamente')
    else:
        # Se imprime un mensaje de error si la carpeta no existe
        print(f'La carpeta {nombre_actual} no existe en la ruta especificada')


try:
    while True: #Bucle hasta que el usuario decida salir
        sys.stdin.flush()  #Vacia el buffer de entrada del usuario
        data = sock.recv(1024) #Recibe datos del servidor
        print('\n', data.decode()) # Imprime el Menu
        # Solicitar al usuario que ingrese la opción deseada
        request = input('Escribe el numero de la opcion que quieres realizar: ')
        sock.sendall(request.encode()) # Enviar la opción al servidor
        if request == '1':
            verCarpetaLocal()
        elif request == '2':
            verCarpetaRemota()
        elif request == '3':
            print('\nNombre de la Carpeta Local: ')
            nombre = input('>>> ')
            crear_carperta1(nombre)
            verCarpetaLocal()
        elif request == '4':
            print('\nNombre de la Carpeta Remota: ')
            nombre = input('>>> ')
            sock.sendall(nombre.encode())
            crear_carpeta(nombre)
            verCarpetaRemota()
        elif request == '5':
            print('\n¿Que archivo deseas eliminar? (Carpeta Local)')
            nombre = input('>>> ')
            eliminar_archivo1(nombre)
            verCarpetaLocal()
        elif request == '6':
            print('\n¿Que archivo deseas eliminar? (Carpeta Remota)')
            nombre = input('>>> ')
            sock.sendall(nombre.encode())
            eliminar_archivo(nombre)
            verCarpetaRemota()
        elif request == '7':
            print('\n¿Que carpeta deseas eliminar? (Carpeta Local)')
            nombre = input('>>> ')
            eliminar_carpeta1(nombre)
            verCarpetaLocal()
        elif request == '8':
            print('\n¿Que carpeta deseas eliminar? (Carpeta Remota)')
            nombre = input('>>> ')
            sock.sendall(nombre.encode())
            eliminar_carpeta(nombre)
            verCarpetaRemota()
        elif request == '9':
            print('\n¿Que archivos deseas subir? ')
            nombre = input('>>> ')
            sock.sendall(nombre.encode())
            subir_archivo(nombre)
            verCarpetaRemota()
        elif request == '10':
            print('\n¿Que carpeta deseas subir?')
            nombre = input('>>> ')
            sock.sendall(nombre.encode())
            subir_carpeta(nombre)
            verCarpetaRemota()
        elif request == '11':
            print('\n¿Que archivo deseas descargar?')
            nombre = input('>>> ')
            sock.sendall(nombre.encode())
            descargar_archivo(nombre)
            verCarpetaLocal()
        elif request == '12':
            print('\n¿Que carpeta deseas descargar?')
            nombre = input('>>> ')
            sock.sendall(nombre.encode())
            descargar_carpeta(nombre)
            verCarpetaLocal()
        elif request == '13':
            print ('\n¿Que archivo deseas renombrar?(Carpeta Local)')
            nombre_actual = input('>>> ')
            print ('\n¿Que nombre le quieres poner?')
            nuevo_nombre = input('>>> ')
            renombrar_archivo1(nombre_actual,nuevo_nombre)
            verCarpetaLocal()
        elif request == '14':
            print('\n¿Que archivo deseas renombrar? (Carpeta Remota)')
            nombre_anterior = input('>>> ')
            print('\n¿Que nombre le quieres poner?')
            nuevo_nombre = input('>>> ')
            renombrar_archivo(nombre_anterior,nuevo_nombre)
            verCarpetaRemota()
        elif request == '15':
            print('\n¿Que carpeta deseas renombrar? (Carpeta Local)')
            nombre_actual = input('>>> ')
            print('\n¿Que nombre le quieres poner?')
            nuevo_nombre = input('>>> ')
            renombrar_carpeta1(nombre_actual,nuevo_nombre)
            verCarpetaLocal()
        elif request == '16':
            print('\n¿Que carpeta deseas renombrar? (Carpeta Remota)')
            nombre_actual = input('>>> ')
            print('\n¿Que nombre le quieres poner?')
            nuevo_nombre = input('>>> ')
            renombrar_carpeta(nombre_actual,nuevo_nombre)
            verCarpetaRemota()
        else:
            break

finally:
    sock.close() #Cierra el Socket