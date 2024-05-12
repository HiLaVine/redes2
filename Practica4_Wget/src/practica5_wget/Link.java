package practica5_wget;

// Importamos las librerías necesarias
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class Link {
    // Creamos una lista para almacenar los enlaces
    private List<String> list = new ArrayList<>();
    // Creamos un bloqueo de lectura/escritura para manejar la concurrencia en nuestra lista
    private ReadWriteLock rwLock = new ReentrantReadWriteLock();
    
    public Link(){
    }
 
    // Constructor con elementos iniciales
    public Link(String... initialElements) {
        list.addAll(Arrays.asList(initialElements));
    }
 
    // Método para añadir un nuevo enlace a la lista
    public void add(String link) {
        Lock writeLock = rwLock.writeLock(); // Conseguimos el bloqueo de escritura
        writeLock.lock();  // Bloqueamos para escritura
        try {
            list.add(link);  // Añadimos el enlace
        } finally {
            writeLock.unlock();  // Desbloqueamos después de la escritura
        }
    }
 
    // Método para obtener un enlace en un índice específico
    public String get(int index) {
        Lock readLock = rwLock.readLock();  // Conseguimos el bloqueo de lectura
        readLock.lock();  // Bloqueamos para lectura
        try {
            return list.get(index);  // Devolvemos el enlace en el índice especificado
        } finally {
            readLock.unlock();  // Desbloqueamos después de la lectura
        }
    }
    
    // Método para verificar si un camino ya existe en la lista
    public boolean exists(String path){
        Lock writeLock = rwLock.writeLock();  // Conseguimos el bloqueo de escritura
        writeLock.lock();  // Bloqueamos para escritura
        try {
            for (int i = 0; i < list.size(); i++) {
                if(list.get(i).equals(path)){
                    return true;  // Si encontramos el camino en la lista, devolvemos verdadero
                }
            }
            list.add(path);  // Si no, añadimos el camino a la lista
            return false;  // Y devolvemos falso
        } finally {
            writeLock.unlock();  // Desbloqueamos después de la escritura
        }
    }

    // Método para obtener el tamaño de la lista
    public int size() {
        Lock readLock = rwLock.readLock();  // Conseguimos el bloqueo de lectura
        readLock.lock();  // Bloqueamos para lectura
        try {
            return list.size();  // Devolvemos el tamaño de la lista
        } finally {
            readLock.unlock();  // Desbloqueamos después de la lectura
        }
    }
}
