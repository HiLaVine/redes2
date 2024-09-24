import java.io.*;
import java.net.*;
import java.nio.*;
import java.nio.channels.*;
import java.nio.charset.*;
import java.nio.file.*;
import java.text.SimpleDateFormat;
import java.util.*;

public class SHTTPNB {

    public static final int PUERTO = 8000; // Puerto en el que escucha el servidor
    private Selector selector;
    private ServerSocketChannel serverChannel;

    public SHTTPNB() {
        try {
            selector = Selector.open();
            serverChannel = ServerSocketChannel.open();
            serverChannel.bind(new InetSocketAddress(PUERTO));
            serverChannel.configureBlocking(false);
            serverChannel.register(selector, SelectionKey.OP_ACCEPT);
            System.out.println("Servidor iniciado:---OK");
            System.out.println("Esperando Cliente...");

            while (true) {
                selector.select();
                Set<SelectionKey> keys = selector.selectedKeys();
                Iterator<SelectionKey> iterator = keys.iterator();

                while (iterator.hasNext()) {
                    SelectionKey key = iterator.next();
                    iterator.remove();

                    if (key.isAcceptable()) {
                        acceptConnection();
                    } else if (key.isReadable()) {
                        handleRequest(key);
                    }
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void acceptConnection() throws IOException {
        SocketChannel client = serverChannel.accept();
        client.configureBlocking(false);
        client.register(selector, SelectionKey.OP_READ);
        System.out.println("Cliente Conectado desde: " + client.getRemoteAddress());
    }

    private void handleRequest(SelectionKey key) {
        SocketChannel client = (SocketChannel) key.channel();
        ByteBuffer buffer = ByteBuffer.allocate(1024);
        Charset charset = Charset.forName("UTF-8");
        CharsetDecoder decoder = charset.newDecoder();
        CharsetEncoder encoder = charset.newEncoder();

        try {
            client.read(buffer);
            buffer.flip();
            String peticion = decoder.decode(buffer).toString();
            buffer.clear();

            if (peticion == null) {
                sendResponse(client, "<html><head><title>Servidor WEB</title></head><body bgcolor=\"#AACCFF\"><br>Linea Vacia</br></body></html>", "text/html", 400);
                client.close();
                return;
            }

            System.out.println("Cliente Conectado desde: " + client.getRemoteAddress());
            System.out.println("Por el puerto: " + client.socket().getPort());
            System.out.println("Petición:\n" + peticion);

            StringTokenizer st1 = new StringTokenizer(peticion, "\n");
            String line = st1.nextToken();
            System.out.println("\nMETODO: " + line);

            if (line.toUpperCase().startsWith("GET")) {
                handleGetRequest(client, line);
            } else if (line.toUpperCase().startsWith("POST")) {
                handlePostRequest(client, peticion);
            } else if (line.toUpperCase().startsWith("DELETE")) {
                handleDeleteRequest(client, line);
            } else if (line.toUpperCase().startsWith("PUT")) {
                handlePutRequest(client, line, peticion);
            } else if (line.toUpperCase().startsWith("HEAD")) {
                handleHeadRequest(client, line);
            } else {
                sendResponse(client, "501 Not Implemented", "text/plain", 501);
                client.close();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void handleGetRequest(SocketChannel client, String line) throws IOException {
        String fileName = getFileName(line);
        if (fileName.isEmpty()) {
            fileName = "index.htm";
        }

        String parametros = extractGetParameters(line);
        if (parametros.isEmpty()) {
            sendFile(client, fileName, "text/html");
        } else {
            String response = "<html><head><title>SERVIDOR WEB</title></head>"
                    + "<body bgcolor=\"#90ee90\"><center><h1>Parametros Obtenidos mediante el Metodo GET</h1><h3><b>"
                    + parametros + "</b></h3></center></body></html>";
            sendResponse(client, response, "text/html", 200);
        }
    }

    private void handlePostRequest(SocketChannel client, String peticion) throws IOException {
        String parametros = extractPostParameters(peticion);
        String response = "<html><head><title>SERVIDOR WEB</title></head>"
                + "<body bgcolor=\"#90ee90\"><center><h1>Parametros Obtenidos mediante el Metodo POST</h1><h3><b>"
                + parametros + "</b></h3></center></body></html>";
        sendResponse(client, response, "text/html", 201);
    }

    private void handleDeleteRequest(SocketChannel client, String line) throws IOException {
        String fileName = getFileName(line);
        File file = new File(fileName);
        String response;
        String title;
        int statusCode;

        if (file.getName().equals("index2.htm")) {
            title = "ERROR 403";
            response = "El fichero " + file.getName() + " está protegido y el servidor deniega la acción solicitada.";
            statusCode = 403;
        } else if (file.delete()) {
            title = "Archivo eliminado";
            response = "El fichero " + file.getName() + " ha sido eliminado satisfactoriamente.";
            statusCode = 202;
        } else {
            title = "ERROR 404";
            response = "El fichero " + file.getName() + " no pudo ser eliminado, es probable que no exista en el servidor.";
            statusCode = 404;
        }

        String jsonResponse = "{\"title\":\"" + title + "\",\"message\":\"" + response + "\"}";
        sendResponse(client, jsonResponse, "application/json", statusCode);
    }

    private void handlePutRequest(SocketChannel client, String line, String peticion) throws IOException {
        String fileName = getFileName(line);
        Path filePath = Paths.get(fileName);
        String contenido = extractPutContent(peticion);
        boolean fileExists = Files.exists(filePath);
        Files.write(filePath, contenido.getBytes());

        String response;
        if (fileExists) {
            response = "<response><title>SERVIDOR WEB - Actualización</title>"
                    + "<message>El fichero " + fileName + " fue modificado exitosamente</message></response>";
        } else {
            response = "<response><title>SERVIDOR WEB - Creación</title>"
                    + "<message>El fichero " + fileName + " fue creado exitosamente</message></response>";
        }

        sendResponse(client, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + response, "application/xml", 202);
    }

    private void handleHeadRequest(SocketChannel client, String line) throws IOException {
        String fileName = getFileName(line);
        Path filePath = Paths.get(fileName);
        if (Files.exists(filePath)) {
            String mimeType = Files.probeContentType(filePath);
            long contentLength = Files.size(filePath);
            sendHeaders(client, mimeType, contentLength, 200);
        } else {
            sendHeaders(client, "text/plain", 0, 404);
        }
    }

    private String getFileName(String line) {
        int start = line.indexOf("/") + 1;
        int end = line.indexOf(" ", start);
        return line.substring(start, end);
    }

    private String extractPostParameters(String peticion) {
        StringTokenizer stokens = new StringTokenizer(peticion, "\n");
        String line = stokens.nextToken();
        while (!line.startsWith("Nombre") && stokens.hasMoreElements()) {
            line = stokens.nextToken();
        }
        return line;
    }

    private String extractGetParameters(String line) {
        int start = line.indexOf("?");
        if (start == -1) {
            return "";
        }
        int end = line.indexOf(" ", start);
        String queryString = line.substring(start + 1, end);
        return queryString.replace("&", "<br>");
    }

    private String extractPutContent(String peticion) {
        int index = peticion.indexOf("\r\n\r\n");
        return peticion.substring(index + 4);
    }

    private void sendFile(SocketChannel client, String fileName, String contentType) throws IOException {
        Path filePath = Paths.get(fileName);
        if (Files.exists(filePath)) {
            ByteBuffer buffer = ByteBuffer.allocate(4096);
            FileChannel fileChannel = FileChannel.open(filePath, StandardOpenOption.READ);
            sendHeaders(client, contentType, Files.size(filePath), 200);
            int bytesRead;
            while ((bytesRead = fileChannel.read(buffer)) > 0) {
                buffer.flip();
                client.write(buffer);
                buffer.clear();
            }
            fileChannel.close();
        } else {
            sendResponse(client, "404 Not Found", "text/plain", 404);
        }
        client.close();
    }

    private void sendHeaders(SocketChannel client, String contentType, long contentLength, int statusCode) throws IOException {
        String response = "HTTP/1.0 " + statusCode + " OK\r\n"
                + "Date: " + new Date() + "\r\n"
                + "Server: MiServidor/1.0\r\n"
                + "Content-Type: " + contentType + "\r\n"
                + "Content-Length: " + contentLength + "\r\n"
                + "Connection: close\r\n\r\n";
        client.write(ByteBuffer.wrap(response.getBytes(StandardCharsets.UTF_8)));
    }

    private void sendResponse(SocketChannel client, String content, String contentType, int statusCode) throws IOException {
        byte[] contentBytes = content.getBytes(StandardCharsets.UTF_8);
        sendHeaders(client, contentType, contentBytes.length, statusCode);
        client.write(ByteBuffer.wrap(contentBytes));
    }

    public static void main(String[] args) {
        new SHTTPNB();
    }
}
