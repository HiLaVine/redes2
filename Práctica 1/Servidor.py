import socket
import os
import shutil
import zipfile

### Practica 01 ###
### Redes 2 ###
### Farrera Mendez Emmanuel Sinai ###
### Ramirez Lopez Felipe Hiram ###

# Configuración del servidor
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024
LOCAL_FOLDER = "local"
REMOTE_FOLDER = "remota"

# Función para recibir archivos del cliente
def receive_file(client_socket, filename):
    # Abre el archivo en modo de escritura binaria ('wb') para recibir los datos del cliente
    with open(filename, 'wb') as f:
        # Bucle infinito para recibir los datos del cliente en bloques y escribirlos en el archivo
        while True:
            # Recibe datos del cliente usando el socket del cliente, con un tamaño de búfer especificado
            data = client_socket.recv(BUFFER_SIZE)
            # Verifica si no hay más datos recibidos del cliente
            if not data:
                # Si no hay más datos, sale del bucle
                break
            # Escribe los datos recibidos en el archivo abierto en modo de escritura binaria
            f.write(data)


# Función para enviar archivos al cliente
def send_file(client_socket_2, filename):
    # Abre el archivo en modo de lectura binaria ('rb') para enviar los datos al cliente
    with open(filename, 'rb') as f:
        # Lee el primer bloque de datos del archivo
        data = f.read(BUFFER_SIZE)
        # Bucle mientras haya datos en el archivo para enviar al cliente
        while data:
            # Envía el bloque actual de datos al cliente a través del socket del cliente
            client_socket_2.send(data)
            # Lee el siguiente bloque de datos del archivo
            data = f.read(BUFFER_SIZE)


# Función para recibir una carpeta del cliente
def receive_folder(client_socket, foldername, filename):
    try:
        # Crea una carpeta en el servidor con el nombre especificado
        os.mkdir(foldername)
        # Abre un archivo en modo de escritura binaria ('wb') para recibir los datos de la carpeta
        with open(filename, 'wb') as f:
            # Bucle para recibir los datos de la carpeta del cliente a través del socket
            while True:
                # Recibe un bloque de datos del cliente
                data = client_socket.recv(BUFFER_SIZE)
                # Si no hay más datos, se sale del bucle
                if not data:
                    break
                # Escribe los datos recibidos en el archivo
                f.write(data)
    except Exception as e:
        # Maneja cualquier excepción que pueda ocurrir durante la recepción de la carpeta
        print(f"Error al recibir la carpeta: {str(e)}")



# Función para enviar una carpeta al cliente
def send_folder(client_socket, foldername):
    try:
        # Comprime la carpeta en un archivo ZIP temporal
        shutil.make_archive(foldername, 'zip', foldername)
        # Abre el archivo ZIP comprimido en modo de lectura binaria ('rb')
        with open(foldername + '.zip', 'rb') as f:
            # Lee el archivo en bloques de tamaño BUFFER_SIZE
            data = f.read(BUFFER_SIZE)
            # Envía los datos al cliente a través del socket mientras haya datos para enviar
            while data:
                client_socket.send(data)
                data = f.read(BUFFER_SIZE)
    except Exception as e:
        # Maneja cualquier excepción que pueda ocurrir durante el envío de la carpeta
        print(f"Error al enviar la carpeta: {str(e)}")
    finally:
        # Elimina el archivo ZIP temporal después de enviarlo
        os.remove(foldername + '.zip')


# Función principal del servidor
def main():

    # Creación de dos sockets, uno para la comunicación principal y otro para enviar datos de respuesta
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Se establece el tiempo de espera para la comunicación en el socket
    server_socket.settimeout(None)
    server_socket_2.settimeout(None)
    # Se enlazan los sockets a la dirección y puerto del servidor
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()  # Se pone el socket en modo de escucha
    server_socket_2.bind((SERVER_HOST, 12346))
    server_socket_2.listen()

    print(f"El servidor está escuchando en {SERVER_HOST}:{SERVER_PORT}")
    
    prendido = True
    while prendido:
        client_socket, client_address = server_socket.accept()
        client_socket_2, client_address_2 = server_socket_2.accept()
        print(f"Se ha conectado un cliente desde {client_address[0]}:{client_address[1]}")

        # Recibe el comando del cliente
        command = client_socket.recv(BUFFER_SIZE).decode()
        print(command)

        # Verifica si el comando recibido comienza con 'SUBIR'
        if command.startswith('SUBIR'):
            # Divide el comando en dos partes utilizando el espacio como separador y descarta la primera parte (que es 'SUBIR')
            _, filename = command.split()
            # Remueve los caracteres de barra invertida y barra inclinada del nombre de archivo para evitar problemas de ruta
            filename = filename.replace("\\", "").replace("/", "")
            # Une el nombre de archivo con la ruta de la carpeta local para obtener la ruta completa del archivo en el servidor
            path = os.path.join(LOCAL_FOLDER, filename)
            # Verifica si el archivo o directorio existe en la carpeta local del servidor
            if os.path.exists(path):
                # Si el archivo o directorio existe:
                # Verifica si es un directorio
                if os.path.isdir(path):
                    # Si es un directorio, envía la carpeta al cliente
                    send_folder(client_socket_2, path)
                    # Imprime un mensaje indicando que se ha enviado la carpeta desde la carpeta local y se ha guardado en la carpeta remota
                    print(
                        f"Se ha recibido la carpeta '{filename}' de la carpeta local y se ha guardado en la carpeta remota.")
                else:
                    # Si es un archivo, envía el archivo al cliente
                    send_file(client_socket_2, path)
                    # Imprime un mensaje indicando que se ha enviado el archivo desde la carpeta local y se ha guardado en la carpeta remota
                    print(
                        f"Se ha recibido el archivo '{filename}' de la carpeta local y se ha guardado en la carpeta remota.")
            else:
                # Si el archivo o directorio no existe en la carpeta local, imprime un mensaje de error
                print(f"El archivo o directorio '{filename}' no existe en la carpeta local.")

        # Verifica si el comando recibido comienza con 'DESCARGAR'
        elif command.startswith('DESCARGAR'):
            # Divide el comando en dos partes utilizando el espacio como separador y descarta la primera parte (que es 'DESCARGAR')
            _, filename = command.split()
            # Remueve los caracteres de barra invertida y barra inclinada del nombre de archivo para evitar problemas de ruta
            filename = filename.replace("\\", "").replace("/", "")
            # Une el nombre de archivo con la ruta de la carpeta remota para obtener la ruta completa del archivo en el servidor remoto
            path = os.path.join(REMOTE_FOLDER, filename)

            # Verifica si el archivo o directorio existe en la carpeta remota del servidor
            if os.path.exists(path):
                # Si el archivo o directorio existe:
                # Verifica si es un directorio
                if os.path.isdir(path):
                    # Si es un directorio, envía la carpeta al cliente
                    send_folder(client_socket_2, path)
                    # Imprime un mensaje indicando que se ha enviado la carpeta desde la carpeta remota y se ha guardado en la carpeta local
                    print(
                        f"Se ha enviado la carpeta '{filename}' de la carpeta remota y de ha guardado en la carpeta local.")
                else:
                    # Si es un archivo, envía el archivo al cliente
                    send_file(client_socket_2, path)
                    # Imprime un mensaje indicando que se ha enviado el archivo desde la carpeta remota y se ha guardado en la carpeta local
                    print(
                        f"Se ha enviado el archivo '{filename}' de la carpeta remota y de ha guardado en la carpeta local.")
            else:
                # Si el archivo o directorio no existe en la carpeta remota, imprime un mensaje de error
                print(f"El archivo o directorio '{filename}' no existe en la carpeta remota.")

        # Verifica si el comando recibido comienza con 'ELIMINAR_LOCAL'
        elif command.startswith('ELIMINAR_LOCAL'):
            # Divide el comando en dos partes utilizando el espacio como separador y descarta la primera parte (que es 'ELIMINAR_LOCAL')
            _, filename = command.split()
            # Une el nombre del archivo con la ruta de la carpeta local para obtener la ruta completa del archivo en el servidor local
            path = os.path.join(LOCAL_FOLDER, filename)

            # Verifica si el archivo o directorio existe en la carpeta local del servidor
            if os.path.exists(path):
                # Si el archivo o directorio existe:
                # Verifica si es un directorio
                if os.path.isdir(path):
                    # Si es un directorio, elimina el directorio y todo su contenido de manera recursiva
                    shutil.rmtree(path)
                    # Imprime un mensaje indicando que se ha eliminado el directorio de la carpeta local
                    print(f"Se ha eliminado el directorio '{filename}' de la carpeta local.")
                else:
                    # Si es un archivo, elimina el archivo
                    os.remove(path)
                    # Imprime un mensaje indicando que se ha eliminado el archivo de la carpeta local
                    print(f"Se ha eliminado el archivo '{filename}' de la carpeta local.")
            else:
                # Si el archivo o directorio no existe en la carpeta local, imprime un mensaje de error
                print(f"El archivo o directorio '{filename}' no existe en la carpeta local.")

        # Verifica si el comando recibido comienza con 'ELIMINAR_REMOTA'
        elif command.startswith('ELIMINAR_REMOTA'):
            # Divide el comando en dos partes utilizando el espacio como separador y descarta la primera parte (que es 'ELIMINAR_REMOTA')
            _, filename = command.split()
            # Une el nombre del archivo con la ruta de la carpeta remota para obtener la ruta completa del archivo en el servidor remoto
            path = os.path.join(REMOTE_FOLDER, filename)

            # Verifica si el archivo o directorio existe en la carpeta remota del servidor
            if os.path.exists(path):
                # Si el archivo o directorio existe:
                # Verifica si es un directorio
                if os.path.isdir(path):
                    # Si es un directorio, elimina el directorio y todo su contenido de manera recursiva
                    shutil.rmtree(path)
                    # Imprime un mensaje indicando que se ha eliminado el directorio de la carpeta remota
                    print(f"Se ha eliminado el directorio '{filename}' de la carpeta remota.")
                else:
                    # Si es un archivo, elimina el archivo
                    os.remove(path)
                    # Imprime un mensaje indicando que se ha eliminado el archivo de la carpeta remota
                    print(f"Se ha eliminado el archivo '{filename}' de la carpeta remota.")
            else:
                # Si el archivo o directorio no existe en la carpeta remota, imprime un mensaje de error
                print(f"El archivo o directorio '{filename}' no existe en la carpeta remota.")


        elif command.startswith('RENOMBRAR_LOCAL'):
            _, old_name, new_name = command.split()
            os.rename(os.path.join(LOCAL_FOLDER, old_name), os.path.join(LOCAL_FOLDER, new_name))
            print(f"Se ha renombrado '{old_name}' a '{new_name}' en la carpeta local.")

        elif command.startswith('RENOMBRAR_REMOTA'):
            _, old_name, new_name = command.split()
            os.rename(os.path.join(REMOTE_FOLDER, old_name), os.path.join(REMOTE_FOLDER, new_name))
            print(f"Se ha renombrado '{old_name}' a '{new_name}' en la carpeta remota.")

        elif command.startswith('COPIAR_LOCAL'):
            _, src = command.split()
            src_path = os.path.join(LOCAL_FOLDER, src)
            dest = f"{src}(copia)"
            dest_path = os.path.join(LOCAL_FOLDER, dest)
            if os.path.exists(src_path):
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path)
                    print(f"Se ha hecho una copia del directorio '{src}' en '{dest}'.")
                else:
                    shutil.copy2(src_path, dest_path)
                    print(f"Se ha hecho una copia del archivo '{src}' en '{dest}'.")
            else:
                print(f"El archivo o directorio '{src}' no existe en la carpeta local.")

        elif command.startswith('COPIAR_REMOTA'):
            _, src = command.split()
            src_path = os.path.join(REMOTE_FOLDER, src)
            dest = f"{src}(copia)"
            dest_path = os.path.join(REMOTE_FOLDER, dest)
            if os.path.exists(src_path):
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path)
                    print(f"Se ha hecho una copia del directorio '{src}' en '{dest}'.")
                else:
                    shutil.copy2(src_path, dest_path)
                    print(f"Se ha hecho una copia del archivo '{src}' en '{dest}'.")
            else:
                print(f"El archivo o directorio '{src}' no existe en la carpeta remota.")

        elif command.startswith('CREAR_CARPETA'):
            _, folder, dir_name = command.split()
            if folder == "local":
                os.mkdir(os.path.join(LOCAL_FOLDER, dir_name))
                print(f"Se ha creado el directorio '{dir_name}' en la carpeta local.")
            elif folder == "remota":
                os.mkdir(os.path.join(REMOTE_FOLDER, dir_name))
                print(f"Se ha creado el directorio '{dir_name}' en la carpeta remota.")

        elif command.startswith('CREAR_ARCHIVO'):
            _, folder, file_name = command.split()
            file = file_name.split(".", 1)
            if folder == "local":
                open(os.path.join(LOCAL_FOLDER, file_name), 'a').close()
                os.path.join(LOCAL_FOLDER, file_name)
                print(f"Se ha creado el archivo '{file_name}' en la carpeta local.")
            elif folder == "remota":
                open(os.path.join(REMOTE_FOLDER, file_name), 'a').close()
                os.path.join(REMOTE_FOLDER, file_name)
                print(f"Se ha creado el archivo '{file_name}' en la carpeta remota.")
        
        elif command.startswith('SALIR'):
            prendido = False

        client_socket_2.shutdown(socket.SHUT_WR)
        client_socket.close()

if __name__ == "__main__":
    main()
    
    if not os.path.exists(LOCAL_FOLDER):
        os.mkdir(LOCAL_FOLDER)
    if not os.path.exists(REMOTE_FOLDER):
        os.mkdir(REMOTE_FOLDER)    
    