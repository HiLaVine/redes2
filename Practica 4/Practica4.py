import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Lock

# Bloqueo para la creación de directorios
crearCarpetaLock = Lock()

def descargar_archivos_desde_url(url, carpeta="Descargas", archivos=None, urlsProcs=None):
    # Validaciones
    with crearCarpetaLock:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
    if archivos is None:
        archivos = set()
    if urlsProcs is None:
        urlsProcs = set()

    urls_a_procesar = Queue()
    urls_a_procesar.put(url)

    while not urls_a_procesar.empty():
        url_actual = urls_a_procesar.get()
        if url_actual in urlsProcs:
            continue
        urlsProcs.add(url_actual)

        ruta_destino_actual = carpeta

        if url_actual.startswith(url):
            subruta = url_actual[len(url):].strip('/')
            subruta_limpia = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in subruta)

            if subruta_limpia:
                ruta_destino_actual = os.path.join(carpeta, subruta_limpia)

                if url_actual.endswith('/') and not os.path.exists(ruta_destino_actual):
                    respuesta = requests.get(url_actual)

                    if respuesta.status_code == 200:
                        with crearCarpetaLock:
                            os.makedirs(ruta_destino_actual)
                    else:
                        print(f"No se pudo acceder al página web {url_actual}. Código de estado: {respuesta.status_code}")

        respuesta = requests.get(url_actual)

        if respuesta.status_code == 200:
            # Utilizar BeautifulSoup para analizar el contenido HTML
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            enlaces = soup.find_all('a')
            
            with ThreadPoolExecutor(max_workers=100) as executor:
                for enlace in enlaces:
                        href = enlace.get('href')
                        if href and not any(href.startswith(prefix) for prefix in ('http', '#', 'mailto')):
                            archivo_url = urljoin(url_actual, href)
                            nombre_archivo = os.path.basename(urlparse(archivo_url).path)

                            if nombre_archivo not in archivos:
                                try:
                                    ruta_archivo = os.path.join(ruta_destino_actual, nombre_archivo)
                                    with open(ruta_archivo, 'wb') as archivo_local:
                                        archivo_local.write(requests.get(archivo_url).content)
                                    print(f"Archivo descargado: {nombre_archivo}")
                                    archivos.add(nombre_archivo)
                                except Exception as e:
                                    error = e
                            else:
                                print(f"Archivo ya descargado: {nombre_archivo}")

                            if archivo_url.startswith(url) and archivo_url != url_actual:
                                urls_a_procesar.put(archivo_url)

try:
    url_a_descargar = input(" la página web a descargar -> \t")
    descargar_archivos_desde_url(url_a_descargar)
except:
    print("Algo salió mal. Por favor, intente de nuevo (Fin del programa)")
