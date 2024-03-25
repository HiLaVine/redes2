import socket
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import zipfile

### Practica 01 ###
### Redes 2 ###
### Farrera Mendez Emmanuel Sinai ###
### Ramirez Lopez Felipe Hiram ###

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

RutaL = "local"
RutaR = "remota"


def CrearMenu():
    # Crea una nueva ventana de la aplicación xd
    ventana = tk.Tk()
    ventana.title("Administrador de Archivos")

    # Crea un marco en el lado izquierdo de la ventana
    frame_izquierdo = ttk.Frame(ventana)
    frame_izquierdo.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)

    # Crea un marco en el lado derecho de la ventana
    frame_derecho = ttk.Frame(ventana)
    frame_derecho.pack(side=tk.RIGHT, padx=10, pady=10, expand=True, fill=tk.BOTH)

    def listar_directorio(tree, ruta):
        # Elimina todos los elementos existentes en el árbol
        for i in tree.get_children():
            tree.delete(i)

        try:
            # Obtiene el contenido del directorio especificado
            contenido = os.listdir(ruta)
            # Itera sobre los elementos del directorio
            for item in contenido:
                # Construye la ruta completa del elemento
                item_path = os.path.join(ruta, item)
                # Verifica si el elemento es un directorio
                if os.path.isdir(item_path):
                    # Inserta el nombre del directorio en el árbol y agrega un "/" al final para denotar una carpeta
                    tree.insert('', 'end', values=(item + "\\",))
                else:
                    # Inserta el nombre del archivo en el árbol
                    tree.insert('', 'end', values=(item,))
        except FileNotFoundError:
            # Inserta un mensaje de error si el directorio no se encuentra
            tree.insert('', 'end', values=("Directorio no encontrado",))

    def SubMenu(sc2, path, accion):
        if accion == "Archivo":
            # Si la acción es "Archivo", recibe los datos del socket y escribe en el archivo especificado por la ruta
            with open(path, 'wb') as f:
                while True:
                    data = sc2.recv(1024)
                    if not data:
                        break
                    f.write(data)

        elif accion == "Carpeta":
            # Si la acción es "Carpeta", recibe los datos del socket y escribe en un archivo ZIP temporal
            with open(path + ".zip", 'wb') as f:
                while True:
                    data = sc2.recv(1024)
                    if not data:
                        break
                    f.write(data)

            # Descomprime el archivo ZIP en la ruta especificada
            if not os.path.exists(path):
                os.makedirs(path)
            with zipfile.ZipFile(path + ".zip", 'r') as zipf:
                zipf.extractall(path)

            # Elimina el archivo ZIP temporal después de la extracción
            os.remove(path + ".zip")

    def boton_presionado(lado, accion, tree):
        print(lado, accion, tree)
        flag = False
        seleccion = tree.selection()

        socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_cliente_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_cliente.connect((SERVER_HOST, SERVER_PORT))
        socket_cliente_2.connect((SERVER_HOST, 12346))

        # Enviar comando al servidor
        if lado == "izquierdo":
            carpeta = "local"
        else:
            carpeta = "remota"

        if seleccion:
            item = tree.item(seleccion[0])
            archivo_seleccionado = item['values'][0]
            print(f"Archivo seleccionado: {archivo_seleccionado}")
            if accion == "Subir":
                comando = f"SUBIR {archivo_seleccionado}"
                flag = True

            elif accion == "Descargar":
                comando = f"DESCARGAR {archivo_seleccionado}"
                flag = True

            elif accion == "Eliminar":
                respuesta = messagebox.askquestion("Confirmar", f"¿Deseas eliminar '{archivo_seleccionado}'?",
                                                   icon='warning')
                if respuesta == 'yes':
                    comando = f"ELIMINAR_{carpeta.upper()} {archivo_seleccionado}"

            elif accion == "Renombrar":
                nuevo_nombre = simpledialog.askstring("Renombrar",
                                                      f"Nuevo nombre para '{archivo_seleccionado}' (sin espacios):",
                                                      initialvalue=archivo_seleccionado)
                comando = f"RENOMBRAR_{carpeta.upper()} {archivo_seleccionado} {nuevo_nombre}"

            elif accion == "Copiar":
                comando = f"COPIAR_{carpeta.upper()} {archivo_seleccionado}"

        else:
            if (accion != "Crear" and accion != "Recargar"):
                messagebox.showwarning("Advertencia", "Seleccionar un archivo para esta acción")
                accion = "Recargar"
        if accion == "Crear":
            # AQUÍ HAY QUE PONER CÓDIGO PARA QUE UNA VENTANA PREGUNTE SI QUIERE UN ARCHIVO O UNA CARPETA
            tipo = simpledialog.askstring("Nuevo", f"Nombre para el nuevo elemento en {lado}:")
            carpeta_nueva = simpledialog.askstring("Crear", f"Nombre para el nuevo elemento en {lado}:")
            comando = f"CREAR_{tipo.upper()} {carpeta} {carpeta_nueva}"
        elif accion == "Recargar":
            listar_directorio(tree_izquierdo, RutaL)
            listar_directorio(tree_derecho, RutaR)
            comando = ""

        # Envía el comando al servidor
        if comando:
            socket_cliente.send(comando.encode())
            if flag:
                a_s = archivo_seleccionado.replace("\\", "").replace("/", "")
                if accion == "Subir":
                    path = os.path.join(RutaR, a_s)
                    if "\\" in archivo_seleccionado or "/" in archivo_seleccionado:
                        SubMenu(socket_cliente_2, path, "Carpeta")
                        messagebox.showinfo("Info", "Carpeta cargada con éxito")
                    else:
                        SubMenu(socket_cliente_2, path, "Archivo")
                        messagebox.showinfo("Info", "Archivo cargado con éxito")
                elif accion == "Descargar":
                    path = os.path.join(RutaL, a_s)
                    if "\\" in archivo_seleccionado or "/" in archivo_seleccionado:
                        SubMenu(socket_cliente_2, path, "Carpeta")
                        messagebox.showinfo("Info", "Carpeta descargada con éxito")
                    else:
                        SubMenu(socket_cliente_2, path, "Archivo")
                        messagebox.showinfo("Info", "Archivo descargado con éxito")
        print(f"Botón '{accion}' presionado en el lado {lado}.")
        listar_directorio(tree_izquierdo, RutaL)
        listar_directorio(tree_derecho, RutaR)
        socket_cliente.close()
        socket_cliente_2.close()
        ventana.update()

    # Carpeta local
    etiqueta_directorio_izquierdo = ttk.Label(frame_izquierdo, text="Carpeta Local: " + RutaL, width=50)
    etiqueta_directorio_izquierdo.pack(fill=tk.X, pady=5)

    # Botones del lado izquierdo
    botones_izquierdos = ["Subir", "Renombrar", "Eliminar", "Copiar", "Crear", "Recargar"]
    for btn_text in botones_izquierdos:
        boton = ttk.Button(frame_izquierdo, text=btn_text,
                           command=lambda accion=btn_text: boton_presionado("izquierdo", accion, tree_izquierdo))
        boton.pack(fill=tk.X, pady=5)

    tree_izquierdo = ttk.Treeview(frame_izquierdo, columns=("LOCAL",), show="headings")
    tree_izquierdo.heading("LOCAL", text="LOCAL")
    tree_izquierdo.pack(expand=True, fill=tk.BOTH, pady=5)

    # Carpeta remota
    etiqueta_directorio_derecho = ttk.Label(frame_derecho, text="Carpeta Remota: " + RutaR, width=50)
    etiqueta_directorio_derecho.pack(fill=tk.X, pady=5)

    # Botones del lado derecho
    botones_derechos = ["Descargar", "Renombrar", "Eliminar", "Copiar", "Crear", "Recargar"]
    for btn_text in botones_derechos:
        boton = ttk.Button(frame_derecho, text=btn_text,
                           command=lambda accion=btn_text: boton_presionado("derecho", accion, tree_derecho))
        boton.pack(fill=tk.X, pady=5)

    tree_derecho = ttk.Treeview(frame_derecho, columns=("REMOTA",), show="headings")
    tree_derecho.heading("REMOTA", text="REMOTA")
    tree_derecho.pack(expand=True, fill=tk.BOTH, pady=5)

    listar_directorio(tree_izquierdo, RutaL)
    listar_directorio(tree_derecho, RutaR)

    ventana.mainloop()
    ventana.update()


def main():
    try:
        # Menu
        CrearMenu()
        socket_salida = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_salida.connect((SERVER_HOST, 12345))
        _.connect((SERVER_HOST, 12346))
        socket_salida.send("SALIR".encode())
        print("Conexión finalizada")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
