package practica5_wget;

// Importa las librerías necesarias
import java.net.URL;
import java.util.Scanner;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.*; 

public class main {
    // Esta es la lista de enlaces para descargar archivos.
    static Link downloadFilesList = new Link();
    
    // MAX_T es el número máximo de hilos que el programa puede tener en funcionamiento.
    static final int MAX_T = 10; 
    
    public static void main(String[] args) {
        // Imprime el título de la aplicación
        System.out.println("\u001B[32m\t\t\t\tAPLICACIÓN WGET\u001B[0m");
        System.out.println("\nHerramienta de descarga WGET para uno o más recursos a través de sus respectivos URL’s");
        // Crea un objeto Scanner para leer la entrada del usuario
        Scanner sc= new Scanner(System.in);
        
        // Solicita al usuario que introduzca una URL
        System.out.println("\u001B[33m\nIngresa la URL del Sitio WEB del que desea descargar los archivos y/o carpetas: \u001B[0m");
        
        // Lee la URL del usuario
        String url= sc.nextLine();
       
        try {
            // Crea un objeto URL con la URL del usuario
            URL webUrl = new URL(url);
            
            // Crea un grupo de hilos para gestionar las descargas.
            ExecutorService pool = Executors.newFixedThreadPool(MAX_T);
            
            // Ejecuta el gestor de archivos en un nuevo hilo.
            pool.execute(new Archivo(webUrl, downloadFilesList));            
        } catch (Exception e) {
           // Si hay alguna excepción (como una URL mal formada), imprime el rastro de la excepción.
           e.printStackTrace();
        }
    }
}
