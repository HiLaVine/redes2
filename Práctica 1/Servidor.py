import socket
import os
import shutil
import zipfile

# Configuración del servidor
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024
LOCAL_FOLDER = "local"
REMOTE_FOLDER = "remota"

# Función para recibir archivos del cliente
def receive_file(client_socket, filename):
    with open(filename, 'wb') as f:
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            f.write(data)

# Función para enviar archivos al cliente
def send_file(client_socket_2, filename):
    with open(filename, 'rb') as f:
        data = f.read(BUFFER_SIZE)
        while data:
            client_socket_2.send(data)
            data = f.read(BUFFER_SIZE)

# Función para recibir una carpeta del cliente
def receive_folder(client_socket, foldername, filename):
    try:
        os.mkdir(foldername)  # Crea una carpeta en el servidor con el nombre especificado
        with open(filename, 'wb') as f:
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
    except Exception as e:
        print(f"Error al recibir la carpeta: {str(e)}")


# Función para enviar una carpeta al cliente
def send_folder(client_socket, foldername):
    try:
        # Comprime la carpeta en un archivo ZIP temporal
        shutil.make_archive(foldername, 'zip', foldername)
        with open(foldername + '.zip', 'rb') as f:
            data = f.read(BUFFER_SIZE)
            while data:
                client_socket.send(data)
                data = f.read(BUFFER_SIZE)
    except Exception as e:
        print(f"Error al enviar la carpeta: {str(e)}")
    finally:
        os.remove(foldername + '.zip')

# Función principal del servidor
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(None)
    server_socket_2.settimeout(None)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()
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

        if command.startswith('SUBIR'):
            _, filename = command.split()    
            filename = filename.replace("\\", "").replace("/", "")        
            path = os.path.join(LOCAL_FOLDER, filename)
            if os.path.exists(path):
                if os.path.isdir(path):
                    send_folder(client_socket_2, path)
                    print(f"Se ha recibido la carpeta '{filename}' de la carpeta local y se ha guardado en la carpeta remota.")
                else:
                    send_file(client_socket_2, path)
                    print(f"Se ha recibido el archivo '{filename}' de la carpeta local y se ha guardado en la carpeta remota.")
            else:
                print(f"El archivo o directorio '{filename}' no existe en la carpeta local.")


        elif command.startswith('DESCARGAR'):
            _, filename = command.split()            
            filename = filename.replace("\\", "").replace("/", "")
            path = os.path.join(REMOTE_FOLDER, filename)
            
            if os.path.exists(path):
                if os.path.isdir(path):
                    send_folder(client_socket_2, path)
                    print(f"Se ha enviado la carpeta '{filename}' de la carpeta remota y de ha guardado en la carpeta local.")
                else:
                    send_file(client_socket_2, path)
                    print(f"Se ha enviado el archivo '{filename}' de la carpeta remota y de ha guardado en la carpeta local.")
            else:
                print(f"El archivo o directorio '{filename}' no existe en la carpeta remota.")


        elif command.startswith('ELIMINAR_LOCAL'):
            _, filename = command.split()
            path = os.path.join(LOCAL_FOLDER, filename)
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"Se ha eliminado el directorio '{filename}' de la carpeta local.")
                else:
                    os.remove(path)
                    print(f"Se ha eliminado el archivo '{filename}' de la carpeta local.")
            else:
                print(f"El archivo o directorio '{filename}' no existe en la carpeta local.")

        elif command.startswith('ELIMINAR_REMOTA'):
            _, filename = command.split()
            path = os.path.join(REMOTE_FOLDER, filename)
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"Se ha eliminado el directorio '{filename}' de la carpeta remota.")
                else:
                    os.remove(path)
                    print(f"Se ha eliminado el archivo '{filename}' de la carpeta remota.")
            else:
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
    