package practica4_wget;

import practica4_wget.Link;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class Archivo extends Thread {
    private Link downloadFilesList;
    private URL url;
    // Definimos la ruta donde se guardarán los archivos descargados
    static String path = "C:\\programacion\\redes2\\Practica4_Wget\\Descargas\\";
    
    // Constructor que toma una URL y una lista de archivos para descargar
    public Archivo(URL url, Link downloadFilesList){
        this.url = url;
        this.downloadFilesList = downloadFilesList;
    }
    
    // El método run se invoca cuando se inicia el hilo
    public void run(){
        try {
            // Intentamos descargar el archivo
            download(url);
            System.out.println("DESCARGA COMPLETADA");
        } catch (Exception e) {
            // Imprimimos la excepción en caso de error
            e.printStackTrace();
        }
    }
    
    // Método que realiza la descarga del archivo
    public void download(URL url) throws IOException{
        
        // Definimos las variables necesarias
        String line;
        String name;
        String fileName;
        String newLink;
        String auxNewLink;
        String newName;
        int index;
        
        try{
            // Abrimos una conexión HTTP a la URL
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            
            // Obtenemos el nombre del archivo y del host
            fileName = conn.getURL().getFile();
            name = conn.getURL().getHost() + fileName;
            
            // Verificamos si la respuesta es un error HTTP
            if(conn.getResponseCode() == HttpURLConnection.HTTP_FORBIDDEN || conn.getResponseCode() == HttpURLConnection.HTTP_NOT_FOUND)
                return;
            
            // Si el archivo no se ha descargado aún
            if(!downloadFilesList.exists(name)){
                newName = name;
                
                // Si el nombre contiene un ".", es un archivo
                if(fileName.contains(".")){
                    System.out.println("Descargando el archivo: " + newName);
                    newName = name.substring(0, name.lastIndexOf("/"));
                    File f = new File(path + newName);
                    f.mkdirs();
                    f.setWritable(true);
                }
                // Si no, es una carpeta
                else{
                    System.out.println("Descargando la carpeta: " + name);
                    File f = new File(path + name);
                    f.mkdirs();
                    f.setWritable(true);
                }
                
                // Si el contenido es HTML
                if(conn.getContentType().contains("text/html")){  
                    
                    // Si no contiene ".html", añade "index.html" al final del nombre
                    if(!name.contains(".html")){
                        name = name + "index.html";
                    }
                    
                    // Creamos un BufferedReader para leer la entrada y un BufferedWriter para escribir la salida
                    BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                    BufferedWriter bw = new BufferedWriter(new FileWriter(new File(path + name)));

                    // Leemos cada línea del archivo HTML
                    while((line = br.readLine()) != null) {
                        // Agregamos un salto de línea al final
                        line = line + "\n";

                        // Si la línea contiene un enlace href, extraemos el enlace y lo descargamos
                        if(line.contains("href=\"")){
                            // Extraemos el enlace
                            index = line.indexOf("href=") + 6;
                            newLink = line.substring(index, line.indexOf("\"", index));
                            
                            auxNewLink = newLink;
                            if(!newLink.contains("?") && !newLink.contains("@")){
                                if(newLink.startsWith("/")){
                                    newLink = url.getProtocol() + "://" + url.getHost() + newLink;
                                } else {
                                    newLink = url.getProtocol() + "://" + url.getHost() + url.getFile() + newLink;
                                }
                                // Descargamos el enlace
                                download(new URL(newLink));
                            }
                            
                            // Actualizamos la línea para que apunte al archivo descargado localmente
                            line = line.replace("https://", path);
                            line = line.replace("http://", path);
                            
                            if(!auxNewLink.startsWith("/")){
                                line  = line.replace("href=\"", "href=\"" + path + url.getHost() + url.getFile() + "/");
                            }
                            
                        }
                        
                        // Si la línea contiene una imagen src, extraemos la imagen y la descargamos
                        if(line.contains("src=\"")){
                            // Extraemos la imagen
                            index = line.indexOf("src") + 5;
                            newLink = line.substring(index, line.indexOf("\"", index));
                        
                            if(!newLink.contains("?")){
                                if(newLink.startsWith("/")){
                                    newLink = url.getProtocol() + "://" + url.getHost() + newLink;
                                } else {
                                    newLink = url.getProtocol() + "://" + url.getHost() + url.getFile() + newLink;
                                }
                                // Descargamos la imagen
                                download(new URL(newLink));
                            }
                            
                            // Actualizamos la línea para que apunte a la imagen descargada localmente
                            line = line.replace("https://", path);
                            line = line.replace("http://", path);
                            line  = line.replace("/icons/", "../icons/");
    
                        }
                        // Escribimos la línea en el archivo de salida
                        bw.write(line);
                        bw.newLine();
                    }
                    
                    // Cerramos el BufferedReader y BufferedWriter
                    br.close();
                    bw.close();
                
                } else { // Si el contenido no es HTML
                                        
                    // Creamos un DataInputStream para leer la entrada y un DataOutputStream para escribir la salida
                    DataInputStream dis = new DataInputStream(conn.getInputStream());
                    DataOutputStream dos = new DataOutputStream(new FileOutputStream(path + name));

                    // Leemos los datos del archivo y los escribimos en el archivo de salida
                    long recibidos = 0;
                    int n;

                    while(recibidos < conn.getContentLengthLong()){
                        byte[] b = new byte[2000];
                        n = dis.read(b);
                        recibidos = recibidos + n;

                        dos.write(b, 0, n);
                        dos.flush();
                    }

                    // Cerramos el DataInputStream y DataOutputStream
                    dis.close();
                    dos.close();

                }
            
            }
        } catch(Exception e){
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            System.out.println("connection.getResponseCode(): " + conn.getResponseCode());
        }
        
    }
    
}
