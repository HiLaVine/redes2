import socket
import pathlib
import os
import sys
import shutil



### Practica 01 ###
### Farrera Mendez Emmanuel Sinai ###
### Ramirez Lopez Felipe Hiram ###
### Aplicaciones para la comunicaciones en red ###

# Crea un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(None) # settimeout is the attr of socks.
#Establece la dirección del servidor y el número de puerto
server_address = ('127.0.0.1', 1234)

#Asociar el socket a la dirección del servidor
sock.bind(server_address)

#Escucha en el socket en busca de conexiones entrantes, en este caso solo una.
sock.listen()


print('Iniciando Servidor \x1b[1;31m{}\x1b[0m en puerto \x1b[1;31m{}\x1b[0m'.format(*server_address))
carpeta = 'remota'#Carpeta del servidor
#Menu de opciones que puede realizar el usuario

menu = b'''\x1b[1;33m\n
+----------------------------------------------------------------+
| Practica No.1 Aplicacion Drive para Almacenamiento de Archivos |
+----------------------------------------------------------------+
     1. Visualizar Carpeta Local
     2. Visualizar Carpeta Remota
     3. Crear Carpeta Local
     4. Crear Carpeta Remota
     5. Eliminar Archivo Local
     6. Eliminar Archivo Remoto
     7. Eliminar Carpeta Local
     8. Eliminar Carpeta Remota
     9. Subir Archivo a la Carpeta Remota
     10. Subir Carpeta a la Carpeta Remota
     11. Descargar Archivo a la Carpeta Local
     12. Descargar Carpeta a la Carpeta Local
     13. Renombrar Archivo Local
     14. Renombrar Archivo Remoto
     15. Renombrar Carpeta Local
     16. Renombrar Carpeta Remota
     X. Terminar Conexion                                          
+----------------------------------------------------------------+
\x1b[0m
'''

#Funcion para crear una Carpeta en el Servidor
def crear_carpeta(nombre):
    # Cambiar al directorio
    os.chdir('remota')
    print('Creando carpeta...', nombre)
    #Crea la carpeta
    os.makedirs(nombre, exist_ok=True)
    print('Carpeta creada correctamente')
    # Enviar señal de finalización al cliente
    connection.send(b'DONE')
    os.chdir('..')


#Función para eliminar un Archivo en el servidor
def eliminar_archivo(nombre):
    print('Eliminando...', nombre)
    # Eliminar el archivo especificado
    os.unlink(nombre)
    print('Archivo eliminado correctamente')
    # Enviar una señal de finalización al cliente
    connection.send(b'DONE')
    os.chdir('..')

#Función para eliminar una Carpeta en el Servidor
def eliminar_carpeta(nombre):
    print('Eliminando...', nombre)
    #Elimina la carpeta
    shutil.rmtree(nombre)
    print('Carpeta eliminada correctamente')
    # Enviar señal de finalización al cliente
    connection.send(b'DONE')
    os.chdir('..')

#Función subir un Archivo en el Servidor
def subir_archivo(nombre):
    # Abre un archivo con el nombre proporcionado en modo de escritura binaria
    file = open(nombre, "wb")
    print("Recibiendo....", nombre)
    while True:
        # Recibe datos del cliente a través de la conexión
        data = connection.recv(1024)
        # Se ha terminado de recibir el archivo
        if data == b"DONE":
            print("Carga completa. \n")
            # Limpia el búfer de entrada estándar
            sys.stdin.flush()
            break
        # Escribe los datos recibidos en el archivo
        file.write(data)
        # Limpia el búfer de entrada estándar
        sys.stdin.flush()
    # Limpia el búfer de entrada estándar
    sys.stdin.flush()
    # Cierra el archivo
    file.close()
    os.chdir('..')


#Función para subir una Carpeta al Servidor
def subir_carpeta(nombre):
    # Crear el directorio especificado
    os.makedirs(nombre)
    # Crear el directorio especificado
    os.chdir(nombre)
    # Abrir el archivo para escritura binaria
    file = open(nombre+'.zip', "wb")
    # Imprimir un mensaje indicando que se está recibiendo el archivo
    print("Recibiendo....", nombre)
    # Leer los datos del archivo en bloques de 1024 bytes hasta que se reciba la señal de finalizaciónxxx
    while True:
        data = connection.recv(1024)
        if data == b"DONE":
            print("Carga completa. \n")
            sys.stdin.flush()
            break
        file.write(data)
        sys.stdin.flush()
    sys.stdin.flush()
    # Cerrar el archivo
    file.close()
    # Desempaquetar el archivo zip en el directorio actual
    shutil.unpack_archive(nombre+'.zip')
    # Eliminar el archivo zip
    os.unlink(nombre + '.zip')
    # Cambiar el directorio de trabajo al directorio padre dos veces
    os.chdir('..')

#Función para Descargar una Carpeta desde el Servidor
def descargar_archivo(nombre):
    # Abre un archivo con el nombre proporcionado en modo de lectura binaria
    file = open(nombre, "rb")
    # Lee los primeros 1024 bytes del archivo
    data = file.read(1024)
    print("Enviando...", nombre)
    #Envía los datos del archivo al cliente a través de la conexión
    while data:
        # Envía los datos al cliente a través de la conexión
        connection.send(data)
        # Lee los siguientes 1024 bytes del archivo
        data = file.read(1024)
        # Limpia el búfer de entrada estándar
        sys.stdin.flush()
    # Limpia el búfer de entrada estándar
    sys.stdin.flush()
    # Cierra el archivo
    file.close()
    os.chdir('..')
    # Envía un mensaje al cliente indicando que se ha terminado de enviar el archivo
    connection.send(b"DONE")
    print("Enviado correctamente")


#Función para descargar una carpeta desde el servidor
def descargar_carpeta(nombre):
    # Crear un archivo zip del directorio especificado
    shutil.make_archive(nombre, "zip", nombre)
    # Abrir el archivo zip en modo de lectura binaria
    file = open(nombre + '.zip', "rb")
    # Leer los datos del archivo en bloques de 1024 bytes y enviarlos al cliente
    data = file.read(1024)
    print("Enviando...", nombre)
    while data:
        connection.send(data)
        data = file.read(1024)
        sys.stdin.flush()
    sys.stdin.flush()
    # Cerrar el archivo
    file.close()
    # Eliminar el archivo zip
    os.unlink(nombre + '.zip')
    # Cambiar el directorio de trabajo al directorio padre
    os.chdir('..')
    connection.send(b"DONE")
    print("Enviado correctamente")


# Se inicia un ciclo infinito que espera la conexión de clientes
while True:
    print('\nEsperando Clientes...')

    # Se espera la conexión del cliente
    connection, client_address = sock.accept()

    try:
        # Se informa que el cliente se ha conectado
        print('\nCliente Conectado:', client_address)

        # Se inicia un ciclo infinito que espera la respuesta del cliente
        while True:
            # Se limpia la entrada estándar del sistema
            sys.stdin.flush()

            # Se envía el menú al cliente
            connection.sendall(menu)

            # Se reciben los datos del cliente
            data = connection.recv(5)
            print(data.decode())

            # Si se reciben datos, se verifica la opción seleccionada por el cliente y se realiza la acción correspondiente
            if data:
                os.chdir('remota')

                # Opción 4: Crea carpeta en el Servidor
                if data.decode() == '4':
                    nombre = connection.recv(50)
                    crear_carpeta(nombre.decode())
                    sys.stdin.flush()

                # Opción 6: Elimina archivo en el Servidor
                elif data.decode() == '6':
                    nombre = connection.recv(50)
                    eliminar_archivo(nombre.decode())
                    sys.stdin.flush()

                # Opción 8: Elimina carpeta en el Servidor
                elif data.decode() == '8':
                    nombre = connection.recv(50)
                    eliminar_carpeta(nombre.decode())
                    sys.stdin.flush()

                # Opción 9: Sube archivo al Servidor
                elif data.decode() == '9':
                    nombre = connection.recv(50)
                    subir_archivo(nombre.decode())
                    sys.stdin.flush()

                # Opción 10: Sube carpeta al Servidor
                elif data.decode() == '10':
                    nombre = connection.recv(50)
                    subir_carpeta(nombre.decode())
                    sys.stdin.flush()

                # Opción 11: Descargar archivo desde el Servidor
                elif data.decode() == '11':
                    nombre = connection.recv(50)
                    descargar_archivo(nombre.decode())
                    sys.stdin.flush()

                # Opción 12: Descargar carpeta desde el Servidor
                elif data.decode() == '12':
                    nombre = connection.recv(50)
                    descargar_carpeta(nombre.decode())
                    sys.stdin.flush()

                # Opción X: Salir del programa
                elif data.decode() == 'X':
                    sys.stdin.flush()
                    break

            # Si no se reciben datos, se sale del ciclo de espera de respuestas del cliente
            else:
                break

    # Si se produce un error durante la conexión, se cierra la conexión
    except Exception as e:
        print(e)
        connection.close()

    # Si la conexión termina correctamente, se cierra la conexión
    finally:
        connection.close()